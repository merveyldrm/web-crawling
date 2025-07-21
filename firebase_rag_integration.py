import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import os

# Local imports
from advanced_comment_analyzer import AdvancedCommentAnalyzer
from priority_analyzer import PriorityAnalyzer

class FirebaseRAGSystem:
    def __init__(self, service_account_path: str = None):
        """
        Firebase RAG sistemi başlatıcı
        
        Args:
            service_account_path: Firebase service account JSON dosya yolu
        """
        self.db = None
        self.comment_analyzer = AdvancedCommentAnalyzer()
        self.priority_analyzer = PriorityAnalyzer()
        
        # Firebase bağlantısını kur
        self.init_firebase(service_account_path)
        
        # Koleksiyon isimleri
        self.collections = {
            'comments': 'trendyol_comments',
            'analysis_results': 'comment_analysis',
            'knowledge_base': 'rag_knowledge',
            'priority_scores': 'priority_analysis',
            'monitoring_logs': 'realtime_logs'
        }
        
        print("✅ Firebase RAG Sistemi başlatıldı")
    
    def init_firebase(self, service_account_path: str = None):
        """Firebase bağlantısını başlat"""
        try:
            # Eğer zaten başlatılmışsa atla
            if firebase_admin._apps:
                self.db = firestore.client()
                return
            
            # Service account dosyası kontrolü
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase service account ile bağlandı: {service_account_path}")
            else:
                # Çevresel değişkenlerle denemeye çalış
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase default credentials ile bağlandı")
                else:
                    # Demo mode - yerel emulator
                    print("⚠️ Firebase credentials bulunamadı.")
                    print("📝 Demo mode: Firestore emulator kullanılacak")
                    
                    # Emulator environment variables
                    os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
                    
                    firebase_admin.initialize_app()
                    print("🔧 Firestore emulator bağlantısı kuruldu")
            
            self.db = firestore.client()
            
        except Exception as e:
            print(f"❌ Firebase bağlantı hatası: {e}")
            print("💡 Çözüm önerileri:")
            print("   1. Firebase service account JSON dosyasını indirin")
            print("   2. GOOGLE_APPLICATION_CREDENTIALS environment variable'ını ayarlayın")
            print("   3. Firestore emulator çalıştırın: firebase emulators:start")
            raise
    
    def upload_csv_to_firestore(self, csv_file_path: str = "trendyol_comments.csv"):
        """CSV dosyasından Firestore'a yorum yükleme"""
        
        print(f"📤 {csv_file_path} dosyası Firestore'a yükleniyor...")
        
        try:
            # CSV'yi oku
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            
            # Başarı sayacı
            uploaded_count = 0
            skipped_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Yorum hash'i oluştur (tekrar kontrolü için)
                    comment_hash = self.create_comment_hash(row)
                    
                    # Bu yorum zaten var mı kontrol et
                    existing = self.db.collection(self.collections['comments']).where('comment_hash', '==', comment_hash).limit(1).get()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Yorum verisini hazırla
                    comment_data = {
                        'comment_hash': comment_hash,
                        'user': str(row.get('user', 'Anonymous')),
                        'date': str(row.get('date', '')),
                        'comment': str(row.get('comment', '')),
                        'uploaded_at': firestore.SERVER_TIMESTAMP,
                        'processed': False,
                        'analysis_completed': False
                    }
                    
                    # Firestore'a ekle
                    self.db.collection(self.collections['comments']).add(comment_data)
                    uploaded_count += 1
                    
                    # İlerleme göster
                    if uploaded_count % 10 == 0:
                        print(f"📊 {uploaded_count} yorum yüklendi...")
                
                except Exception as e:
                    print(f"⚠️ Satır {index} yüklenirken hata: {e}")
                    continue
            
            print(f"✅ Yükleme tamamlandı!")
            print(f"📊 Yeni yüklenen: {uploaded_count}")
            print(f"📊 Zaten mevcut: {skipped_count}")
            print(f"📊 Toplam: {uploaded_count + skipped_count}")
            
            return uploaded_count
            
        except Exception as e:
            print(f"❌ CSV yükleme hatası: {e}")
            return 0
    
    def create_comment_hash(self, row) -> str:
        """Yorum için unique hash oluştur"""
        content = f"{row.get('user', '')}{row.get('date', '')}{row.get('comment', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_unanalyzed_comments(self):
        """İşlenmemiş yorumları analiz et"""
        
        print("🔍 İşlenmemiş yorumlar aranıyor...")
        
        # İşlenmemiş yorumları getir
        unprocessed_docs = self.db.collection(self.collections['comments']).where('processed', '==', False).limit(50).get()
        
        if not unprocessed_docs:
            print("✅ Tüm yorumlar işlenmiş")
            return 0
        
        processed_count = 0
        
        for doc in unprocessed_docs:
            try:
                doc_data = doc.to_dict()
                comment_text = doc_data.get('comment', '')
                
                if not comment_text:
                    continue
                
                print(f"🔬 Analiz ediliyor: {comment_text[:50]}...")
                
                # 1. Sentiment ve kategori analizi
                comments_list = [doc_data]
                analysis_result = self.comment_analyzer.analyze_all_comments(comments_list)
                
                # 2. Öncelik analizi
                priority_result = self.priority_analyzer.analyze_critical_issues(comments_list, analysis_result)
                
                # 3. Sonuçları Firebase'e kaydet
                analysis_doc = {
                    'comment_id': doc.id,
                    'comment_hash': doc_data['comment_hash'],
                    'sentiment_analysis': analysis_result,
                    'priority_analysis': priority_result,
                    'analyzed_at': firestore.SERVER_TIMESTAMP,
                    'version': '1.0'
                }
                
                # Analysis koleksiyonuna ekle
                self.db.collection(self.collections['analysis_results']).add(analysis_doc)
                
                # Yorumun processed flag'ini güncelle
                doc.reference.update({
                    'processed': True,
                    'analysis_completed': True,
                    'processed_at': firestore.SERVER_TIMESTAMP
                })
                
                processed_count += 1
                
                # Rate limiting (Firebase quota için)
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Yorum analiz hatası: {e}")
                continue
        
        print(f"✅ {processed_count} yorum analiz edildi ve Firebase'e kaydedildi")
        return processed_count
    
    def add_knowledge_base_entry(self, category: str, problem: str, solution: str, source: str = "internal"):
        """RAG bilgi tabanına entry ekle"""
        
        knowledge_entry = {
            'category': category,
            'problem_description': problem,
            'solution': solution,
            'source': source,
            'created_at': firestore.SERVER_TIMESTAMP,
            'usage_count': 0,
            'effectiveness_score': 0.0,
            'tags': self.extract_tags(problem + " " + solution)
        }
        
        doc_ref = self.db.collection(self.collections['knowledge_base']).add(knowledge_entry)
        print(f"📚 Bilgi tabanına eklendi: {category} - {problem[:50]}...")
        
        return doc_ref[1].id  # Document ID'yi döndür
    
    def extract_tags(self, text: str) -> List[str]:
        """Metinden tag'ler çıkar"""
        # Basit tag extraction
        keywords = ['kargo', 'teslimat', 'kalite', 'beden', 'fiyat', 'renk', 'müşteri', 'hizmet']
        found_tags = [keyword for keyword in keywords if keyword in text.lower()]
        return found_tags
    
    def search_knowledge_base(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """RAG bilgi tabanında arama"""
        
        print(f"🔍 Bilgi tabanında arama: '{query}'")
        
        # Firestore query oluştur
        kb_ref = self.db.collection(self.collections['knowledge_base'])
        
        if category:
            kb_ref = kb_ref.where('category', '==', category)
        
        # Basit text matching (Firestore'da full-text search sınırlı)
        docs = kb_ref.limit(50).get()  # Daha fazla doc getir, sonra filtrele
        
        results = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id
            
            # Basit relevance scoring
            relevance_score = self.calculate_relevance(query, doc_data)
            
            if relevance_score > 0:
                doc_data['relevance_score'] = relevance_score
                results.append(doc_data)
        
        # Relevance'a göre sırala ve limit uygula
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"📊 {len(results)} sonuç bulundu")
        
        return results[:limit]
    
    def calculate_relevance(self, query: str, knowledge_entry: Dict) -> float:
        """Basit relevance score hesaplama"""
        
        query_lower = query.lower()
        score = 0.0
        
        # Problem description'da arama
        problem = knowledge_entry.get('problem_description', '').lower()
        if query_lower in problem:
            score += 1.0
        
        # Tag'lerde arama
        tags = knowledge_entry.get('tags', [])
        for tag in tags:
            if tag.lower() in query_lower:
                score += 0.5
        
        # Category match
        category = knowledge_entry.get('category', '').lower()
        if category in query_lower:
            score += 0.3
        
        return score
    
    def get_real_time_insights(self) -> Dict:
        """Gerçek zamanlı insight'lar"""
        
        print("📊 Gerçek zamanlı insight'lar hesaplanıyor...")
        
        # Son 24 saatin yorumları
        yesterday = datetime.now() - timedelta(days=1)
        
        # Firestore timestamp query
        recent_comments = self.db.collection(self.collections['comments']).where(
            'uploaded_at', '>=', yesterday
        ).get()
        
        # Son analizler
        recent_analysis = self.db.collection(self.collections['analysis_results']).where(
            'analyzed_at', '>=', yesterday
        ).get()
        
        # İstatistikleri hesapla
        insights = {
            'total_comments_24h': len(recent_comments),
            'analyzed_comments_24h': len(recent_analysis),
            'processing_rate': len(recent_analysis) / max(len(recent_comments), 1) * 100,
            'timestamp': datetime.now().isoformat(),
            'urgent_categories': [],
            'top_issues': []
        }
        
        # Acil kategorileri bul
        urgent_count = 0
        for analysis_doc in recent_analysis:
            analysis_data = analysis_doc.to_dict()
            priority_data = analysis_data.get('priority_analysis', {})
            
            if 'critical_issues' in priority_data:
                for category, data in priority_data['critical_issues'].items():
                    if data.get('priority_score', 0) >= 80:
                        urgent_count += 1
                        insights['urgent_categories'].append({
                            'category': category,
                            'score': data.get('priority_score', 0)
                        })
        
        insights['urgent_count'] = urgent_count
        
        print(f"📈 24 saat özeti: {insights['total_comments_24h']} yorum, {urgent_count} acil kategori")
        
        return insights
    
    def setup_sample_knowledge_base(self):
        """Örnek bilgi tabanı kurulumu"""
        
        print("📚 Örnek bilgi tabanı kuruluyor...")
        
        sample_knowledge = [
            {
                'category': 'kargo',
                'problem': 'Kargo gecikmesi ve teslimat sorunları',
                'solution': 'Alternatif kargo firmaları ile anlaşma yapın, express teslimat seçeneği sunun, kargo takip sistemini iyileştirin',
                'source': 'internal_policy'
            },
            {
                'category': 'kargo',
                'problem': 'Hasarlı paket gelişi',
                'solution': 'Paketleme kalitesini artırın, kargo firması ile hasar anlaşması yapın, müşteriye anında değişim sunun',
                'source': 'customer_support'
            },
            {
                'category': 'kalite',
                'problem': 'Ürün kalitesi ve defolu ürün şikayetleri',
                'solution': 'Kalite kontrol sürecini sıkılaştırın, tedarikçi denetimi yapın, hızlı iade/değişim prosedürü uygulayın',
                'source': 'quality_department'
            },
            {
                'category': 'beden_uyum',
                'problem': 'Beden uyumsuzluğu ve kalıp sorunları',
                'solution': 'Beden tablosunu güncelleyin, model fotoğraflarını standartlaştırın, AR deneme özelliği ekleyin',
                'source': 'product_management'
            },
            {
                'category': 'fiyat',
                'problem': 'Yüksek fiyat ve değer algısı sorunları',
                'solution': 'Rekabetçi fiyatlandırma analizi yapın, değer önerisi iyileştirin, kampanya ve indirim stratejileri geliştirin',
                'source': 'pricing_team'
            },
            {
                'category': 'musteri_hizmeti',
                'problem': 'Müşteri hizmetleri yanıt süresi ve kalitesi',
                'solution': 'Chatbot entegrasyonu yapın, FAQ sistemini güncelleyin, temsilci eğitimlerini artırın',
                'source': 'customer_service'
            }
        ]
        
        added_count = 0
        for knowledge in sample_knowledge:
            try:
                self.add_knowledge_base_entry(
                    knowledge['category'],
                    knowledge['problem'],
                    knowledge['solution'],
                    knowledge['source']
                )
                added_count += 1
            except Exception as e:
                print(f"⚠️ Bilgi eklenirken hata: {e}")
        
        print(f"✅ {added_count} bilgi tabanı girdisi eklendi")
    
    def demonstrate_rag_system(self):
        """RAG sistemi demonstrasyonu"""
        
        print("\n🔥 FİREBASE RAG SİSTEMİ DEMO")
        print("="*50)
        
        # 1. CSV'yi yükle
        uploaded = self.upload_csv_to_firestore()
        
        # 2. Bilgi tabanını kur
        self.setup_sample_knowledge_base()
        
        # 3. Yorumları analiz et
        if uploaded > 0:
            processed = self.process_unanalyzed_comments()
        
        # 4. RAG aramaları test et
        test_queries = [
            "kargo gecikmesi nasıl çözülür",
            "ürün kalitesi sorunları",
            "beden uyumsuzluğu çözümü"
        ]
        
        print(f"\n🔍 RAG ARAMA TESTLERİ:")
        print("-" * 30)
        
        for query in test_queries:
            results = self.search_knowledge_base(query, limit=2)
            
            print(f"\n📝 Sorgu: '{query}'")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['solution'][:100]}...")
                print(f"      📊 Relevance: {result['relevance_score']:.2f}")
        
        # 5. Gerçek zamanlı insight'lar
        insights = self.get_real_time_insights()
        print(f"\n📊 GERÇEKDökan ZAMANLI İNSIGHT'LAR:")
        print(f"   📈 24 saat içinde: {insights['total_comments_24h']} yorum")
        print(f"   🔬 Analiz edilen: {insights['analyzed_comments_24h']} yorum")
        print(f"   🚨 Acil kategori: {insights['urgent_count']}")

def main():
    """Firebase RAG sistemi ana fonksiyon"""
    
    print("🚀 FİREBASE RAG SİSTEMİ v1.0")
    print("📊 Gerçek Veritabanı + RAG Entegrasyonu")
    print("="*60)
    
    # Service account path (kullanıcıdan al veya environment variable)
    service_account = input("Firebase service account JSON path (boş bırakabilirsiniz): ").strip()
    service_account = service_account if service_account else None
    
    try:
        # Firebase RAG sistemini başlat
        firebase_rag = FirebaseRAGSystem(service_account)
        
        print("\n🔍 Hangi işlemi yapmak istiyorsunuz?")
        print("1. 📤 CSV'yi Firestore'a yükle")
        print("2. 🔬 Yorumları analiz et")
        print("3. 📚 Bilgi tabanını kur")
        print("4. 🔍 RAG arama testi")
        print("5. 📊 Gerçek zamanlı insight'lar")
        print("6. 🎯 Tam demo (hepsi)")
        print("7. 🚪 Çıkış")
        
        choice = input("\nSeçiminiz (1-7): ").strip()
        
        if choice == '1':
            firebase_rag.upload_csv_to_firestore()
        
        elif choice == '2':
            firebase_rag.process_unanalyzed_comments()
        
        elif choice == '3':
            firebase_rag.setup_sample_knowledge_base()
        
        elif choice == '4':
            query = input("Arama sorgunuz: ")
            results = firebase_rag.search_knowledge_base(query)
            
            print(f"\n🔍 '{query}' için sonuçlar:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['solution']}")
                print(f"   📊 Relevance: {result['relevance_score']:.2f}")
                print(f"   📋 Kategori: {result['category']}")
        
        elif choice == '5':
            insights = firebase_rag.get_real_time_insights()
            print(f"\n📊 Gerçek zamanlı insight'lar:")
            print(json.dumps(insights, indent=2, ensure_ascii=False, default=str))
        
        elif choice == '6':
            firebase_rag.demonstrate_rag_system()
        
        elif choice == '7':
            print("👋 Sistem kapatılıyor...")
        
        else:
            print("❌ Geçersiz seçim!")
    
    except Exception as e:
        print(f"❌ Sistem hatası: {e}")
        print("\n💡 Çözüm önerileri:")
        print("1. Firebase proje ayarlarını kontrol edin")
        print("2. Service account JSON dosyasını indirin")
        print("3. Firestore emulator çalıştırın: firebase emulators:start")

if __name__ == "__main__":
    main() 