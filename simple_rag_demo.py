#!/usr/bin/env python3
"""
🚀 Basit RAG Demo - Python 3.13 Uyumlu
Trendyol yorumları için minimal RAG sistemi
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import sqlite3
import hashlib

# Mevcut sistem import'ları
try:
    from src.analyzers.advanced_comment_analyzer import AdvancedCommentAnalyzer
    from src.analyzers.priority_analyzer import PriorityAnalyzer
    print("✅ Mevcut analiz modülleri yüklendi")
except ImportError as e:
    print(f"⚠️ Analiz modülleri yüklenemedi: {e}")
    print("💡 Temel versiyonla devam edilecek")

class SimpleRAGSystem:
    def __init__(self, db_path: str = "simple_rag.db"):
        """Basit RAG sistemi - TF-IDF tabanlı"""
        self.db_path = db_path
        self.init_database()
        
        # Analiz modülleri
        try:
            self.comment_analyzer = AdvancedCommentAnalyzer()
            self.priority_analyzer = PriorityAnalyzer()
            self.has_analyzers = True
        except:
            self.has_analyzers = False
            print("⚠️ Analiz modülleri olmadan çalışılacak")
        
        # Basit TF-IDF için stop words
        self.stop_words = {
            'bir', 'bu', 'da', 'de', 'ile', 'için', 'çok', 'var', 'yok', 'olan',
            've', 'ama', 'fakat', 'ancak', 'şey', 'şu', 'o', 'ben', 'sen', 'biz',
            'siz', 'onlar', 'hiç', 'her', 'ne', 'nasıl', 'neden', 'kim', 'hangi'
        }
        
        print("✅ Basit RAG sistemi hazır")
    
    def init_database(self):
        """SQLite veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                user TEXT,
                date TEXT,
                comment TEXT,
                comment_hash TEXT UNIQUE,
                category TEXT DEFAULT 'unknown',
                priority_score REAL DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY,
                category TEXT,
                problem TEXT,
                solution TEXT,
                keywords TEXT,
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
    
    def load_comments_from_csv(self, csv_file: str = "trendyol_comments.csv") -> int:
        """CSV'den yorumları yükle"""
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
        
        loaded_count = 0
        
        for _, row in df.iterrows():
            comment = str(row.get('comment', ''))
            user = str(row.get('user', ''))
            date = str(row.get('date', ''))
            
            if not comment.strip():
                continue
            
            comment_hash = self.get_comment_hash(comment, user, date)
            
            # Analiz yap (eğer modüller varsa)
            category = 'unknown'
            priority_score = 0
            
            if self.has_analyzers:
                try:
                    analysis = self.comment_analyzer.analyze_comment(comment)
                    priority = self.priority_analyzer.analyze_comment_priority(comment)
                    
                    category = analysis.get('category_analysis', {}).get('highest_category', 'unknown')
                    priority_score = priority.get('priority_score', 0)
                except:
                    pass
            
            # Veritabanına ekle
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO comments 
                    (user, date, comment, comment_hash, category, priority_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user, date, comment, comment_hash, category, priority_score))
                
                if cursor.rowcount > 0:
                    loaded_count += 1
            except Exception as e:
                print(f"⚠️ Yorum ekleme hatası: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ {loaded_count} yorum veritabanına eklendi")
        return loaded_count
    
    def add_knowledge(self, category: str, problem: str, solution: str, keywords: List[str] = None):
        """Bilgi tabanına entry ekle"""
        if keywords is None:
            keywords = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_base (category, problem, solution, keywords)
            VALUES (?, ?, ?, ?)
        ''', (category, problem, solution, ','.join(keywords)))
        
        conn.commit()
        conn.close()
        
        print(f"📚 Bilgi eklendi: {category} - {problem[:50]}...")
    
    def simple_text_similarity(self, text1: str, text2: str) -> float:
        """Basit TF-IDF benzerlik hesaplama"""
        def tokenize(text: str) -> set:
            words = text.lower().split()
            return {word for word in words if word not in self.stop_words and len(word) > 2}
        
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def search_similar_comments(self, query: str, limit: int = 5) -> List[Dict]:
        """Benzer yorumları ara"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM comments')
        all_comments = cursor.fetchall()
        
        similarities = []
        
        for comment_row in all_comments:
            comment_id, user, date, comment, comment_hash, category, priority_score, processed_at = comment_row
            
            similarity = self.simple_text_similarity(query, comment)
            
            if similarity > 0.1:  # Minimum benzerlik eşiği
                similarities.append({
                    'id': comment_id,
                    'user': user,
                    'date': date,
                    'comment': comment,
                    'category': category,
                    'priority_score': priority_score,
                    'similarity': similarity
                })
        
        # Benzerlik skoruna göre sırala
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        conn.close()
        return similarities[:limit]
    
    def search_knowledge_base(self, query: str, limit: int = 3) -> List[Dict]:
        """Bilgi tabanında ara"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge_base')
        all_knowledge = cursor.fetchall()
        
        results = []
        
        for knowledge_row in all_knowledge:
            kb_id, category, problem, solution, keywords, created_at = knowledge_row
            
            # Problem ve solution'da ara
            problem_sim = self.simple_text_similarity(query, problem)
            solution_sim = self.simple_text_similarity(query, solution)
            keyword_sim = self.simple_text_similarity(query, keywords)
            
            max_sim = max(problem_sim, solution_sim, keyword_sim)
            
            if max_sim > 0.1:
                results.append({
                    'id': kb_id,
                    'category': category,
                    'problem': problem,
                    'solution': solution,
                    'keywords': keywords.split(',') if keywords else [],
                    'similarity': max_sim
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        conn.close()
        return results[:limit]
    
    def query(self, question: str) -> Dict[str, Any]:
        """RAG sorgusu"""
        print(f"🔍 Soru: {question}")
        
        # 1. Benzer yorumları bul
        similar_comments = self.search_similar_comments(question, limit=3)
        
        # 2. Bilgi tabanını ara
        knowledge_results = self.search_knowledge_base(question, limit=2)
        
        # 3. Basit yanıt oluştur
        answer_parts = []
        
        if similar_comments:
            answer_parts.append("**Benzer Yorumlardan Bulgular:**")
            for i, comment in enumerate(similar_comments, 1):
                priority = comment['priority_score']
                category = comment['category']
                answer_parts.append(f"{i}. {comment['comment'][:100]}... (Öncelik: {priority:.0f}/100, Kategori: {category})")
        
        if knowledge_results:
            answer_parts.append("\n**Bilgi Tabanından Öneriler:**")
            for i, kb in enumerate(knowledge_results, 1):
                answer_parts.append(f"{i}. **{kb['category']}**: {kb['solution']}")
        
        if not answer_parts:
            answer_parts.append("Bu soru için ilgili bilgi bulunamadı.")
        
        answer = "\n".join(answer_parts)
        
        return {
            "question": question,
            "answer": answer,
            "similar_comments": similar_comments,
            "knowledge_results": knowledge_results,
            "timestamp": datetime.now().isoformat()
        }
    
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
            "has_advanced_analyzers": self.has_analyzers
        }


def setup_demo_knowledge(rag):
    """Demo bilgi tabanını kur"""
    print("🌐 Demo bilgi tabanı kuruluyor...")
    
    knowledge_entries = [
        {
            "category": "kargo",
            "problem": "Kargo gecikmesi ve teslimat sorunları",
            "solution": "1) Alternatif kargo firmaları ile anlaşma yapın, 2) Express teslimat seçeneği sunun, 3) SMS/Email takip sistemi kurun",
            "keywords": ["kargo", "teslimat", "gecikme", "geç"]
        },
        {
            "category": "kalite",
            "problem": "Ürün kalitesi ve bozuk ürün şikayetleri",
            "solution": "1) Kalite kontrol süreçlerini sıkılaştırın, 2) Tedarikçi denetimi yapın, 3) Kusurlu ürünler için hızlı iade prosedürü",
            "keywords": ["kalite", "bozuk", "defolu", "kötü"]
        },
        {
            "category": "beden",
            "problem": "Beden uyumsuzluğu ve kalıp sorunları",
            "solution": "1) Beden tablosunu güncelleyin, 2) AR deneme özelliği ekleyin, 3) Müşteri yorumlarından beden önerileri",
            "keywords": ["beden", "uyum", "kalıp", "büyük", "küçük"]
        },
        {
            "category": "musteri_hizmetleri",
            "problem": "Müşteri hizmetleri yanıt süresi ve kalitesi",
            "solution": "1) 24/7 chat desteği kurun, 2) Yanıt süresini 2 saate düşürün, 3) Çok dilli destek sağlayın",
            "keywords": ["müşteri", "hizmet", "destek", "yanıt"]
        },
        {
            "category": "fiyat",
            "problem": "Fiyat algısı ve değer sorunları",
            "solution": "1) Rekabet analizi yapın, 2) Kampanya ve indirim sistemi kurun, 3) Değer algısını artıracak içerikler",
            "keywords": ["fiyat", "pahalı", "değer", "ucuz"]
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
    """Ana demo fonksiyonu"""
    print("🚀 BASİT RAG SİSTEMİ DEMO")
    print("=" * 50)
    print("Python 3.13 uyumlu, minimal bağımlılık")
    
    # RAG sistemini başlat
    rag = SimpleRAGSystem()
    
    # CSV'den yorumları yükle
    doc_count = rag.load_comments_from_csv("trendyol_comments.csv")
    if doc_count == 0:
        print("⚠️ CSV dosyası bulunamadı veya yüklenemedi")
        print("💡 Önce trendyol_selenium_scraper.py çalıştırarak yorum toplayın")
        return
    
    # Demo bilgi tabanını kur
    setup_demo_knowledge(rag)
    
    # Sistem istatistikleri
    stats = rag.get_stats()
    print(f"\n📊 SİSTEM İSTATİSTİKLERİ:")
    print(f"   📝 Toplam Yorum: {stats['total_comments']}")
    print(f"   📚 Bilgi Tabanı: {stats['total_knowledge_entries']}")
    print(f"   📈 Ortalama Öncelik: {stats['average_priority']}/100")
    print(f"   🔧 Gelişmiş Analiz: {'✅' if stats['has_advanced_analyzers'] else '❌'}")
    
    # Demo sorguları
    demo_questions = [
        "Kargo sorunları hakkında şikayetler var mı?",
        "Ürün kalitesi ile ilgili ne tür sorunlar yaşanıyor?",
        "Beden uyumsuzluğu için ne önerirsin?",
        "Müşteri hizmetleri nasıl iyileştirilebilir?",
        "En yüksek öncelikli problemler neler?"
    ]
    
    print(f"\n💬 DEMO SORGULARI:")
    print("=" * 50)
    
    for question in demo_questions:
        print(f"\n❓ SORU: {question}")
        print("-" * 40)
        
        result = rag.query(question)
        print(f"🤖 YANIT:\n{result['answer']}")
        print(f"📊 Bulunan benzer yorum: {len(result['similar_comments'])}")
        print(f"📚 Bilgi tabanı sonucu: {len(result['knowledge_results'])}")
    
    print(f"\n✅ DEMO TAMAMLANDI!")
    print("\n💡 Gelişmiş özellikler için:")
    print("   - LangChain kurulumu: pip install langchain chromadb")
    print("   - Web arayüzü: streamlit run rag_chat_interface.py")


if __name__ == "__main__":
    main() 