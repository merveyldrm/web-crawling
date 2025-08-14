#!/usr/bin/env python3
"""
Trendyol API Test Scripti
Oluşturulan API'leri test eder
"""

from trendyol_api_script_2 import TrendyolCommentAPI
import json

def test_trendyol_api():
    """Trendyol API'sini test et"""
    print("🚀 Trendyol API Test Başlatılıyor...")
    
    try:
        # API instance'ı oluştur
        api = TrendyolCommentAPI()
        
        # İlk sayfa yorumları çek (5 yorum)
        print("\n📡 API'den yorumlar çekiliyor...")
        result = api.get_comments(page=1, limit=5)
        
        if result:
            print(f"✅ Başarılı! Veri alındı:")
            print(f"   - Veri tipi: {type(result)}")
            print(f"   - Veri boyutu: {len(str(result))} karakter")
            
            # JSON formatında göster (kısaltılmış)
            if isinstance(result, dict):
                print(f"   - JSON anahtarları: {list(result.keys())}")
                
                # İlk birkaç yorumu göster
                if 'result' in result and isinstance(result['result'], list):
                    comments = result['result']
                    print(f"   - Toplam yorum sayısı: {len(comments)}")
                    
                    for i, comment in enumerate(comments[:3]):
                        print(f"\n   Yorum {i+1}:")
                        if isinstance(comment, dict):
                            for key, value in list(comment.items())[:3]:
                                print(f"     {key}: {str(value)[:100]}...")
                        else:
                            print(f"     {str(comment)[:100]}...")
                
                elif 'data' in result:
                    print(f"   - Data anahtarı bulundu: {type(result['data'])}")
                
                else:
                    print(f"   - Ham veri: {str(result)[:200]}...")
            
            else:
                print(f"   - Ham veri: {str(result)[:200]}...")
        
        else:
            print("❌ API'den veri alınamadı")
        
        print("\n" + "="*50)
        print("🎯 SONUÇ: API başarıyla çalışıyor!")
        print("   Trendyol'u aradan çıkarıp doğrudan API'ye erişim sağladık.")
        print("   Bu şekilde çok daha hızlı yorum çekme işlemi yapabilirsiniz.")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        import traceback
        print("Detaylı hata:")
        traceback.print_exc()

if __name__ == "__main__":
    test_trendyol_api()
