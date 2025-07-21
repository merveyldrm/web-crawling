# Trendyol Yorum Analizi

Bu proje, Trendyol ürün yorumlarını çekip analiz eden bir web uygulamasıdır.

## Özellikler

- Trendyol ürün URL'sinden yorumları otomatik çekme
- En az 100 yorum toplama
- AI destekli yorum analizi
- Artı/eksi özellikler ayrımı
- Kategorik analiz (kalite, kargo, fiyat)
- Opsiyonel beden/uyum ve renk/model analizi
- CSV ve TXT formatında indirme

## Kurulum

1. Python 3.7+ yüklü olmalıdır
2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Chrome WebDriver'ı yükleyin (Selenium için gerekli)

## Kullanım

1. Uygulamayı başlatın:
```bash
python app.py
```

2. Tarayıcınızda `http://localhost:5000` adresine gidin

3. Trendyol ürün URL'sini girin ve "Yorumları Çek" butonuna tıklayın

4. Yorumlar çekildikten sonra:
   - CSV dosyasını indirin
   - "Analiz Et" butonuyla AI özeti oluşturun
   - Özet dosyasını indirin

## Dosya Yapısı

- `app.py` - Flask web uygulaması
- `trendyol_selenium_scraper.py` - Yorum çekme modülü
- `comment_summarizer.py` - Yorum analiz modülü
- `templates/index.html` - Web arayüzü
- `requirements.txt` - Gerekli paketler

## Notlar

- Uygulama headless modda Chrome kullanır
- Yorum çekme işlemi birkaç dakika sürebilir
- En az 100 yorum toplanmaya çalışılır
- Tekstil ürünleri için beden/uyum analizi otomatik yapılır
