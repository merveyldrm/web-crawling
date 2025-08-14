#!/usr/bin/env python3
"""
Gelişmiş Trendyol API Scripti
1000+ yorum çekebilen optimize edilmiş sistem
"""

import requests
import json
import time
import csv
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class EnhancedTrendyolAPI:
    def __init__(self):
        self.session = requests.Session()
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Referer': 'https://www.trendyol.com/',
            'Origin': 'https://www.trendyol.com'
        }
        self.session.headers.update(self.base_headers)
        
        # API endpoint'leri
        self.api_endpoints = {
            'reviews': 'https://apigw.trendyol.com/discovery-web-socialgw-service/reviews',
            'product_reviews': 'https://apigw.trendyol.com/discovery-web-websfxsocialreviewrating-santral/product-reviews-detailed',
            'review_likes': 'https://apigw.trendyol.com/discovery-web-socialgw-service/api/review-like/filter'
        }
        
        # Rate limiting
        self.request_delay = 1.0  # saniye
        self.max_retries = 3
        
    def extract_product_info(self, url):
        """URL'den ürün bilgilerini çıkar"""
        try:
            # URL'yi parse et
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            # Ürün ID'sini bul
            product_id = None
            for part in path_parts:
                if part.startswith('p-'):
                    product_id = part.replace('p-', '')
                    break
            
            # Seller ID'sini URL'den çıkar
            seller_id = None
            query_params = parse_qs(parsed.query)
            if 'merchantId' in query_params:
                seller_id = query_params['merchantId'][0]
            elif 'boutiqueId' in query_params:
                seller_id = query_params['boutiqueId'][0]
            
            return {
                'product_id': product_id,
                'seller_id': seller_id,
                'url': url
            }
        except Exception as e:
            print(f"URL parse hatası: {e}")
            return None
    
    def get_reviews_via_api(self, product_info, page=1, limit=50):
        """API üzerinden yorumları çek"""
        try:
            # API endpoint'i
            url = f"{self.api_endpoints['product_reviews']}"
            
            # Parametreler
            params = {
                'sellerId': product_info['seller_id'],
                'contentId': product_info['product_id'],
                'page': page,
                'order': 'DESC',
                'orderBy': 'Score',
                'channelId': 1
            }
            
            # İstek gönder
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API çağrısı hatası: {e}")
            return None
    
    def get_reviews_via_web(self, product_info, page=1):
        """Web sayfası üzerinden yorumları çek"""
        try:
            # Yorumlar sayfası URL'si
            reviews_url = f"{product_info['url']}/yorumlar"
            
            # Parametreler
            params = {
                'boutiqueId': product_info['seller_id'],
                'merchantId': product_info['seller_id'],
                'page': page
            }
            
            # İstek gönder
            response = self.session.get(reviews_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Web API Hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Web API çağrısı hatası: {e}")
            return None
    
    def parse_reviews_data(self, data):
        """API yanıtından yorumları parse et"""
        reviews = []
        
        try:
            if isinstance(data, dict):
                # Farklı API yanıt formatlarını kontrol et
                if 'result' in data and isinstance(data['result'], dict):
                    # HTML içeriği varsa parse et
                    html_content = data['result'].get('html', '')
                    if html_content:
                        reviews = self.parse_html_reviews(html_content)
                
                elif 'data' in data and isinstance(data['data'], list):
                    reviews = data['data']
                
                elif 'reviews' in data and isinstance(data['reviews'], list):
                    reviews = data['reviews']
                
                elif 'items' in data and isinstance(data['items'], list):
                    reviews = data['items']
                
                else:
                    # Ham veriyi kontrol et
                    reviews = self.extract_reviews_from_raw_data(data)
            
            return reviews
            
        except Exception as e:
            print(f"Veri parse hatası: {e}")
            return []
    
    def parse_html_reviews(self, html_content):
        """HTML içeriğinden yorumları çıkar"""
        reviews = []
        
        try:
            # Basit HTML parsing (gerçek uygulamada BeautifulSoup kullanılabilir)
            import re
            
            # Yorum pattern'leri
            comment_patterns = [
                r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*review[^"]*"[^>]*>(.*?)</div>',
                r'<p[^>]*class="[^"]*comment-text[^"]*"[^>]*>(.*?)</p>'
            ]
            
            for pattern in comment_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    # HTML tag'lerini temizle
                    clean_text = re.sub(r'<[^>]+>', '', match).strip()
                    if clean_text and len(clean_text) > 10:
                        reviews.append({
                            'comment': clean_text,
                            'source': 'html_parsed'
                        })
            
            return reviews
            
        except Exception as e:
            print(f"HTML parse hatası: {e}")
            return []
    
    def extract_reviews_from_raw_data(self, data):
        """Ham veriden yorumları çıkar"""
        reviews = []
        
        try:
            # JSON string'i dict'e çevir
            if isinstance(data, str):
                data = json.loads(data)
            
            # Recursive olarak yorumları ara
            def find_reviews(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Yorum benzeri alanları kontrol et
                        if any(keyword in key.lower() for keyword in ['comment', 'review', 'text', 'content']):
                            if isinstance(value, str) and len(value) > 10:
                                reviews.append({
                                    'comment': value,
                                    'field': key,
                                    'source': 'raw_data'
                                })
                        
                        # Recursive arama
                        find_reviews(value, current_path)
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        current_path = f"{path}[{i}]"
                        find_reviews(item, current_path)
            
            find_reviews(data)
            return reviews
            
        except Exception as e:
            print(f"Ham veri parse hatası: {e}")
            return []
    
    def get_all_reviews(self, product_url, target_count=1000, max_pages=50):
        """Tüm yorumları çek"""
        print(f"🎯 Hedef: {target_count} yorum çekmek")
        
        # Ürün bilgilerini çıkar
        product_info = self.extract_product_info(product_url)
        if not product_info:
            print("❌ Ürün bilgileri çıkarılamadı")
            return []
        
        print(f"📦 Ürün ID: {product_info['product_id']}")
        print(f"🏪 Seller ID: {product_info['seller_id']}")
        
        all_reviews = []
        page = 1
        
        while len(all_reviews) < target_count and page <= max_pages:
            print(f"\n📄 Sayfa {page} çekiliyor... (Mevcut: {len(all_reviews)} yorum)")
            
            # API'den yorumları çek
            api_data = self.get_reviews_via_api(product_info, page=page)
            
            if api_data:
                reviews = self.parse_reviews_data(api_data)
                if reviews:
                    all_reviews.extend(reviews)
                    print(f"✅ API'den {len(reviews)} yorum alındı")
                else:
                    print("⚠️ API'den yorum alınamadı, web API deneniyor...")
                    
                    # Web API'yi dene
                    web_data = self.get_reviews_via_web(product_info, page=page)
                    if web_data:
                        web_reviews = self.parse_reviews_data(web_data)
                        if web_reviews:
                            all_reviews.extend(web_reviews)
                            print(f"✅ Web API'den {len(web_reviews)} yorum alındı")
            
            # Rate limiting
            time.sleep(self.request_delay)
            page += 1
            
            # Eğer yeni yorum gelmiyorsa dur
            if page > 3 and len(all_reviews) == 0:
                print("❌ Hiç yorum alınamadı")
                break
        
        print(f"\n🎉 Toplam {len(all_reviews)} yorum çekildi!")
        return all_reviews[:target_count]  # Hedef sayıda yorum döndür
    
    def save_reviews_to_csv(self, reviews, filename=None):
        """Yorumları CSV dosyasına kaydet"""
        if not reviews:
            print("❌ Kaydedilecek yorum bulunamadı")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trendyol_reviews_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['comment', 'user', 'date', 'rating', 'seller', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for review in reviews:
                    # Eksik alanları doldur
                    review_data = {
                        'comment': review.get('comment', ''),
                        'user': review.get('user', 'Anonim'),
                        'date': review.get('date', ''),
                        'rating': review.get('rating', ''),
                        'seller': review.get('seller', ''),
                        'source': review.get('source', 'api')
                    }
                    writer.writerow(review_data)
            
            print(f"✅ {len(reviews)} yorum {filename} dosyasına kaydedildi")
            
        except Exception as e:
            print(f"❌ CSV kaydetme hatası: {e}")
    
    def analyze_reviews(self, reviews):
        """Yorumları analiz et"""
        if not reviews:
            print("❌ Analiz edilecek yorum bulunamadı")
            return
        
        print(f"\n📊 Yorum Analizi:")
        print(f"   - Toplam yorum: {len(reviews)}")
        
        # Kaynak dağılımı
        sources = {}
        for review in reviews:
            source = review.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   - Kaynak dağılımı:")
        for source, count in sources.items():
            print(f"     * {source}: {count} yorum")
        
        # Ortalama yorum uzunluğu
        total_length = sum(len(str(review.get('comment', ''))) for review in reviews)
        avg_length = total_length / len(reviews) if reviews else 0
        print(f"   - Ortalama yorum uzunluğu: {avg_length:.1f} karakter")

def main():
    """Ana fonksiyon"""
    print("🚀 Gelişmiş Trendyol API Sistemi")
    print("=" * 50)
    
    # URL al
    url = input("Trendyol ürün URL'sini girin: ").strip()
    if not url:
        print("❌ URL gerekli!")
        return
    
    # Hedef yorum sayısını al
    target_input = input("Hedef yorum sayısını girin (varsayılan: 1000): ").strip()
    target_count = int(target_input) if target_input else 1000
    
    # API instance'ı oluştur
    api = EnhancedTrendyolAPI()
    
    try:
        # Yorumları çek
        reviews = api.get_all_reviews(url, target_count=target_count)
        
        if reviews:
            # Analiz et
            api.analyze_reviews(reviews)
            
            # CSV'ye kaydet
            api.save_reviews_to_csv(reviews)
            
            print(f"\n🎯 Başarılı! {len(reviews)} yorum çekildi ve kaydedildi.")
        else:
            print("❌ Hiç yorum çekilemedi")
    
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
