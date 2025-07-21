import asyncio
import json
import time
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
from queue import Queue
import sqlite3
from dataclasses import dataclass
import schedule

# External imports for RAG
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    import openai  # OpenAI API for enhanced text generation
except ImportError:
    print("⚠️ Bazı RAG kütüphaneleri eksik. 'pip install sentence-transformers openai' çalıştırın")

from advanced_comment_analyzer import AdvancedCommentAnalyzer
from priority_analyzer import PriorityAnalyzer
from topic_modeling_analyzer import TopicModelingAnalyzer

@dataclass
class ExternalSource:
    name: str
    url: str
    source_type: str  # 'api', 'web_scrape', 'document'
    update_frequency: str  # 'hourly', 'daily', 'weekly'
    last_updated: Optional[datetime] = None

class RAGKnowledgeBase:
    def __init__(self, db_path: str = "rag_knowledge.db"):
        self.db_path = db_path
        self.embedding_model = None
        self.init_database()
        
        # Sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Embedding modeli yüklendi")
        except Exception as e:
            print(f"⚠️ Embedding modeli yüklenemedi: {e}")
    
    def init_database(self):
        """SQLite veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Harici bilgi kaynakları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS external_sources (
                id INTEGER PRIMARY KEY,
                source_name TEXT UNIQUE,
                content TEXT,
                embedding BLOB,
                url TEXT,
                source_type TEXT,
                last_updated TIMESTAMP,
                relevance_score REAL DEFAULT 0.0
            )
        ''')
        
        # Ürün bilgileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_info (
                id INTEGER PRIMARY KEY,
                product_name TEXT,
                brand TEXT,
                category TEXT,
                technical_specs TEXT,
                official_description TEXT,
                embedding BLOB,
                last_updated TIMESTAMP
            )
        ''')
        
        # Yorum geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comment_history (
                id INTEGER PRIMARY KEY,
                comment_hash TEXT UNIQUE,
                comment_text TEXT,
                analysis_result TEXT,
                priority_score REAL,
                timestamp TIMESTAMP,
                processed BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_external_source(self, source_name: str, content: str, url: str, source_type: str):
        """Harici kaynak ekle ve embedding oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Embedding oluştur
        embedding = None
        if self.embedding_model:
            try:
                embedding_vector = self.embedding_model.encode([content])[0]
                embedding = embedding_vector.tobytes()
            except Exception as e:
                print(f"⚠️ Embedding oluşturulamadı: {e}")
        
        cursor.execute('''
            INSERT OR REPLACE INTO external_sources 
            (source_name, content, embedding, url, source_type, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_name, content, embedding, url, source_type, datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Harici kaynak eklendi: {source_name}")
    
    def find_relevant_context(self, query: str, limit: int = 3) -> List[Dict]:
        """Query'ye en yakın harici kaynakları bul"""
        if not self.embedding_model:
            return []
        
        try:
            query_embedding = self.embedding_model.encode([query])[0]
        except Exception:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT source_name, content, url, embedding FROM external_sources WHERE embedding IS NOT NULL')
        results = []
        
        for row in cursor.fetchall():
            source_name, content, url, embedding_bytes = row
            
            try:
                stored_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = cosine_similarity([query_embedding], [stored_embedding])[0][0]
                
                results.append({
                    'source_name': source_name,
                    'content': content[:500] + '...' if len(content) > 500 else content,
                    'url': url,
                    'similarity': float(similarity)
                })
            except Exception:
                continue
        
        conn.close()
        
        # Benzerlik skoruna göre sırala
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

class RealTimeCommentMonitor:
    def __init__(self, check_interval: int = 300):  # 5 dakika
        self.check_interval = check_interval
        self.comment_analyzer = AdvancedCommentAnalyzer()
        self.priority_analyzer = PriorityAnalyzer()
        self.topic_analyzer = TopicModelingAnalyzer()
        self.rag_kb = RAGKnowledgeBase()
        
        self.comment_queue = Queue()
        self.is_running = False
        self.last_check = datetime.now()
        
        # Otomatik raporlama
        self.auto_reports = {
            'hourly_priority': True,
            'daily_summary': True,
            'weekly_trend': True
        }
    
    def load_current_comments(self) -> List[Dict]:
        """Mevcut yorumları yükle"""
        return self.comment_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    def get_comment_hash(self, comment: Dict) -> str:
        """Yorum için hash oluştur (tekrar kontrolü için)"""
        comment_str = f"{comment.get('comment', '')}{comment.get('user', '')}{comment.get('date', '')}"
        return hashlib.md5(comment_str.encode()).hexdigest()
    
    def check_for_new_comments(self) -> List[Dict]:
        """Yeni yorumları kontrol et"""
        current_comments = self.load_current_comments()
        new_comments = []
        
        conn = sqlite3.connect(self.rag_kb.db_path)
        cursor = conn.cursor()
        
        for comment in current_comments:
            comment_hash = self.get_comment_hash(comment)
            
            # Bu yorum daha önce işlendi mi?
            cursor.execute('SELECT id FROM comment_history WHERE comment_hash = ?', (comment_hash,))
            if not cursor.fetchone():
                new_comments.append(comment)
                
                # Yeni yorumu veritabanına ekle
                cursor.execute('''
                    INSERT INTO comment_history (comment_hash, comment_text, timestamp)
                    VALUES (?, ?, ?)
                ''', (comment_hash, comment.get('comment', ''), datetime.now()))
        
        conn.commit()
        conn.close()
        
        return new_comments
    
    def enhanced_analysis_with_rag(self, comments: List[Dict]) -> Dict:
        """RAG destekli gelişmiş analiz"""
        if not comments:
            return {'message': 'Yeni yorum bulunamadı'}
        
        print(f"🔍 {len(comments)} yeni yorum analiz ediliyor...")
        
        # 1. Temel analizler
        analysis_results = self.comment_analyzer.analyze_all_comments(comments)
        priority_results = self.priority_analyzer.analyze_critical_issues(comments, analysis_results)
        
        # 2. RAG ile harici bağlam bulma
        enhanced_results = analysis_results.copy()
        enhanced_results['rag_context'] = {}
        
        for category in analysis_results.get('category_analysis', {}):
            # Her kategori için harici kaynaklardan bilgi al
            category_comments = analysis_results['category_analysis'][category]
            
            if category_comments.get('negative'):
                # Negatif yorumlar için harici çözümler ara
                query = f"{category} problemi çözümü öneri iyileştirme"
                context = self.rag_kb.find_relevant_context(query, limit=2)
                
                enhanced_results['rag_context'][category] = {
                    'external_solutions': context,
                    'query_used': query
                }
        
        # 3. AI destekli öneriler (eğer OpenAI key varsa)
        enhanced_results['ai_recommendations'] = self.generate_ai_recommendations(priority_results)
        
        return {
            'analysis_results': enhanced_results,
            'priority_results': priority_results,
            'new_comments_count': len(comments),
            'analysis_timestamp': datetime.now().isoformat(),
            'rag_enhanced': True
        }
    
    def generate_ai_recommendations(self, priority_results: Dict) -> Dict:
        """AI destekli öneriler oluştur"""
        recommendations = {}
        
        try:
            # OpenAI API key kontrolü (çevresel değişken olarak)
            import os
            if not os.getenv('OPENAI_API_KEY'):
                return {'message': 'OpenAI API key bulunamadı (opsiyonel)'}
            
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            critical_issues = priority_results.get('critical_issues', {})
            
            for category, data in critical_issues.items():
                if data['priority_score'] > 60:  # Sadece yüksek öncelik
                    
                    prompt = f"""
                    E-ticaret kategorisi: {category}
                    Öncelik skoru: {data['priority_score']}/100
                    Şikayet sayısı: {data['total_negative_comments']}
                    Sorumlu departman: {data['category_info']['department']}
                    
                    Bu kategori için 3 spesifik, uygulanabilir iyileştirme önerisi ver:
                    """
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    recommendations[category] = {
                        'ai_suggestions': response.choices[0].message.content,
                        'priority_score': data['priority_score']
                    }
        
        except Exception as e:
            return {'error': f'AI öneriler oluşturulamadı: {e}'}
        
        return recommendations
    
    def start_monitoring(self):
        """Gerçek zamanlı izlemeyi başlat"""
        self.is_running = True
        print("🚀 Gerçek zamanlı yorum izleme başlatıldı!")
        print(f"⏰ Kontrol aralığı: {self.check_interval} saniye")
        
        # Scheduled tasks
        schedule.every().hour.do(self.hourly_priority_check)
        schedule.every().day.at("09:00").do(self.daily_summary_report)
        schedule.every().week.do(self.weekly_trend_report)
        
        while self.is_running:
            try:
                # 1. Yeni yorumları kontrol et
                new_comments = self.check_for_new_comments()
                
                if new_comments:
                    print(f"📝 {len(new_comments)} yeni yorum bulundu!")
                    
                    # 2. RAG destekli analiz yap
                    enhanced_analysis = self.enhanced_analysis_with_rag(new_comments)
                    
                    # 3. Sonuçları kaydet ve bildir
                    self.save_realtime_analysis(enhanced_analysis)
                    self.notify_if_critical(enhanced_analysis)
                
                # 4. Scheduled görevleri çalıştır
                schedule.run_pending()
                
                # 5. Bekle
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ İzleme durduruldu")
                break
            except Exception as e:
                print(f"❌ İzleme hatası: {e}")
                time.sleep(30)  # Hata durumunda biraz bekle
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.is_running = False
        print("⏹️ Gerçek zamanlı izleme durduruldu")
    
    def hourly_priority_check(self):
        """Saatlik öncelik kontrolü"""
        print("⏰ Saatlik öncelik kontrolü yapılıyor...")
        
        comments = self.load_current_comments()
        if len(comments) < 10:
            return
        
        analysis = self.comment_analyzer.analyze_all_comments(comments)
        priority = self.priority_analyzer.analyze_critical_issues(comments, analysis)
        
        # Acil durumları kontrol et
        critical_issues = priority.get('critical_issues', {})
        urgent_count = sum(1 for cat, data in critical_issues.items() if data['priority_score'] >= 80)
        
        if urgent_count > 0:
            self.send_urgent_alert(f"🚨 {urgent_count} acil kategori tespit edildi!")
    
    def daily_summary_report(self):
        """Günlük özet raporu"""
        print("📊 Günlük özet raporu oluşturuluyor...")
        
        # Son 24 saatin yorumlarını analiz et
        # (Bu örnekte tüm yorumları kullanıyoruz)
        comments = self.load_current_comments()
        
        if comments:
            enhanced_analysis = self.enhanced_analysis_with_rag(comments)
            
            # Günlük rapor dosyası oluştur
            daily_report_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(daily_report_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_analysis, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"📄 Günlük rapor kaydedildi: {daily_report_file}")
    
    def weekly_trend_report(self):
        """Haftalık trend raporu"""
        print("📈 Haftalık trend raporu oluşturuluyor...")
        # Haftalık trendleri analiz etme kodu buraya gelecek
    
    def save_realtime_analysis(self, analysis: Dict):
        """Gerçek zamanlı analiz sonuçlarını kaydet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"realtime_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Gerçek zamanlı analiz kaydedildi: {filename}")
    
    def notify_if_critical(self, analysis: Dict):
        """Kritik durumda bildirim gönder"""
        priority_results = analysis.get('priority_results', {})
        critical_issues = priority_results.get('critical_issues', {})
        
        urgent_categories = [
            cat for cat, data in critical_issues.items() 
            if data['priority_score'] >= 80
        ]
        
        if urgent_categories:
            alert_message = f"🚨 ACİL: {', '.join(urgent_categories)} kategorilerinde kritik sorunlar tespit edildi!"
            self.send_urgent_alert(alert_message)
    
    def send_urgent_alert(self, message: str):
        """Acil durum bildirimi gönder"""
        print(f"\n{'='*60}")
        print(f"🚨 ACİL DURUM BİLDİRİMİ 🚨")
        print(f"⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📢 Mesaj: {message}")
        print(f"{'='*60}\n")
        
        # Burada email, SMS, Slack vb. entegrasyonları eklenebilir
        # send_email(message)
        # send_slack_notification(message)

class ExternalDataCollector:
    def __init__(self, rag_kb: RAGKnowledgeBase):
        self.rag_kb = rag_kb
        self.sources = [
            ExternalSource("Trendyol Yardım", "https://yardim.trendyol.com", "web_scrape", "daily"),
            ExternalSource("Müşteri Hizmetleri KB", "internal_kb", "document", "weekly"),
            ExternalSource("Ürün Katalog API", "api_endpoint", "api", "hourly")
        ]
    
    def collect_product_specifications(self, product_name: str):
        """Ürün teknik özelliklerini topla"""
        # Örnek: Ürün API'sinden bilgi çekme
        try:
            # Bu gerçek bir API call olacak
            specs = {
                'marka': 'Örnek Marka',
                'kategori': 'Bebek Gıdası',
                'malzemeler': 'Organik malzemeler',
                'saklama_koşulları': 'Serin ve kuru yerde',
                'kullanım_talimatları': 'Yemekten önce karıştırın'
            }
            
            content = f"Ürün: {product_name}\n"
            content += "\n".join([f"{k}: {v}" for k, v in specs.items()])
            
            self.rag_kb.add_external_source(
                f"ürün_specs_{product_name}",
                content,
                "internal_api",
                "api"
            )
            
        except Exception as e:
            print(f"⚠️ Ürün bilgisi alınamadı: {e}")
    
    def collect_troubleshooting_guides(self):
        """Sorun giderme kılavuzlarını topla"""
        guides = {
            'kargo_sorunları': """
            Kargo Sorunları için Çözümler:
            1. Geciken kargolar için kargo firması ile iletişime geçin
            2. Hasarlı paketler için fotoğraf çekin ve müşteri hizmetlerine bildirin
            3. Kayıp kargolar için takip numarası ile sorgulatın
            """,
            'ürün_kalitesi': """
            Kalite Sorunları için Aksiyonlar:
            1. Defolu ürünler için kalite kontrol sürecini gözden geçirin
            2. Tedarikçi denetimi yapın
            3. İade/değişim sürecini hızlandırın
            """,
            'beden_uyumsuzluğu': """
            Beden Sorunları için Çözümler:
            1. Beden tablosunu güncelleyin
            2. Model fotoğraflarını standardize edin
            3. Müşteri yorumlarında beden önerilerini paylaşın
            """
        }
        
        for guide_name, content in guides.items():
            self.rag_kb.add_external_source(
                f"guide_{guide_name}",
                content,
                "internal_knowledge_base",
                "document"
            )

def main():
    """Gerçek zamanlı RAG sistemi demo"""
    
    print("🚀 GERÇEK ZAMANLI RAG SİSTEMİ v1.0")
    print("📊 Otomatik Yorum Analizi + Harici Kaynak Entegrasyonu")
    print("="*70)
    
    # Sistem kurulumu
    monitor = RealTimeCommentMonitor(check_interval=60)  # 1 dakika test için
    data_collector = ExternalDataCollector(monitor.rag_kb)
    
    print("🔧 Sistem hazırlanıyor...")
    
    # Harici verileri topla
    data_collector.collect_troubleshooting_guides()
    data_collector.collect_product_specifications("Bebek Maması")
    
    print("✅ Harici veriler yüklendi")
    
    # Kullanıcı seçimi
    print("\n🔍 Hangi modu çalıştırmak istiyorsunuz?")
    print("1. 🔄 Gerçek Zamanlı İzleme (Sürekli)")
    print("2. 📊 Tek Seferlik RAG Analizi")
    print("3. 🧪 RAG Bilgi Tabanı Testi")
    print("4. 🚪 Çıkış")
    
    choice = input("\nSeçiminiz (1-4): ").strip()
    
    if choice == '1':
        print("\n🚀 Gerçek zamanlı izleme başlatılıyor...")
        print("💡 Durdurmak için Ctrl+C basın")
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            print("\n⏹️ İzleme durduruldu")
    
    elif choice == '2':
        print("\n📊 Tek seferlik RAG analizi yapılıyor...")
        comments = monitor.load_current_comments()
        enhanced_analysis = monitor.enhanced_analysis_with_rag(comments)
        
        # Sonuçları göster
        if 'analysis_results' in enhanced_analysis:
            print(f"\n✅ {enhanced_analysis['new_comments_count']} yorum analiz edildi")
            
            # RAG bağlamını göster
            rag_context = enhanced_analysis['analysis_results'].get('rag_context', {})
            if rag_context:
                print(f"\n🧠 RAG BAĞLAMI:")
                for category, context in rag_context.items():
                    print(f"   📋 {category.upper()}:")
                    for solution in context.get('external_solutions', []):
                        print(f"      🔗 {solution['source_name']}: {solution['content'][:100]}...")
        
        # AI önerileri
        ai_recs = enhanced_analysis.get('ai_recommendations', {})
        if ai_recs and 'error' not in ai_recs:
            print(f"\n🤖 AI ÖNERİLERİ:")
            for category, rec in ai_recs.items():
                print(f"   📋 {category}: {rec['ai_suggestions'][:200]}...")
    
    elif choice == '3':
        print("\n🧪 RAG bilgi tabanı test ediliyor...")
        
        test_queries = [
            "kargo gecikmesi nasıl çözülür",
            "ürün kalitesi sorunları için ne yapılmalı",
            "beden uyumsuzluğu çözümleri"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            results = monitor.rag_kb.find_relevant_context(query, limit=2)
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['source_name']}")
                print(f"      📊 Benzerlik: %{result['similarity']*100:.1f}")
                print(f"      📝 İçerik: {result['content'][:150]}...")
    
    elif choice == '4':
        print("👋 Sistem kapatılıyor...")
    
    else:
        print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main() 