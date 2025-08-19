# 🚀 Deployment Guide - Render & Railway

Bu rehber, Trendyol RAG sistemini Render veya Railway üzerinde Selenium desteği ile deploy etmek için adım adım talimatları içerir.

## 📋 Platform Karşılaştırması

| Özellik | Render | Railway |
|---------|--------|---------|
| **Selenium Desteği** | ✅ Tam destek | ✅ Tam destek |
| **Chrome Kurulumu** | ✅ Otomatik | ✅ Otomatik |
| **Ücretsiz Plan** | ✅ 750 saat/ay | ✅ $5 kredi/ay |
| **Build Time** | ~5-10 dakika | ~3-5 dakika |
| **Deploy Süreci** | Basit | Basit |

## 🎯 Render Deployment

### Adım 1: Render Hesabı Oluştur
1. [Render.com](https://render.com) adresine gidin
2. GitHub hesabınızla giriş yapın
3. "New +" > "Web Service" seçin

### Adım 2: Repository Bağla
1. GitHub repository'nizi seçin
2. Branch: `main` (veya `master`)
3. Root Directory: `/` (boş bırakın)

### Adım 3: Build Ayarları
```
Build Command: pip install -r requirements.txt
Start Command: streamlit run comprehensive_rag_streamlit.py --server.port $PORT --server.address 0.0.0.0
```

### Adım 4: Environment Variables
```
PYTHON_VERSION=3.9.16
CHROME_BIN=/usr/bin/google-chrome
CHROME_DRIVER_PATH=/usr/bin/chromedriver
```

### Adım 5: Deploy
1. "Create Web Service" butonuna tıklayın
2. Build sürecini bekleyin (5-10 dakika)
3. URL'nizi alın: `https://your-app-name.onrender.com`

## 🚂 Railway Deployment

### Adım 1: Railway Hesabı Oluştur
1. [Railway.app](https://railway.app) adresine gidin
2. GitHub hesabınızla giriş yapın
3. "New Project" > "Deploy from GitHub repo"

### Adım 2: Repository Seç
1. Repository'nizi seçin
2. "Deploy Now" butonuna tıklayın

### Adım 3: Otomatik Konfigürasyon
- `railway.json` ve `nixpacks.toml` dosyaları otomatik olarak Chrome'u kuracak
- Build süreci 3-5 dakika sürecek

### Adım 4: Domain Ayarla
1. "Settings" > "Domains"
2. Custom domain ekleyin veya Railway domain'ini kullanın

## 🔧 Selenium Cloud Optimizasyonları

### Chrome Options (Otomatik)
```python
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
```

### Environment Variables
```bash
CHROME_BIN=/usr/bin/google-chrome
CHROME_DRIVER_PATH=/usr/bin/chromedriver
```

## 📊 Deployment Sonrası Test

### 1. Ana Sayfa Kontrolü
- URL'ye gidin
- Streamlit arayüzü yüklenmeli
- "Initialize RAG System" butonu çalışmalı

### 2. Selenium Test
- "Data Management" sekmesine gidin
- "Start Scraping" butonuna tıklayın
- Trendyol URL'si girin
- Yorumlar çekilmeli

### 3. RAG Sistemi Test
- "Chat Interface" sekmesine gidin
- Soru sorun
- AI yanıt vermeli

## 🚨 Sorun Giderme

### Build Hatası
```
Error: Chrome installation failed
```
**Çözüm:** Build loglarını kontrol edin, genellikle internet bağlantısı sorunu

### Selenium Hatası
```
Chrome driver not found
```
**Çözüm:** Environment variables doğru ayarlanmış mı kontrol edin

### Memory Hatası
```
Out of memory
```
**Çözüm:** Render'da "Standard" plana geçin (1GB RAM)

### Timeout Hatası
```
Build timeout
```
**Çözüm:** Railway'de build timeout'u artırın

## 💰 Maliyet Analizi

### Render
- **Free Plan:** 750 saat/ay (yaklaşık 31 gün)
- **Standard Plan:** $7/ay (1GB RAM, daha hızlı)

### Railway
- **Free Plan:** $5 kredi/ay
- **Pro Plan:** $20/ay (sınırsız)

## 🔄 Otomatik Deploy

### GitHub Actions (Opsiyonel)
```yaml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v1.0.0
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

## 📱 Mobile Uyumluluk

Streamlit otomatik olarak mobile uyumlu, ancak:
- Chrome headless modda çalışır
- Touch events desteklenmez
- Responsive design mevcut

## 🔒 Güvenlik

### Environment Variables
- API key'leri environment variable olarak saklayın
- `.env` dosyasını commit etmeyin
- Production'da HTTPS kullanın

### Rate Limiting
- Trendyol API çağrılarını sınırlayın
- User input validation yapın
- SQL injection koruması mevcut

## 📈 Monitoring

### Render Dashboard
- Real-time logs
- Performance metrics
- Error tracking

### Railway Dashboard
- Build logs
- Deploy history
- Resource usage

## 🎉 Başarı Kriterleri

✅ Selenium scraper çalışıyor  
✅ RAG sistemi yanıt veriyor  
✅ CSV upload çalışıyor  
✅ Chat interface aktif  
✅ Mobile uyumlu  

## 📞 Destek

Sorun yaşarsanız:
1. Build loglarını kontrol edin
2. Environment variables'ları doğrulayın
3. Chrome path'lerini kontrol edin
4. Memory limitlerini kontrol edin

---

**Not:** Bu deployment yapılandırması Selenium'i tam destekler ve Streamlit Cloud'daki kısıtlamaları aşar. 