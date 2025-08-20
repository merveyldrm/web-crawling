import requests
import json

# API sunucunuzun adresi
API_URL = "http://127.0.0.1:8000/scrape/"

# Test edilecek örnek bir Trendyol ürün URL'si
# Lütfen bunu test etmek istediğiniz gerçek bir URL ile değiştirin
PRODUCT_URL = "https://www.trendyol.com/pull-bear/siyah-regular-fit-bisiklet-yaka-uzun-kollu-sweatshirt-05741502-p-87732358"

# API'ye gönderilecek veri
# min_comments'i test için düşük bir sayıda tutalım
payload = {
    "product_url": PRODUCT_URL,
    "min_comments": 10 # Test sırasında hızlı sonuç almak için düşük bir değer
}

print(f"API'ye istek gönderiliyor: {API_URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    # API'ye POST isteği gönder
    response = requests.post(API_URL, json=payload, timeout=600) # Kazıma işlemi uzun sürebilir, timeout'u yüksek tutalım

    # Yanıtın durum kodunu kontrol et
    response.raise_for_status()  # HTTP 2xx dışında bir kod varsa hata fırlatır

    # Başarılı yanıtı işle
    print("\n--- API Yanıtı ---")
    print(f"Durum Kodu: {response.status_code}")
    
    # Gelen JSON verisini formatlı bir şekilde yazdır
    response_data = response.json()
    print(json.dumps(response_data, indent=2, ensure_ascii=False))
    
    # Yorum sayısını kontrol et
    if 'comments' in response_data and response_data['comments']:
        print(f"\nBaşarıyla {len(response_data['comments'])} adet yorum alındı.")
    else:
        print("\nAPI'den yorum alınamadı veya bir hata oluştu.")

except requests.exceptions.HTTPError as http_err:
    print(f"\nHTTP Hatası: {http_err}")
    print(f"Yanıt İçeriği: {response.text}")
except requests.exceptions.RequestException as err:
    print(f"\nBir Hata Oluştu: {err}")

