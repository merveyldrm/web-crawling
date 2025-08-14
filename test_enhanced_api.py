#!/usr/bin/env python3
"""
Gelişmiş Trendyol API Test Scripti
1000+ yorum çekme sistemini test eder
"""

from enhanced_trendyol_api import EnhancedTrendyolAPI
import time

def test_enhanced_api():
    """Gelişmiş API sistemini test et"""
    print("🚀 Gelişmiş Trendyol API Test Sistemi")
    print("=" * 60)
    
    # Test URL'si
    test_url = input("Trendyol ürün URL'sini girin: ").strip()
    
    if not test_url:
        # Örnek URL kullan
        test_url = "https://www.trendyol.com/zuhre-ana/karadut-ozu-670-gr-p-712245449?boutiqueId=61&merchantId=985455"
        print(f"Örnek URL kullanılıyor: {test_url}")
    
    # Hedef yorum sayısını al
    target_input = input("Hedef yorum sayısını girin (varsayılan: 1000): ").strip()
    target_count = int(target_input) if target_input else 1000
    
    print(f"\n🎯 Test Başlatılıyor...")
    print(f"   URL: {test_url}")
    print(f"   Hedef: {target_count} yorum")
    print("-" * 60)
    
    # API instance'ı oluştur
    api = EnhancedTrendyolAPI()
    
    try:
        # Başlangıç zamanını kaydet
        start_time = time.time()
        
        # Yorumları çek
        reviews = api.get_all_reviews(test_url, target_count=target_count)
        
        # Bitiş zamanını kaydet
        end_time = time.time()
        duration = end_time - start_time
        
        if reviews:
            print(f"\n✅ BAŞARILI!")
            print(f"   - Çekilen yorum: {len(reviews)}")
            print(f"   - Geçen süre: {duration:.2f} saniye")
            print(f"   - Hız: {len(reviews)/duration:.1f} yorum/saniye")
            
            # Analiz et
            api.analyze_reviews(reviews)
            
            # CSV'ye kaydet
            api.save_reviews_to_csv(reviews)
            
            print(f"\n🎉 Test tamamlandı!")
            print(f"   {len(reviews)} yorum başarıyla çekildi ve kaydedildi.")
            
            # Performans karşılaştırması
            print(f"\n📊 Performans Karşılaştırması:")
            print(f"   - Selenium (eski): ~30 saniye/100 yorum")
            print(f"   - API (yeni): {duration:.2f} saniye/{len(reviews)} yorum")
            
            if duration > 0:
                speedup = (30 * len(reviews) / 100) / duration
                print(f"   - Hız artışı: {speedup:.1f}x daha hızlı")
        
        else:
            print("❌ Hiç yorum çekilemedi")
    
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {e}")
        import traceback
        print("Detaylı hata:")
        traceback.print_exc()

def compare_methods():
    """Farklı yöntemleri karşılaştır"""
    print("\n📊 Yöntem Karşılaştırması:")
    print("=" * 40)
    
    methods = [
        {
            "name": "Selenium (Eski)",
            "speed": "Yavaş",
            "reliability": "Orta",
            "max_comments": "100-200",
            "bot_detection": "Yüksek risk"
        },
        {
            "name": "API (Yeni)",
            "speed": "Hızlı",
            "reliability": "Yüksek",
            "max_comments": "1000+",
            "bot_detection": "Düşük risk"
        }
    ]
    
    for method in methods:
        print(f"\n🔹 {method['name']}:")
        print(f"   - Hız: {method['speed']}")
        print(f"   - Güvenilirlik: {method['reliability']}")
        print(f"   - Maksimum yorum: {method['max_comments']}")
        print(f"   - Bot tespiti: {method['bot_detection']}")

def show_usage_tips():
    """Kullanım ipuçları göster"""
    print("\n💡 Kullanım İpuçları:")
    print("=" * 30)
    
    tips = [
        "🎯 Hedef yorum sayısını 1000+ olarak ayarlayın",
        "⏱️ Rate limiting için 1-2 saniye bekleme süresi kullanın",
        "📊 Büyük veri setleri için CSV formatını tercih edin",
        "🔄 Farklı API endpoint'lerini deneyin",
        "📈 Performans için paralel işlem kullanın"
    ]
    
    for tip in tips:
        print(f"   {tip}")

def main():
    """Ana fonksiyon"""
    print("🚀 Gelişmiş Trendyol API Test Sistemi")
    print("=" * 60)
    
    while True:
        print("\nSeçenekler:")
        print("1. API Testi Çalıştır")
        print("2. Yöntem Karşılaştırması")
        print("3. Kullanım İpuçları")
        print("4. Çıkış")
        
        choice = input("\nSeçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            test_enhanced_api()
        elif choice == "2":
            compare_methods()
        elif choice == "3":
            show_usage_tips()
        elif choice == "4":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim! Lütfen 1-4 arası bir sayı girin.")

if __name__ == "__main__":
    main()
