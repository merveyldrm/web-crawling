#!/usr/bin/env python3
"""
Trendyol API Tespit Sistemi - Test Scripti
Bu script, API tespit sistemini test etmek için kullanılır.
"""

import sys
import os
from advanced_trendyol_api_detector import AdvancedTrendyolAPIDetector

def test_api_detection():
    """API tespit sistemini test et"""
    print("=== Trendyol API Tespit Sistemi Test ===")
    print("Bu test, Trendyol'un yorum API endpoint'lerini tespit eder.")
    print()
    
    # Test URL'si (örnek)
    test_url = input("Trendyol ürün URL'sini girin (veya Enter'a basın): ").strip()
    
    if not test_url:
        # Örnek URL kullan
        test_url = "https://www.trendyol.com/trendyol-man/trendyol-man-erkek-beyaz-basic-tshirt-p-12345678"
        print(f"Örnek URL kullanılıyor: {test_url}")
    
    print(f"\nTest URL: {test_url}")
    print("API tespit işlemi başlatılıyor...")
    print("-" * 50)
    
    try:
        # Detector oluştur
        detector = AdvancedTrendyolAPIDetector()
        
        # API'leri tespit et
        results = detector.detect_and_analyze_advanced(test_url)
        
        if results:
            print(f"\n✅ Başarılı! {len(results)} API endpoint'i tespit edildi.")
            
            for i, result in enumerate(results):
                print(f"\n--- API {i+1} ---")
                print(f"URL: {result['api_info']['url']}")
                print(f"Status: {'✅ Erişilebilir' if result['test_result']['success'] else '❌ Erişilemez'}")
                
                if result['test_result']['success']:
                    print(f"Response Size: {result['test_result']['size']} bytes")
                    
                    # Token'ları göster
                    if result['tokens']:
                        print("Bulunan Token'lar:")
                        for key, value in result['tokens'].items():
                            masked_value = value[:20] + "..." if len(str(value)) > 20 else value
                            print(f"  {key}: {masked_value}")
                    
                    # Script dosyasını kaydet
                    filename = f"trendyol_api_script_{i+1}.py"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result['script'])
                    print(f"Script kaydedildi: {filename}")
                    
                    # Kullanım örneği göster
                    print("\nKullanım örneği:")
                    print(f"from {filename.replace('.py', '')} import TrendyolCommentAPI")
                    print("api = TrendyolCommentAPI()")
                    print("comments = api.get_all_comments(product_id='PRODUCT_ID')")
                else:
                    print(f"Hata: {result['test_result']['error']}")
        else:
            print("❌ Hiç API endpoint'i tespit edilemedi.")
            print("Olası nedenler:")
            print("- Sayfa yüklenemedi")
            print("- Anti-bot koruması aktif")
            print("- Network trafiği yakalanamadı")
            print("- API endpoint'i değişmiş olabilir")
        
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {e}")
        print("\nHata ayıklama önerileri:")
        print("1. Chrome tarayıcısının yüklü olduğundan emin olun")
        print("2. İnternet bağlantınızı kontrol edin")
        print("3. URL'nin doğru olduğundan emin olun")
        print("4. Gerekli paketlerin yüklü olduğunu kontrol edin")
    
    finally:
        try:
            detector.close()
        except:
            pass

def show_usage_example():
    """Kullanım örneği göster"""
    print("\n=== Kullanım Örneği ===")
    print("""
# 1. API tespit et
detector = AdvancedTrendyolAPIDetector()
results = detector.detect_and_analyze_advanced("https://www.trendyol.com/urun-url")

# 2. Script'i kullan
from trendyol_api_script_1 import TrendyolCommentAPI
api = TrendyolCommentAPI()

# 3. Yorumları çek
comments = api.get_all_comments(product_id="123456", max_pages=5)

# 4. Sonuçları işle
for comment in comments:
    print(f"Yorum: {comment}")
    """)

def show_legal_warning():
    """Yasal uyarıları göster"""
    print("\n=== ⚠️ YASAL UYARILAR ===")
    print("""
1. Bu araçlar sadece eğitim ve araştırma amaçlıdır
2. Trendyol'un kullanım şartlarını ihlal etmeyin
3. Rate limiting uygulayın (1-2 saniye bekleme)
4. Verileri ticari amaçla kullanmayın
5. Sistemlere zarar vermeyin
6. Sorumlu kullanım yapın

Bu araçları kullanırken tüm yasal sorumluluğu üstlenirsiniz.
    """)

def main():
    """Ana fonksiyon"""
    print("🚀 Trendyol API Tespit Sistemi")
    print("=" * 50)
    
    while True:
        print("\nSeçenekler:")
        print("1. API Tespit Testi")
        print("2. Kullanım Örneği")
        print("3. Yasal Uyarılar")
        print("4. Çıkış")
        
        choice = input("\nSeçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            test_api_detection()
        elif choice == "2":
            show_usage_example()
        elif choice == "3":
            show_legal_warning()
        elif choice == "4":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim! Lütfen 1-4 arası bir sayı girin.")

if __name__ == "__main__":
    main() 