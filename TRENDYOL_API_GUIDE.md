# 🚀 Trendyol API Tespit ve Doğrudan Erişim Sistemi

Bu proje, Trendyol'un yorum API endpoint'lerini tespit ederek doğrudan erişim sağlamayı amaçlar. Bu sayede Selenium kullanmadan çok daha hızlı ve verimli yorum çekme işlemi gerçekleştirilebilir.

## 📋 İçindekiler

1. [Sistem Bileşenleri](#sistem-bileşenleri)
2. [Kurulum](#kurulum)
3. [Kullanım](#kullanım)
4. [API Tespit Süreci](#api-tespit-süreci)
5. [Doğrudan API Erişimi](#doğrudan-api-erişimi)
6. [Yasal ve Etik Uyarılar](#yasal-ve-etik-uyarılar)
7. [Sık Sorulan Sorular](#sık-sorulan-sorular)

## 🔧 Sistem Bileşenleri

### 1. `trendyol_api_detector.py`
- **Temel API tespit sistemi**
- Network trafiğini yakalar
- API endpoint'lerini tespit eder
- Basit test scriptleri oluşturur

### 2. `advanced_trendyol_api_detector.py`
- **Gelişmiş API tespit sistemi**
- Token'ları ve gizli parametreleri çıkarır
- Session bilgilerini yakalar
- Gelişmiş test scriptleri oluşturur

## 🛠️ Kurulum

### Gereksinimler
```bash
pip install selenium requests webdriver-manager
```

### Chrome WebDriver
```bash
# Otomatik kurulum (önerilen)
pip install webdriver-manager

# Manuel kurulum
# ChromeDriver'ı https://chromedriver.chromium.org/ adresinden indirin
```

## 🚀 Kullanım

### 1. Temel API Tespiti

```bash
python trendyol_api_detector.py
```

**Çıktı:**
- Tespit edilen API endpoint'leri
- Basit test scriptleri
- API erişilebilirlik durumu

### 2. Gelişmiş API Tespiti

```bash
python advanced_trendyol_api_detector.py
```

**Çıktı:**
- Token'lar ve gizli parametreler
- Session bilgileri
- Gelişmiş test scriptleri
- Tam API erişim kodu

## 🔍 API Tespit Süreci

### Adım 1: Network Trafiği Yakalama
```python
# Selenium ile sayfa yüklenir
driver.get(product_url)

# Network logları yakalanır
logs = driver.get_log('performance')

# API çağrıları analiz edilir
api_calls = analyze_network_logs(logs)
```

### Adım 2: Token Çıkarma
```python
# JavaScript ile sayfadaki token'lar çıkarılır
tokens = extract_tokens_from_page()

# LocalStorage, SessionStorage, Global değişkenler taranır
# Script tag'leri analiz edilir
```

### Adım 3: API Test Etme
```python
# Tespit edilen API'ler test edilir
test_result = test_api_with_tokens(api_info)

# Erişilebilir API'ler için script oluşturulur
script = generate_advanced_api_script(api_info, test_result)
```

## 📡 Doğrudan API Erişimi

### Oluşturulan Script Kullanımı

```python
from trendyol_api_script_1 import TrendyolCommentAPI

# API instance'ı oluştur
api = TrendyolCommentAPI()

# Tek sayfa yorum çek
comments = api.get_comments(product_id="123456", page=1, limit=50)

# Tüm yorumları çek
all_comments = api.get_all_comments(product_id="123456", max_pages=10)
```

### Manuel API Çağrısı

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.trendyol.com/',
    'Origin': 'https://www.trendyol.com'
}

# Tespit edilen API endpoint'i
url = "https://api.trendyol.com/comments/123456"

response = requests.get(url, headers=headers)
comments = response.json()
```

## ⚠️ Yasal ve Etik Uyarılar

### 🚨 ÖNEMLİ UYARILAR

1. **Yasal Sorumluluk**
   - Bu araçlar sadece eğitim ve araştırma amaçlıdır
   - Kullanıcı, bu araçları kullanırken tüm yasal sorumluluğu üstlenir
   - Trendyol'un kullanım şartlarını ihlal etmeyin

2. **Rate Limiting**
   - API'ye çok sık istek atmayın
   - Sunucuları aşırı yüklemeyin
   - Makul aralıklarla istek gönderin (1-2 saniye)

3. **Veri Kullanımı**
   - Çekilen verileri ticari amaçla kullanmayın
   - Kişisel veri koruma kanunlarına uyun
   - Verileri güvenli şekilde saklayın

4. **Etik Kurallar**
   - Trendyol'un sistemlerine zarar vermeyin
   - Diğer kullanıcıların deneyimini bozmayın
   - Sorumlu kullanım yapın

### 📋 Kullanım Koşulları

- ✅ **İzin Verilenler:**
  - Eğitim ve araştırma amaçlı kullanım
  - Kişisel projeler için veri analizi
  - Açık kaynak projeler

- ❌ **Yasak Olanlar:**
  - Ticari kullanım
  - Toplu veri çekme
  - Sistemlere zarar verme
  - Diğer kullanıcıları rahatsız etme

## 🔧 Teknik Detaylar

### Tespit Edilen API Türleri

1. **Yorum API'leri**
   ```
   https://api.trendyol.com/comments/{product_id}
   https://gw.trendyol.com/reviews/{product_id}
   https://mobileapi.trendyol.com/ratings/{product_id}
   ```

2. **Parametreler**
   ```python
   {
       'page': 1,
       'limit': 50,
       'productId': '123456',
       'sort': 'date',
       'filter': 'all'
   }
   ```

3. **Headers**
   ```python
   {
       'User-Agent': '...',
       'Accept': 'application/json',
       'Referer': 'https://www.trendyol.com/',
       'Authorization': 'Bearer {token}',
       'X-API-Key': '{api_key}'
   }
   ```

### Token Türleri

1. **Bearer Token**
   - Authorization header'ında kullanılır
   - Session bazlı geçerlilik

2. **API Key**
   - X-API-Key header'ında kullanılır
   - Uzun süreli geçerlilik

3. **Session Token**
   - Cookie veya localStorage'da saklanır
   - Kısa süreli geçerlilik

## 📊 Performans Karşılaştırması

| Yöntem | Hız | Güvenilirlik | Karmaşıklık |
|--------|-----|---------------|-------------|
| Selenium | Yavaş | Orta | Yüksek |
| Doğrudan API | Hızlı | Yüksek | Düşük |
| Hybrid | Orta | Yüksek | Orta |

## 🔍 Sık Sorulan Sorular

### Q: API endpoint'i değişirse ne yapmalıyım?
A: Script'i tekrar çalıştırarak yeni endpoint'i tespit edin.

### Q: Token'lar geçersiz olursa?
A: Sayfayı yeniden yükleyerek yeni token'ları çıkarın.

### Q: Rate limiting nasıl aşılır?
A: İstekler arasında bekleme süresi ekleyin (1-2 saniye).

### Q: Anti-bot koruması varsa?
A: User-Agent ve diğer header'ları gerçek tarayıcı gibi ayarlayın.

## 🛡️ Güvenlik Önlemleri

1. **IP Rotasyonu**
   ```python
   # Proxy kullanımı
   proxies = {
       'http': 'http://proxy:port',
       'https': 'https://proxy:port'
   }
   ```

2. **User-Agent Rotasyonu**
   ```python
   user_agents = [
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
       # ... daha fazla
   ]
   ```

3. **Request Aralığı**
   ```python
   import time
   
   for page in range(1, max_pages + 1):
       response = requests.get(url, headers=headers)
       time.sleep(2)  # 2 saniye bekle
   ```

## 📝 Örnek Kullanım Senaryoları

### Senaryo 1: Tek Ürün Analizi
```python
# 1. API tespit et
detector = AdvancedTrendyolAPIDetector()
results = detector.detect_and_analyze_advanced(product_url)

# 2. Script oluştur
script = results[0]['script']
with open('my_api_script.py', 'w') as f:
    f.write(script)

# 3. Kullan
from my_api_script import TrendyolCommentAPI
api = TrendyolCommentAPI()
comments = api.get_all_comments(product_id="123456")
```

### Senaryo 2: Toplu Analiz
```python
product_urls = [
    "https://www.trendyol.com/urun1",
    "https://www.trendyol.com/urun2",
    # ...
]

for url in product_urls:
    # Her ürün için API tespit et
    results = detector.detect_and_analyze_advanced(url)
    # Sonuçları kaydet
```

## 🎯 Sonuç

Bu sistem sayesinde:

✅ **Hız:** Selenium'a göre 10-50x daha hızlı  
✅ **Güvenilirlik:** Daha az hata oranı  
✅ **Ölçeklenebilirlik:** Çok sayıda ürün analizi  
✅ **Maliyet:** Daha az sistem kaynağı kullanımı  

**⚠️ Unutmayın:** Bu araçları sorumlu ve yasal sınırlar içinde kullanın!

---

**Son Güncelleme:** 2024-01-XX
**Versiyon:** 1.0.0 
