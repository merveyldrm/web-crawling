import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
from urllib.parse import urlparse, parse_qs

class TrendyolAPIDetector:
    def __init__(self):
        # Chrome DevTools Protocol için gerekli ayarlar
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Network logging için gerekli
        self.options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        
        # Bot tespitini engelle
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Network trafiğini yakalamak için
        self.network_requests = []
        self.comment_apis = []

    def enable_network_logging(self):
        """Network trafiğini yakalamak için DevTools Protocol'ü etkinleştir"""
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # Network event listener'ları ekle
        self.driver.execute_cdp_cmd('Network.setRequestInterception', {
            'patterns': [{
                'urlPattern': '*',
                'resourceType': 'XHR',
                'interceptionStage': 'Request'
            }]
        })

    def capture_network_requests(self, product_url):
        """Network trafiğini yakala ve analiz et"""
        print(f"Network trafiği yakalanıyor: {product_url}")
        
        # Logları temizle
        self.driver.get_log('performance')
        
        # Sayfayı yükle
        self.driver.get(product_url)
        time.sleep(5)
        
        # Yorumlar bölümüne scroll yap
        self.scroll_to_comments()
        
        # Network loglarını al
        logs = self.driver.get_log('performance')
        
        # API çağrılarını analiz et
        api_calls = self.analyze_network_logs(logs)
        
        return api_calls

    def scroll_to_comments(self):
        """Yorumlar bölümüne scroll yap ve daha fazla yorum yükle"""
        print("Yorumlar bölümüne scroll yapılıyor...")
        
        # Sayfanın altına scroll yap
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Yorumlar bölümünü bul
        comment_selectors = [
            "#reviews",
            ".reviews", 
            "[class*='review']",
            "[class*='comment']",
            "[data-testid*='review']"
        ]
        
        for selector in comment_selectors:
            try:
                section = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", section)
                print(f"Yorum bölümü bulundu: {selector}")
                break
            except:
                continue
        
        # "Daha fazla" butonlarını tıkla
        for i in range(5):
            try:
                more_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Daha fazla') or contains(text(), 'Daha Fazla') or " +
                    "contains(text(), 'göster') or contains(text(), 'Göster') or " +
                    "contains(text(), 'yükle') or contains(text(), 'Yükle')]"
                )
                
                for btn in more_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", btn)
                        print(f"Daha fazla yorum butonuna tıklandı ({i+1})")
                        time.sleep(3)
                        break
                        
                # Scroll yap
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                
            except Exception as e:
                print(f"Scroll hatası: {e}")
                break

    def analyze_network_logs(self, logs):
        """Network loglarını analiz et ve API çağrılarını bul"""
        api_calls = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                
                if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                    request_id = message['message']['params']['requestId']
                    response = message['message']['params']['response']
                    
                    url = response['url']
                    
                    # Trendyol API endpoint'lerini ara
                    if self.is_trendyol_api(url):
                        api_info = {
                            'url': url,
                            'method': 'GET',  # Varsayılan
                            'headers': {},
                            'params': {},
                            'response_size': response.get('encodedDataLength', 0),
                            'status': response.get('status', 0)
                        }
                        
                        # URL parametrelerini parse et
                        parsed_url = urlparse(url)
                        api_info['params'] = parse_qs(parsed_url.query)
                        
                        api_calls.append(api_info)
                        print(f"API çağrısı bulundu: {url}")
                        
            except Exception as e:
                continue
        
        return api_calls

    def is_trendyol_api(self, url):
        """URL'nin Trendyol API'si olup olmadığını kontrol et"""
        trendyol_domains = [
            'trendyol.com',
            'api.trendyol.com',
            'mobileapi.trendyol.com',
            'gw.trendyol.com',
            'apigw.trendyol.com'
        ]
        
        # Trendyol domain kontrolü
        for domain in trendyol_domains:
            if domain in url:
                return True
        
        # Yorum/comment içeren URL'ler
        comment_keywords = ['comment', 'review', 'yorum', 'rating', 'feedback']
        for keyword in comment_keywords:
            if keyword in url.lower():
                return True
        
        return False

    def extract_api_details(self, api_calls):
        """API çağrılarından detayları çıkar"""
        comment_apis = []
        
        for api in api_calls:
            url = api['url']
            
            # Yorum API'si olup olmadığını kontrol et
            if self.is_comment_api(url):
                comment_apis.append({
                    'url': url,
                    'method': api['method'],
                    'headers': api['headers'],
                    'params': api['params'],
                    'response_size': api['response_size'],
                    'status': api['status']
                })
        
        return comment_apis

    def is_comment_api(self, url):
        """URL'nin yorum API'si olup olmadığını kontrol et"""
        comment_patterns = [
            'comment',
            'review', 
            'yorum',
            'rating',
            'feedback',
            'evaluation'
        ]
        
        url_lower = url.lower()
        for pattern in comment_patterns:
            if pattern in url_lower:
                return True
        
        return False

    def test_api_endpoint(self, api_info):
        """API endpoint'ini test et"""
        url = api_info['url']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Referer': 'https://www.trendyol.com/',
            'Origin': 'https://www.trendyol.com'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'success': True,
                        'data': data,
                        'size': len(response.content)
                    }
                except:
                    return {
                        'success': True,
                        'data': response.text,
                        'size': len(response.content)
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'size': len(response.content)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_direct_api_script(self, api_info):
        """Doğrudan API çağrısı için Python scripti oluştur"""
        script = f'''import requests
import json

def get_trendyol_comments(product_id=None, page=1, limit=50):
    """
    Trendyol yorumlarını doğrudan API'den çek
    
    Args:
        product_id: Ürün ID'si (URL'den çıkarılabilir)
        page: Sayfa numarası
        limit: Sayfa başına yorum sayısı
    
    Returns:
        dict: API yanıtı
    """
    
    # API endpoint'i
    url = "{api_info['url']}"
    
    # Headers
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Referer': 'https://www.trendyol.com/',
        'Origin': 'https://www.trendyol.com'
    }}
    
    # Parameters
    params = {{
        'page': page,
        'limit': limit
    }}
    
    # Product ID varsa ekle
    if product_id:
        params['productId'] = product_id
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Hatası: {{response.status_code}}")
            return None
            
    except Exception as e:
        print(f"Bağlantı hatası: {{e}}")
        return None

# Kullanım örneği
if __name__ == "__main__":
    # Ürün ID'sini URL'den çıkar
    # Örnek: https://www.trendyol.com/urun/123456 -> product_id = 123456
    
    comments = get_trendyol_comments(product_id="PRODUCT_ID_HERE")
    
    if comments:
        print(f"Toplam {{len(comments)}} yorum bulundu")
        for comment in comments[:5]:  # İlk 5 yorumu göster
            print(f"- {{comment}}")
    else:
        print("Yorum alınamadı")
'''
        
        return script

    def detect_and_analyze(self, product_url):
        """Ana tespit ve analiz fonksiyonu"""
        print("=== Trendyol API Tespit Sistemi ===")
        print(f"Hedef URL: {product_url}")
        
        # Network trafiğini yakala
        api_calls = self.capture_network_requests(product_url)
        
        if not api_calls:
            print("Hiç API çağrısı bulunamadı!")
            return None
        
        print(f"\nToplam {len(api_calls)} API çağrısı bulundu")
        
        # Yorum API'lerini filtrele
        comment_apis = self.extract_api_details(api_calls)
        
        if not comment_apis:
            print("Yorum API'si bulunamadı!")
            return None
        
        print(f"\n{len(comment_apis)} yorum API'si bulundu:")
        
        results = []
        for i, api in enumerate(comment_apis):
            print(f"\n--- API {i+1} ---")
            print(f"URL: {api['url']}")
            print(f"Method: {api['method']}")
            print(f"Status: {api['status']}")
            print(f"Response Size: {api['response_size']} bytes")
            
            # API'yi test et
            test_result = self.test_api_endpoint(api)
            
            if test_result['success']:
                print("✅ API erişilebilir")
                print(f"Response size: {test_result['size']} bytes")
                
                # Python scripti oluştur
                script = self.generate_direct_api_script(api)
                
                results.append({
                    'api_info': api,
                    'test_result': test_result,
                    'script': script
                })
            else:
                print(f"❌ API erişilemez: {test_result['error']}")
        
        return results

    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()

def main():
    """Ana fonksiyon"""
    print("Trendyol API Tespit Sistemi")
    print("=" * 50)
    
    # Test URL'si
    test_url = input("Trendyol ürün URL'sini girin: ").strip()
    
    if not test_url:
        print("URL gerekli!")
        return
    
    detector = TrendyolAPIDetector()
    
    try:
        results = detector.detect_and_analyze(test_url)
        
        if results:
            print("\n" + "="*50)
            print("SONUÇLAR")
            print("="*50)
            
            for i, result in enumerate(results):
                print(f"\n--- API {i+1} ---")
                print(f"URL: {result['api_info']['url']}")
                print(f"Status: {result['test_result']['success']}")
                
                # Script'i dosyaya kaydet
                filename = f"trendyol_api_script_{i+1}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result['script'])
                print(f"Script kaydedildi: {filename}")
        
        else:
            print("Hiç API bulunamadı!")
            
    except Exception as e:
        print(f"Hata: {e}")
        
    finally:
        detector.close()

if __name__ == "__main__":
    main() 