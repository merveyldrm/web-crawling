#!/usr/bin/env python3
"""
🚀 FAISS + Sentence Transformers RAG Sistemi
Gelişmiş vector search ile semantic similarity
"""

import os
import json
import pickle
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3

# FAISS ve embedding imports
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Mevcut analiz modülleri
try:
    from advanced_comment_analyzer import AdvancedCommentAnalyzer
    from priority_analyzer import PriorityAnalyzer
    ANALYZERS_AVAILABLE = True
except ImportError:
    ANALYZERS_AVAILABLE = False

class FaissRAGSystem:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        db_path: str = "faiss_rag.db",
        vector_path: str = "./faiss_vectors"
    ):
        """
        FAISS tabanlı RAG sistemi
        
        Args:
            model_name: Sentence transformer model
            db_path: SQLite veritabanı yolu
            vector_path: FAISS indeks dosyalarının yolu
        """
        self.model_name = model_name
        self.db_path = db_path
        self.vector_path = vector_path
        
        # Embedding modeli
        print("📥 Embedding modeli yükleniyor...")
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"✅ Model yüklendi: {model_name} (dim: {self.embedding_dim})")
        
        # FAISS indeks
        self.comment_index = None
        self.knowledge_index = None
        self.comment_metadata = []
        self.knowledge_metadata = []
        
        # Vector path oluştur
        os.makedirs(vector_path, exist_ok=True)
        
        # SQLite database
        self.init_database()
        
        # Analiz modülleri
        if ANALYZERS_AVAILABLE:
            self.comment_analyzer = AdvancedCommentAnalyzer()
            self.priority_analyzer = PriorityAnalyzer()
            print("✅ Gelişmiş analiz modülleri aktif")
        else:
            print("⚠️ Temel mod - gelişmiş analiz modülleri yok")
        
        # Mevcut indeksleri yükle
        self.load_indexes()
        
        print("🚀 FAISS RAG sistemi hazır!")
    
    def init_database(self):
        """SQLite veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Yorumlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                user TEXT,
                date TEXT,
                comment TEXT,
                comment_hash TEXT UNIQUE,
                category TEXT DEFAULT 'unknown',
                priority_score REAL DEFAULT 0,
                embedding_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bilgi tabanı
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY,
                category TEXT,
                problem TEXT,
                solution TEXT,
                keywords TEXT,
                embedding_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vector indeks metadatası
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_metadata (
                id INTEGER PRIMARY KEY,
                vector_type TEXT,  -- 'comment' or 'knowledge'
                record_id INTEGER,
                embedding_vector BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📁 SQLite veritabanı hazır")
    
    def get_comment_hash(self, comment: str, user: str = "", date: str = "") -> str:
        """Yorum için unique hash"""
        text = f"{comment}{user}{date}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Metinler için embedding oluştur"""
        print(f"🔄 {len(texts)} metin için embedding oluşturuluyor...")
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.astype('float32')
    
    def load_comments_from_csv(self, csv_file: str = "trendyol_comments.csv") -> int:
        """CSV'den yorumları yükle ve vector store'a ekle"""
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} bulunamadı!")
            return 0
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f"📊 {len(df)} yorum bulundu")
        except Exception as e:
            print(f"❌ CSV okuma hatası: {e}")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Yeni yorumları hazırla
        new_comments = []
        comment_texts = []
        
        for _, row in df.iterrows():
            comment = str(row.get('comment', ''))
            user = str(row.get('user', ''))
            date = str(row.get('date', ''))
            
            if not comment.strip():
                continue
            
            comment_hash = self.get_comment_hash(comment, user, date)
            
            # Zaten var mı kontrol et
            cursor.execute('SELECT id FROM comments WHERE comment_hash = ?', (comment_hash,))
            if cursor.fetchone():
                continue
            
            # Analiz yap
            category = 'unknown'
            priority_score = 0
            
            if ANALYZERS_AVAILABLE:
                try:
                    analysis = self.comment_analyzer.analyze_comment_categories(comment)
                    # En yüksek confidence'lı kategoriyi bul
                    highest_category = 'unknown'
                    highest_confidence = 0
                    for cat, result in analysis.items():
                        if result.get('relevant') and result.get('confidence', 0) > highest_confidence:
                            highest_category = cat
                            highest_confidence = result['confidence']
                    
                    category = highest_category
                    priority_score = self.priority_analyzer.calculate_negativity_score(comment).get('negativity_score', 0)
                except Exception as e:
                    print(f"⚠️ Analiz hatası: {e}")
            
            new_comments.append((user, date, comment, comment_hash, category, priority_score))
            comment_texts.append(comment)
        
        if not new_comments:
            print("📝 Tüm yorumlar zaten mevcut")
            conn.close()
            return 0
        
        # Embeddings oluştur
        embeddings = self.create_embeddings(comment_texts)
        
        # FAISS indekse ekle
        if self.comment_index is None:
            self.comment_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product (cosine similarity)
        
        start_id = len(self.comment_metadata)
        self.comment_index.add(embeddings)
        
        # Veritabanına kaydet
        for i, (user, date, comment, comment_hash, category, priority_score) in enumerate(new_comments):
            embedding_id = start_id + i
            
            # Comment tablosuna ekle
            cursor.execute('''
                INSERT INTO comments 
                (user, date, comment, comment_hash, category, priority_score, embedding_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user, date, comment, comment_hash, category, priority_score, embedding_id))
            
            comment_id = cursor.lastrowid
            
            # Metadata ekle
            self.comment_metadata.append({
                'id': comment_id,
                'user': user,
                'date': date,
                'comment': comment,
                'category': category,
                'priority_score': priority_score,
                'embedding_id': embedding_id
            })
            
            # Vector metadata kaydet
            embedding_blob = embeddings[i].tobytes()
            cursor.execute('''
                INSERT INTO vector_metadata (vector_type, record_id, embedding_vector)
                VALUES (?, ?, ?)
            ''', ('comment', comment_id, embedding_blob))
        
        conn.commit()
        conn.close()
        
        # İndeksi kaydet
        self.save_indexes()
        
        print(f"✅ {len(new_comments)} yeni yorum eklendi")
        return len(new_comments)
    
    def add_knowledge(self, category: str, problem: str, solution: str, keywords: List[str] = None):
        """Bilgi tabanına entry ekle"""
        if keywords is None:
            keywords = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bilgi kaydı
        cursor.execute('''
            INSERT INTO knowledge_base (category, problem, solution, keywords)
            VALUES (?, ?, ?, ?)
        ''', (category, problem, solution, ','.join(keywords)))
        
        knowledge_id = cursor.lastrowid
        
        # Embedding oluştur (problem + solution birleşimi)
        text = f"{problem} {solution}"
        embedding = self.create_embeddings([text])[0]
        
        # FAISS indekse ekle
        if self.knowledge_index is None:
            self.knowledge_index = faiss.IndexFlatIP(self.embedding_dim)
        
        embedding_id = len(self.knowledge_metadata)
        self.knowledge_index.add(embedding.reshape(1, -1))
        
        # Metadata güncelle
        cursor.execute('UPDATE knowledge_base SET embedding_id = ? WHERE id = ?', 
                      (embedding_id, knowledge_id))
        
        self.knowledge_metadata.append({
            'id': knowledge_id,
            'category': category,
            'problem': problem,
            'solution': solution,
            'keywords': keywords,
            'embedding_id': embedding_id
        })
        
        # Vector metadata kaydet
        embedding_blob = embedding.tobytes()
        cursor.execute('''
            INSERT INTO vector_metadata (vector_type, record_id, embedding_vector)
            VALUES (?, ?, ?)
        ''', ('knowledge', knowledge_id, embedding_blob))
        
        conn.commit()
        conn.close()
        
        # İndeksi kaydet
        self.save_indexes()
        
        print(f"📚 Bilgi eklendi: {category} - {problem[:50]}...")
    
    def search_similar_comments(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.3,
        sentiment_filter: str = None  # 'positive', 'negative', 'neutral' veya None
    ) -> List[Dict]:
        """FAISS ile benzer yorumları ara"""
        
        if self.comment_index is None or len(self.comment_metadata) == 0:
            return []
        
        # Query embedding
        query_embedding = self.create_embeddings([query])[0]
        
        # Embedding boyutunu kontrol et
        if query_embedding.shape[0] != self.embedding_dim:
            print(f"⚠️ Embedding boyut uyumsuzluğu: {query_embedding.shape[0]} != {self.embedding_dim}")
            return []
        
        # FAISS arama (daha fazla sonuç al filtering için)
        search_limit = min(limit * 4, len(self.comment_metadata))
        try:
            scores, indices = self.comment_index.search(
                query_embedding.reshape(1, -1), 
                search_limit
            )
        except Exception as e:
            print(f"⚠️ FAISS arama hatası: {e}")
            print("🔄 İndeksleri yeniden oluşturuyor...")
            self.reset_vectors()
            return []
        
        results = []
        negative_keywords = ['sorun', 'problem', 'kötü', 'berbat', 'bozuk', 'defolu', 'şikayet', 'memnun değil', 
                           'kalitesiz', 'geç', 'yavaş', 'hasarlı', 'kırık', 'iade', 'beğenmedim', 'beğenmedik',
                           'tavsiye etmem', 'pişman', 'hayal kırıklığı', 'rezalet', 'çöp', 'para israfı', 
                           'aldatmaca', 'sahte', 'taklit']
        
        positive_keywords = ['beğendik', 'beğendim', 'mükemmel', 'harika', 'süper', 'tavsiye ederim', 
                           'memnun', 'kaliteli', 'güzel', 'başarılı', 'teşekkür', 'stok', 'vazgeçilmez',
                           'favorim', 'severek', 'mutlu', 'çok iyi']
        
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < similarity_threshold:
                continue
                
            if idx < len(self.comment_metadata):
                metadata = self.comment_metadata[idx]
                comment_text = metadata['comment'].lower()
                
                # Sentiment filtering - hem pozitif hem negatif kelimeleri kontrol et
                has_negative = any(keyword in comment_text for keyword in negative_keywords)
                has_positive = any(keyword in comment_text for keyword in positive_keywords)
                
                if sentiment_filter == 'negative':
                    # Sadece negatif kelimeler varsa VE pozitif kelimeler yoksa
                    if not has_negative or has_positive:
                        continue
                elif sentiment_filter == 'positive':
                    # Sadece pozitif kelimeler varsa VE negatif kelimeler yoksa
                    if not has_positive or has_negative:
                        continue
                
                results.append({
                    'id': metadata['id'],
                    'user': metadata['user'],
                    'date': metadata['date'],
                    'comment': metadata['comment'],
                    'category': metadata['category'],
                    'priority_score': metadata['priority_score'],
                    'similarity': float(score)
                })
        
        # Similarity'ye göre sırala ve limit uygula
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def search_knowledge_base(
        self,
        query: str,
        limit: int = 3,
        similarity_threshold: float = 0.3
    ) -> List[Dict]:
        """FAISS ile bilgi tabanında ara"""
        
        if self.knowledge_index is None or len(self.knowledge_metadata) == 0:
            return []
        
        # Query embedding
        query_embedding = self.create_embeddings([query])[0]
        
        # FAISS arama
        scores, indices = self.knowledge_index.search(
            query_embedding.reshape(1, -1),
            min(limit * 2, len(self.knowledge_metadata))
        )
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < similarity_threshold:
                continue
                
            if idx < len(self.knowledge_metadata):
                metadata = self.knowledge_metadata[idx]
                results.append({
                    'id': metadata['id'],
                    'category': metadata['category'],
                    'problem': metadata['problem'],
                    'solution': metadata['solution'],
                    'keywords': metadata['keywords'],
                    'similarity': float(score)
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def query(self, question: str) -> Dict[str, Any]:
        """Gelişmiş RAG sorgusu"""
        print(f"🔍 Soru: {question}")
        
        # Sorunun negatif/pozitif eğilimini tespit et
        question_lower = question.lower()
        problem_keywords = ['sorun', 'problem', 'şikayet', 'kötü', 'berbat', 'nasıl çözülebilir', 'iyileştir']
        is_problem_query = any(keyword in question_lower for keyword in problem_keywords)
        
        # 1. Benzer yorumları bul (sorun arayışındaysa negatif filtrele)
        if is_problem_query:
            similar_comments = self.search_similar_comments(question, limit=3, sentiment_filter='negative')
            if not similar_comments:
                # Negatif bulamazsa genel arama yap
                similar_comments = self.search_similar_comments(question, limit=3)
        else:
            similar_comments = self.search_similar_comments(question, limit=3)
        
        # 2. Bilgi tabanını ara
        knowledge_results = self.search_knowledge_base(question, limit=2)
        
        # 3. Gelişmiş yanıt oluştur
        answer_parts = []
        
        if similar_comments:
            answer_parts.append("**🔍 Benzer Yorumlardan Bulgular:**")
            for i, comment in enumerate(similar_comments, 1):
                priority = comment['priority_score']
                category = comment['category']
                similarity = comment['similarity']
                
                # Sentiment tespiti
                comment_text = comment['comment'].lower()
                negative_keywords = ['sorun', 'problem', 'kötü', 'berbat', 'bozuk', 'defolu', 'şikayet', 'memnun değil', 
                                   'kalitesiz', 'geç', 'yavaş', 'hasarlı', 'kırık', 'iade', 'beğenmedim', 'beğenmedik',
                                   'tavsiye etmem', 'pişman', 'hayal kırıklığı', 'rezalet', 'çöp', 'para israfı']
                positive_keywords = ['beğendik', 'beğendim', 'mükemmel', 'harika', 'süper', 'tavsiye ederim', 
                                   'memnun', 'kaliteli', 'güzel', 'başarılı', 'teşekkür', 'stok', 'vazgeçilmez',
                                   'favorim', 'severek', 'mutlu', 'çok iyi']
                
                has_negative = any(kw in comment_text for kw in negative_keywords)
                has_positive = any(kw in comment_text for kw in positive_keywords)
                
                if has_negative and not has_positive:
                    sentiment_emoji = "🔴"
                elif has_positive and not has_negative:
                    sentiment_emoji = "🟢"
                else:
                    sentiment_emoji = "⚪"
                
                answer_parts.append(
                    f"{i}. {sentiment_emoji} {comment['comment'][:120]}... "
                    f"(Benzerlik: {similarity:.2f}, Öncelik: {priority:.0f}/100, "
                    f"Kategori: {category})"
                )
        else:
            if is_problem_query:
                answer_parts.append("**🔍 Benzer Yorumlardan Bulgular:**")
                answer_parts.append("Bu konuda olumsuz bir yorum tespit edilmedi. Bu olumlu bir durumdur! ✅")
        
        if knowledge_results:
            answer_parts.append("\n**💡 Bilgi Tabanından Çözüm Önerileri:**")
            for i, kb in enumerate(knowledge_results, 1):
                similarity = kb['similarity']
                answer_parts.append(
                    f"{i}. **{kb['category'].title()}** (Benzerlik: {similarity:.2f})\n"
                    f"   Problem: {kb['problem']}\n"
                    f"   Çözüm: {kb['solution']}"
                )
        
        if not answer_parts:
            answer_parts.append("Bu soru için ilgili bilgi bulunamadı. Daha spesifik terimler deneyebilirsiniz.")
        
        answer = "\n".join(answer_parts)
        
        return {
            "question": question,
            "answer": answer,
            "similar_comments": similar_comments,
            "knowledge_results": knowledge_results,
            "embedding_model": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "query_type": "problem_focused" if is_problem_query else "general"
        }
    
    def save_indexes(self):
        """FAISS indekslerini kaydet"""
        try:
            if self.comment_index is not None:
                faiss.write_index(self.comment_index, f"{self.vector_path}/comment_index.faiss")
                
                with open(f"{self.vector_path}/comment_metadata.pkl", 'wb') as f:
                    pickle.dump(self.comment_metadata, f)
            
            if self.knowledge_index is not None:
                faiss.write_index(self.knowledge_index, f"{self.vector_path}/knowledge_index.faiss")
                
                with open(f"{self.vector_path}/knowledge_metadata.pkl", 'wb') as f:
                    pickle.dump(self.knowledge_metadata, f)
            
            print("💾 FAISS indeksleri kaydedildi")
        except Exception as e:
            print(f"⚠️ İndeks kaydetme hatası: {e}")
    
    def load_indexes(self):
        """FAISS indekslerini yükle"""
        try:
            # Comment indeks
            comment_index_path = f"{self.vector_path}/comment_index.faiss"
            comment_metadata_path = f"{self.vector_path}/comment_metadata.pkl"
            
            if os.path.exists(comment_index_path) and os.path.exists(comment_metadata_path):
                self.comment_index = faiss.read_index(comment_index_path)
                with open(comment_metadata_path, 'rb') as f:
                    self.comment_metadata = pickle.load(f)
                print(f"📥 Comment indeks yüklendi: {len(self.comment_metadata)} yorum")
            
            # Knowledge indeks
            knowledge_index_path = f"{self.vector_path}/knowledge_index.faiss"
            knowledge_metadata_path = f"{self.vector_path}/knowledge_metadata.pkl"
            
            if os.path.exists(knowledge_index_path) and os.path.exists(knowledge_metadata_path):
                self.knowledge_index = faiss.read_index(knowledge_index_path)
                with open(knowledge_metadata_path, 'rb') as f:
                    self.knowledge_metadata = pickle.load(f)
                print(f"📥 Knowledge indeks yüklendi: {len(self.knowledge_metadata)} bilgi")
        
        except Exception as e:
            print(f"⚠️ İndeks yükleme hatası: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Sistem istatistikleri"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM comments')
        total_comments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_base')
        total_knowledge = cursor.fetchone()[0]
        
        cursor.execute('SELECT category, COUNT(*) FROM comments GROUP BY category')
        category_dist = dict(cursor.fetchall())
        
        cursor.execute('SELECT AVG(priority_score) FROM comments WHERE priority_score > 0')
        avg_priority = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_comments": total_comments,
            "total_knowledge_entries": total_knowledge,
            "category_distribution": category_dist,
            "average_priority": round(avg_priority, 2),
            "vector_comments": len(self.comment_metadata),
            "vector_knowledge": len(self.knowledge_metadata),
            "embedding_model": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "has_advanced_analyzers": ANALYZERS_AVAILABLE
        }
    
    def reset_vectors(self):
        """Vector store'u sıfırla"""
        try:
            # FAISS indekslerini sıfırla
            self.comment_index = None
            self.knowledge_index = None
            self.comment_metadata = []
            self.knowledge_metadata = []
            
            # Dosyaları sil
            for filename in os.listdir(self.vector_path):
                if filename.endswith(('.faiss', '.pkl')):
                    os.remove(os.path.join(self.vector_path, filename))
            
            # Veritabanını sıfırla
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM comments')
            cursor.execute('DELETE FROM knowledge_base')
            cursor.execute('DELETE FROM vector_metadata')
            conn.commit()
            conn.close()
            
            print("🗑️ Vector store sıfırlandı")
        except Exception as e:
            print(f"⚠️ Sıfırlama hatası: {e}")


def setup_demo_knowledge(rag):
    """Demo bilgi tabanını kur"""
    print("🌐 Demo bilgi tabanı kuruluyor...")
    
    knowledge_entries = [
        {
            "category": "kargo",
            "problem": "Kargo gecikmesi, teslimat sorunları ve paket hasarı",
            "solution": "1) Kargo firması çeşitliliği artırın, 2) Express teslimat seçeneği ekleyin, 3) Paket takip sistemi geliştirin, 4) Hasar garantisi verin",
            "keywords": ["kargo", "teslimat", "gecikme", "geç", "hasar", "kırık"]
        },
        {
            "category": "kalite",
            "problem": "Ürün kalitesi, dayanıklılık ve bozuk ürün şikayetleri",
            "solution": "1) Kalite kontrol süreçlerini güçlendirin, 2) Tedarikçi denetimi yapın, 3) Malzeme standartlarını yükseltin, 4) Test prosedürleri uygulayın",
            "keywords": ["kalite", "bozuk", "defolu", "kötü", "dayanıksız", "sahte"]
        },
        {
            "category": "beden",
            "problem": "Beden uyumsuzluğu, kalıp sorunları ve ölçü farklılıkları",
            "solution": "1) Beden tablosunu standart hale getirin, 2) AR deneme özelliği ekleyin, 3) Kullanıcı yorumlarından beden önerileri sunun, 4) Esnek iade politikası",
            "keywords": ["beden", "uyum", "kalıp", "büyük", "küçük", "dar", "bol"]
        },
        {
            "category": "musteri_hizmetleri",
            "problem": "Müşteri hizmetleri yanıt süresi, çözüm kalitesi ve iletişim sorunları",
            "solution": "1) 7/24 canlı destek kurun, 2) Yanıt süresini 2 saate düşürün, 3) Çok dilli destek ekleyin, 4) Self-servis çözüm merkezi oluşturun",
            "keywords": ["müşteri", "hizmet", "destek", "yanıt", "çözüm", "ilgisiz"]
        },
        {
            "category": "fiyat",
            "problem": "Fiyat algısı, değer karşılığı ve rekabet sorunları",
            "solution": "1) Dinamik fiyatlandırma sistemi kurun, 2) Sadakat programları başlatın, 3) Değer paketi oluşturun, 4) Fiyat karşılaştırma aracı ekleyin",
            "keywords": ["fiyat", "pahalı", "değer", "ucuz", "indirim", "kampanya"]
        },
        {
            "category": "website",
            "problem": "Website performansı, kullanıcı deneyimi ve teknik sorunlar",
            "solution": "1) Sayfa yükleme hızını artırın, 2) Mobil optimizasyonu geliştirin, 3) Arama fonksiyonunu iyileştirin, 4) Checkout sürecini basitleştirin",
            "keywords": ["site", "yavaş", "hata", "bulunamadı", "mobil", "arama"]
        }
    ]
    
    for entry in knowledge_entries:
        rag.add_knowledge(
            entry["category"],
            entry["problem"],
            entry["solution"],
            entry["keywords"]
        )
    
    print("✅ Demo bilgi tabanı kuruldu")


def main():
    """Demo kullanımı"""
    print("🚀 FAISS RAG SİSTEMİ DEMO")
    print("=" * 60)
    
    # RAG sistemi oluştur
    rag = FaissRAGSystem()
    
    # CSV'den yorumları yükle
    doc_count = rag.load_comments_from_csv("trendyol_comments.csv")
    if doc_count > 0:
        print(f"✅ {doc_count} yeni yorum yüklendi")
    
    # Demo bilgi tabanını kur
    setup_demo_knowledge(rag)
    
    # Sistem istatistikleri
    stats = rag.get_stats()
    print(f"\n📊 SİSTEM İSTATİSTİKLERİ:")
    print(f"   📝 Toplam Yorum: {stats['total_comments']}")
    print(f"   📚 Bilgi Tabanı: {stats['total_knowledge_entries']}")
    print(f"   🔢 Vector Yorum: {stats['vector_comments']}")
    print(f"   🧠 Embedding Model: {stats['embedding_model']}")
    print(f"   📏 Embedding Boyut: {stats['embedding_dimension']}")
    
    # Demo sorguları
    demo_questions = [
        "Kargo sorunları hakkında şikayetler var mı?",
        "Ürün kalitesi ile ilgili en büyük problem nedir?",
        "Beden uyumsuzluğu nasıl çözülebilir?",
        "Müşteri hizmetleri nasıl geliştirilebilir?",
        "Website performansı hakkında ne düşünülüyor?"
    ]
    
    print(f"\n💬 DEMO SORGULARI:")
    print("=" * 60)
    
    for question in demo_questions:
        print(f"\n❓ SORU: {question}")
        print("-" * 50)
        
        result = rag.query(question)
        print(f"🤖 YANIT:\n{result['answer']}")
        print(f"📊 Benzer yorum: {len(result['similar_comments'])}")
        print(f"📚 Bilgi sonucu: {len(result['knowledge_results'])}")
    
    print(f"\n✅ DEMO TAMAMLANDI!")
    print("💡 Web arayüzü için: streamlit run faiss_rag_streamlit.py")


if __name__ == "__main__":
    main() 