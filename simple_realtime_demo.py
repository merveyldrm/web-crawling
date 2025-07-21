import time
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import schedule
from pathlib import Path

# Local imports
from advanced_comment_analyzer import AdvancedCommentAnalyzer
from priority_analyzer import PriorityAnalyzer

class SimpleRealTimeMonitor:
    def __init__(self, check_interval: int = 10):  # 10 saniye test için
        self.check_interval = check_interval
        self.comment_analyzer = AdvancedCommentAnalyzer()
        self.priority_analyzer = PriorityAnalyzer()
        
        self.is_running = False
        self.db_path = "simple_realtime.db"
        self.init_database()
        
        # Simulated external knowledge base
        self.knowledge_base = {
            'kargo_solutions': [
                "Kargo gecikmelerine karşı alternatif kargo firmaları ile anlaşma yapın",
                "Express teslimat seçeneği sunarak müşteri memnuniyetini artırın",
                "Kargo takip sistemi entegrasyonu ile şeffaflık sağlayın"
            ],
            'kalite_solutions': [
                "Kalite kontrol süreçlerini sıkılaştırın ve rastgele örnekleme yapın",
                "Tedarikçi denetimi programını güçlendirin",
                "Müşteri geri bildirimlerini kalite ekibi ile paylaşın"
            ],
            'beden_solutions': [
                "Beden tablosunu günceller ve standardize edin",
                "AR (Artırılmış Gerçeklik) deneme özelliği ekleyin",
                "Müşteri yorumlarından beden önerilerine link ekleyin"
            ]
        }
        
        print("✅ Basit Gerçek Zamanlı İzleme Sistemi hazır")
    
    def init_database(self):
        """Basit SQLite veritabanı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY,
                comment_hash TEXT UNIQUE,
                comment_text TEXT,
                analysis_result TEXT,
                priority_score REAL,
                timestamp TIMESTAMP,
                alert_sent BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY,
                total_comments INTEGER,
                urgent_categories INTEGER,
                last_check TIMESTAMP,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📁 SQLite veritabanı hazırlandı")
    
    def get_comment_hash(self, comment: Dict) -> str:
        """Yorum için hash oluştur"""
        comment_str = f"{comment.get('comment', '')}{comment.get('user', '')}{comment.get('date', '')}"
        return hashlib.md5(comment_str.encode()).hexdigest()
    
    def load_current_comments(self) -> List[Dict]:
        """Mevcut yorumları yükle"""
        return self.comment_analyzer.load_comments_from_csv("trendyol_comments.csv")
    
    def check_for_new_comments(self) -> List[Dict]:
        """Yeni yorumları kontrol et (simulated)"""
        current_comments = self.load_current_comments()
        new_comments = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for comment in current_comments[:5]:  # İlk 5 yorumu test için kullan
            comment_hash = self.get_comment_hash(comment)
            
            cursor.execute('SELECT id FROM monitoring_log WHERE comment_hash = ?', (comment_hash,))
            if not cursor.fetchone():
                new_comments.append(comment)
                
                # Veritabanına ekle
                cursor.execute('''
                    INSERT INTO monitoring_log (comment_hash, comment_text, timestamp)
                    VALUES (?, ?, ?)
                ''', (comment_hash, comment.get('comment', ''), datetime.now()))
        
        conn.commit()
        conn.close()
        
        return new_comments
    
    def analyze_with_mock_rag(self, comments: List[Dict]) -> Dict:
        """Mock RAG sistemi ile analiz"""
        if not comments:
            return {'message': 'Yeni yorum bulunamadı'}
        
        print(f"🔍 {len(comments)} yeni yorum analiz ediliyor...")
        
        # Temel analizler
        analysis_results = self.comment_analyzer.analyze_all_comments(comments)
        priority_results = self.priority_analyzer.analyze_critical_issues(comments, analysis_results)
        
        # Mock RAG - harici çözümler
        enhanced_results = analysis_results.copy()
        enhanced_results['external_solutions'] = {}
        
        for category in analysis_results.get('category_analysis', {}):
            if category in self.knowledge_base:
                solutions_key = f"{category}_solutions"
                if solutions_key in self.knowledge_base:
                    enhanced_results['external_solutions'][category] = self.knowledge_base[solutions_key]
        
        return {
            'analysis_results': enhanced_results,
            'priority_results': priority_results,
            'new_comments_count': len(comments),
            'analysis_timestamp': datetime.now().isoformat(),
            'mock_rag_enhanced': True
        }
    
    def update_system_stats(self, enhanced_analysis: Dict):
        """Sistem istatistiklerini güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Acil kategori sayısı
        priority_results = enhanced_analysis.get('priority_results', {})
        critical_issues = priority_results.get('critical_issues', {})
        urgent_count = sum(1 for cat, data in critical_issues.items() if data['priority_score'] >= 80)
        
        # Toplam yorum sayısı
        total_comments = len(self.load_current_comments())
        
        cursor.execute('''
            INSERT INTO system_stats (total_comments, urgent_categories, last_check, status)
            VALUES (?, ?, ?, ?)
        ''', (total_comments, urgent_count, datetime.now(), 'active'))
        
        conn.commit()
        conn.close()
    
    def send_alert_if_needed(self, enhanced_analysis: Dict):
        """Gerekirse uyarı gönder"""
        priority_results = enhanced_analysis.get('priority_results', {})
        critical_issues = priority_results.get('critical_issues', {})
        
        urgent_categories = [
            cat for cat, data in critical_issues.items() 
            if data['priority_score'] >= 80
        ]
        
        if urgent_categories:
            alert_message = f"🚨 ACİL: {', '.join(urgent_categories)} kategorilerinde kritik sorunlar!"
            print(f"\n{'='*60}")
            print(f"🚨 GERÇEK ZAMANLI UYARI 🚨")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📢 {alert_message}")
            
            # Çözüm önerileri
            for category in urgent_categories:
                if category in enhanced_analysis['analysis_results'].get('external_solutions', {}):
                    solutions = enhanced_analysis['analysis_results']['external_solutions'][category]
                    print(f"\n💡 {category.upper()} için öneriler:")
                    for i, solution in enumerate(solutions[:2], 1):
                        print(f"   {i}. {solution}")
            
            print(f"{'='*60}\n")
            
            # Uyarı gönderildi olarak işaretle
            self.mark_alert_sent(enhanced_analysis)
    
    def mark_alert_sent(self, enhanced_analysis: Dict):
        """Uyarı gönderildi olarak işaretle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE monitoring_log 
            SET alert_sent = 1 
            WHERE timestamp >= datetime('now', '-1 hour')
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_realtime_report(self, enhanced_analysis: Dict):
        """Gerçek zamanlı rapor oluştur"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n📊 GERÇEK ZAMANLI RAPOR - {timestamp}")
        print("="*50)
        
        # Yeni yorumlar
        new_count = enhanced_analysis.get('new_comments_count', 0)
        if new_count > 0:
            print(f"📝 {new_count} yeni yorum işlendi")
            
            # Öncelik kategorileri
            priority_results = enhanced_analysis.get('priority_results', {})
            if 'critical_issues' in priority_results:
                print(f"\n🎯 ÖNCELİK SKORLARI:")
                for category, data in priority_results['critical_issues'].items():
                    score = data['priority_score']
                    emoji = "🔴" if score >= 80 else "🟡" if score >= 60 else "🔵"
                    print(f"   {emoji} {category.upper()}: {score:.1f}/100")
            
            # Harici çözümler
            external_solutions = enhanced_analysis['analysis_results'].get('external_solutions', {})
            if external_solutions:
                print(f"\n💡 HARİCİ ÇÖZÜM ÖNERİLERİ:")
                for category, solutions in external_solutions.items():
                    print(f"   📋 {category.upper()}:")
                    for solution in solutions[:1]:  # Sadece ilk öneriyi göster
                        print(f"      • {solution}")
        else:
            print("😴 Yeni yorum bulunamadı")
        
        print("="*50)
    
    def start_monitoring(self):
        """Gerçek zamanlı izlemeyi başlat"""
        self.is_running = True
        print("🚀 Basit Gerçek Zamanlı İzleme Başlatıldı!")
        print(f"⏰ Kontrol aralığı: {self.check_interval} saniye")
        print("⏹️ Durdurmak için Ctrl+C basın")
        
        try:
            while self.is_running:
                # 1. Yeni yorumları kontrol et
                new_comments = self.check_for_new_comments()
                
                if new_comments:
                    # 2. Mock RAG ile analiz
                    enhanced_analysis = self.analyze_with_mock_rag(new_comments)
                    
                    # 3. Sistem istatistiklerini güncelle
                    self.update_system_stats(enhanced_analysis)
                    
                    # 4. Rapor oluştur
                    self.generate_realtime_report(enhanced_analysis)
                    
                    # 5. Gerekirse uyarı gönder
                    self.send_alert_if_needed(enhanced_analysis)
                else:
                    # Boş kontrol
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Yeni yorum yok")
                
                # Bekle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ İzleme durduruldu")
            self.is_running = False
    
    def get_system_summary(self):
        """Sistem özetini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Son istatistikleri al
        cursor.execute('SELECT * FROM system_stats ORDER BY id DESC LIMIT 1')
        last_stats = cursor.fetchone()
        
        # Log sayısını al
        cursor.execute('SELECT COUNT(*) FROM monitoring_log')
        total_logs = cursor.fetchone()[0]
        
        # Uyarı sayısını al
        cursor.execute('SELECT COUNT(*) FROM monitoring_log WHERE alert_sent = 1')
        alert_count = cursor.fetchone()[0]
        
        conn.close()
        
        if last_stats:
            print(f"\n📊 SİSTEM ÖZETİ")
            print(f"📝 Toplam İzlenen Yorum: {total_logs}")
            print(f"🚨 Gönderilen Uyarı: {alert_count}")
            print(f"⏰ Son Kontrol: {last_stats[3]}")
            print(f"📊 Son Durum: {last_stats[4]}")
        else:
            print("📊 Henüz istatistik bulunmuyor")

def main():
    """Basit gerçek zamanlı demo"""
    
    print("🚀 BASİT GERÇEK ZAMANLI İZLEME SİSTEMİ")
    print("📊 Mock RAG + Otomatik Uyarı + SQLite")
    print("="*60)
    
    monitor = SimpleRealTimeMonitor(check_interval=5)  # 5 saniye test için
    
    print("\n🔍 Hangi modu çalıştırmak istiyorsunuz?")
    print("1. 🔄 Gerçek Zamanlı İzleme (5 saniye aralık)")
    print("2. 📊 Sistem Özeti")
    print("3. 🧪 Mock RAG Testi")
    print("4. 🗑️ Veritabanını Temizle")
    print("5. 🚪 Çıkış")
    
    choice = input("\nSeçiminiz (1-5): ").strip()
    
    if choice == '1':
        monitor.start_monitoring()
    
    elif choice == '2':
        monitor.get_system_summary()
    
    elif choice == '3':
        print("\n🧪 Mock RAG sistemi test ediliyor...")
        
        # Test yorumları
        test_comments = monitor.load_current_comments()[:3]
        
        if test_comments:
            enhanced_analysis = monitor.analyze_with_mock_rag(test_comments)
            
            print(f"✅ {len(test_comments)} yorum analiz edildi")
            
            # Mock RAG sonuçlarını göster
            external_solutions = enhanced_analysis['analysis_results'].get('external_solutions', {})
            if external_solutions:
                print(f"\n💡 MOCK RAG ÇÖZÜMLERİ:")
                for category, solutions in external_solutions.items():
                    print(f"\n📋 {category.upper()} için öneriler:")
                    for i, solution in enumerate(solutions, 1):
                        print(f"   {i}. {solution}")
            else:
                print("❌ Mock RAG çözümü bulunamadı")
        else:
            print("❌ Test yorumu bulunamadı")
    
    elif choice == '4':
        # Veritabanını temizle
        Path(monitor.db_path).unlink(missing_ok=True)
        print("🗑️ Veritabanı temizlendi")
        monitor.init_database()
    
    elif choice == '5':
        print("👋 Sistem kapatılıyor...")
    
    else:
        print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main() 