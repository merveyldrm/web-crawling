import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class TrendyolSeleniumScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        
        # Cloud environment optimizations
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Anti-bot bypass
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set Chrome binary path for cloud environments
        chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/google-chrome')
        if os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
        
        # Window size for cloud
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Chrome driver setup
        try:
            # Try to use system chromedriver first
            chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', '/usr/bin/chromedriver')
            if os.path.exists(chrome_driver_path):
                service = Service(chrome_driver_path)
            else:
                # Fallback to webdriver-manager
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            # Try with minimal options
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        # Bot detection bypass
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set window size
        self.driver.set_window_size(1920, 1080)
        
        print("✅ Selenium scraper initialized successfully")

    def wait_for_comments_to_load(self, timeout=30):
        selectors = [
            "div.comment",
            "div[class*='comment']",
            "div[class*='review']",
            ".reviews .comment",
            ".comment-container .comment"
        ]
        for selector in selectors:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Yorumlar yüklendi: {selector}")
                return True
            except TimeoutException:
                continue
        return False

    def debug_page_structure(self):
        """Sayfanın DOM yapısını debug etmek için"""
        print("=== DEBUG: Sayfa DOM Yapısı ===")
        
        # Sayfa kaynağını al
        page_source = self.driver.page_source
        print(f"Sayfa kaynak kodu uzunluğu: {len(page_source)} karakter")
        
        # Yorumlarla ilgili elementleri ara
        comment_keywords = ['comment', 'review', 'yorum', 'değerlendirme', 'reviews']
        
        for keyword in comment_keywords:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(@class, '{keyword}') or contains(@id, '{keyword}')]")
                print(f"'{keyword}' içeren elementler: {len(elements)} adet")
                
                for i, elem in enumerate(elements[:3]):  # İlk 3'ünü göster
                    try:
                        print(f"  Element {i+1}: {elem.tag_name}, class: {elem.get_attribute('class')}, id: {elem.get_attribute('id')}")
                        print(f"    Text: {elem.text[:100]}...")
                    except:
                        pass
            except:
                continue
        
        # JavaScript ile daha detaylı inceleme
        js_script = """
        // Tüm elementleri tara ve yorum benzeri class/id isimlerini bul
        let commentElements = [];
        let allElements = document.querySelectorAll('*');
        
        allElements.forEach(el => {
            let className = el.className || '';
            let id = el.id || '';
            let text = el.textContent || '';
            
            if ((className.toLowerCase().includes('comment') || 
                 className.toLowerCase().includes('review') ||
                 className.toLowerCase().includes('yorum') ||
                 id.toLowerCase().includes('comment') ||
                 id.toLowerCase().includes('review')) && 
                text.length > 10) {
                commentElements.push({
                    tag: el.tagName,
                    className: className,
                    id: id,
                    text: text.substring(0, 100),
                    innerHTML: el.innerHTML.substring(0, 200)
                });
            }
        });
        
        return commentElements;
        """
        
        try:
            js_results = self.driver.execute_script(js_script)
            print(f"\n=== JavaScript ile bulunan yorum elementleri: {len(js_results)} adet ===")
            
            for i, elem in enumerate(js_results[:5]):
                print(f"Element {i+1}:")
                print(f"  Tag: {elem['tag']}")
                print(f"  Class: {elem['className']}")
                print(f"  ID: {elem['id']}")
                print(f"  Text: {elem['text']}...")
                print(f"  HTML: {elem['innerHTML']}...")
                print("-" * 50)
        except Exception as e:
            print(f"JavaScript debug hatası: {e}")

    def extract_comments_from_page(self):
        # Debug modunu kapat (production için)
        # if not hasattr(self, '_debug_done'):
        #     self.debug_page_structure()
        #     self._debug_done = True
        
        comments = []
        
        # Daha kapsamlı selector listesi - Trendyol 2024/2025 için
        selectors = [
            # Mevcut selectors
            "div.comment",
            "div[class*='comment']",
            "div[class*='review']",
            ".reviews .comment",
            ".comment-container .comment",
            
            # Trendyol'a özgü modern selectors
            "[data-testid*='review']",
            "[data-testid*='comment']",
            "div[class*='Review']",
            "div[class*='Comment']",
            "div[id*='review']",
            "div[id*='comment']",
            
            # Daha genel selectors
            "div[class*='user-review']",
            "div[class*='customer-review']",
            "article",
            "div[class*='feedback']",
            
            # Trendyol'un kullandığı potansiyel class isimleri
            "div[class*='pr-rnr']",  # product-review-rating gibi
            "div[class*='reviews']",
            "div[class*='rating']",
            "div[class*='evaluation']",
            "div[class*='yorumlar']",
            "div[class*='ürün-yorumu']",
            
            # Modern CSS framework patterns
            "div[class*='ReviewItem']",
            "div[class*='CommentItem']",
            "div[class*='UserComment']",
            "div[class*='ProductReview']",
            "div[class*='CustomerReview']",
            
            # CSS Module patterns (hash-based classes)
            "div[class*='review-']",
            "div[class*='comment-']",
            "div[class*='_review_']",
            "div[class*='_comment_']",
            
            # Shadow DOM ve web components
            "review-item",
            "comment-item",
            "user-review",
            
            # En son çare: Herhangi bir div içinde uzun metin
            "div p:not(:empty)",
            "div span:not(:empty)",
        ]
        
        comment_elements = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Selector '{selector}': {len(elements)} element bulundu")
                if elements:
                    # En az 10 karakter metin içeren elementleri filtrele
                    filtered_elements = []
                    for elem in elements:
                        try:
                            if len(elem.text.strip()) >= 10:
                                filtered_elements.append(elem)
                        except:
                            continue
                    
                    if filtered_elements:
                        comment_elements = filtered_elements
                        print(f"Yorumlar bulundu: {selector} ({len(filtered_elements)} adet - filtrelenmiş)")
                    break
            except Exception as e:
                print(f"Selector '{selector}' hatası: {e}")
                continue
        
        if not comment_elements:
            print("Hiç yorum elementi bulunamadı.")
            print("Sayfadaki tüm div elementlerini kontrol ediliyor...")
            
            # Tüm div elementlerini kontrol et
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            print(f"Toplam {len(all_divs)} div elementi bulundu")
            
            # Metin içeren divleri filtrele
            text_divs = []
            for div in all_divs:
                try:
                    text = div.text.strip()
                    if len(text) > 20 and len(text) < 500:  # Yorum boyutunda metin
                        text_divs.append(div)
                except:
                    continue
            
            print(f"Metin içeren {len(text_divs)} div bulundu")
            
            # İlk birkaçını örnek olarak göster
            for i, div in enumerate(text_divs[:5]):
                try:
                    print(f"Div {i+1}: {div.text[:100]}...")
                    print(f"  Class: {div.get_attribute('class')}")
                    print(f"  ID: {div.get_attribute('id')}")
                except:
                    pass
            
            return comments
            
        print(f"Toplam {len(comment_elements)} yorum elementi işlenecek")
        
        for i, element in enumerate(comment_elements):
            try:
                comment_data = self.parse_comment_element(element)
                if comment_data and comment_data.get('comment'):
                    comments.append(comment_data)
                    print(f"Yorum {i+1} başarıyla parse edildi: {comment_data.get('comment', '')[:50]}...")
                else:
                    print(f"Yorum {i+1} parse edilemedi veya boş")
            except Exception as e:
                print(f"Yorum {i+1} parse edilirken hata: {e}")
                continue
                
        print(f"Toplam {len(comments)} yorum çıkarıldı")
        return comments

    def parse_comment_element(self, element):
        comment_data = {}
        try:
            # Kullanıcı adını al
            user_selectors = [
                ".comment-info .comment-info-item",
                ".user-name",
                ".author",
                ".commenter",
                "[class*='user']",
                "[class*='author']"
            ]
            for selector in user_selectors:
                try:
                    user_element = element.find_element(By.CSS_SELECTOR, selector)
                    comment_data['user'] = user_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            # Tarih bilgisini al
            date_selectors = [
                ".comment-info .comment-info-item:nth-child(2)",
                
                ".date",
                ".timestamp",
                ".comment-date",
                "[class*='date']"
            ]
            for selector in date_selectors:
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, selector)
                    comment_data['date'] = date_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            # Yorum metnini al
            text_selectors = [
                ".comment-text p",
                ".comment-text",
                ".review-text",
                ".comment-content",
                "p",
                "[class*='text']",
                "[class*='content']"
            ]
            for selector in text_selectors:
                try:
                    text_element = element.find_element(By.CSS_SELECTOR, selector)
                    comment_data['comment'] = text_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            # Satıcı bilgisini al
            seller_selectors = [
                ".seller-name-info",
                ".seller-name",
                ".merchant-name",
                "[class*='seller']",
                "[class*='merchant']"
            ]
            for selector in seller_selectors:
                try:
                    seller_element = element.find_element(By.CSS_SELECTOR, selector)
                    comment_data['seller'] = seller_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            # Puan bilgisini al
            rating_selectors = [
                ".rating",
                ".star",
                "[class*='rating']",
                "[class*='star']"
            ]
            for selector in rating_selectors:
                try:
                    rating_element = element.find_element(By.CSS_SELECTOR, selector)
                    comment_data['rating'] = rating_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
        except Exception as e:
            print(f"Element parse hatası: {e}")
        return comment_data

    def scroll_and_collect_comments(self, min_comments=1000, max_scrolls=200):
        all_comments = []
        seen = set()
        last_count = 0
        no_new_comments_count = 0
        
        print(f"Hedef: En az {min_comments} yorum toplamak")
        
        for i in range(max_scrolls):
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Optimize edilmiş bekleme süresi
            
            # Yorumlar bölümüne odaklan
            try:
                # Yorumlar bölümünü bul ve ona scroll yap
                review_section = self.driver.find_element(By.CSS_SELECTOR, "[class*='review'], [class*='comment'], #reviews, .reviews")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", review_section)
                time.sleep(1)
            except:
                pass
            
            # 'Daha fazla göster' veya benzeri butonları tıkla (daha agresif)
            try:
                # Daha geniş buton arama
                more_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Daha fazla') or contains(text(), 'Daha Fazla') or " +
                    "contains(text(), 'daha fazla') or contains(text(), 'göster') or " +
                    "contains(text(), 'Göster') or contains(text(), 'yükle') or " +
                    "contains(text(), 'Yükle') or contains(text(), 'Sonraki') or " +
                    "contains(text(), 'Load') or contains(text(), 'More') or " +
                    "contains(text(), 'Tümünü') or contains(text(), 'tümünü')]"
                )
                
                # Veya class'a göre bul
                if not more_buttons:
                    more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        "button[class*='more'], button[class*='load'], button[class*='show'], " +
                        "a[class*='more'], a[class*='load'], div[class*='load-more']"
                    )
                
                for btn in more_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", btn)
                        print(f"Daha fazla yorum butonuna tıklandı. (Scroll {i+1})")
                        time.sleep(2)
                        break  # İlk butona tıkladıktan sonra dur
            except Exception as e:
                pass
            
            # Ajax yüklemelerini bekle
            time.sleep(1)
            
            # Yeni yorumları topla
            new_comments = self.extract_comments_from_page()
            new_added = 0
            
            for c in new_comments:
                # Sadece yorum metni bazlı benzersizlik kontrolü yap (kullanıcı ve tarih olmayabilir)
                comment_text = c.get('comment', '')
                if comment_text and comment_text not in seen:
                    all_comments.append(c)
                    seen.add(comment_text)
                    new_added += 1
            
            print(f"Scroll {i+1}: {new_added} yeni yorum eklendi. Toplam: {len(all_comments)}")
            
            # Hedef sayıya ulaştık mı?
            if len(all_comments) >= min_comments:
                print(f"Hedef sayıya ulaşıldı: {len(all_comments)} yorum")
                break
            
            # Yeni yorum gelmiyorsa
            if len(all_comments) == last_count:
                no_new_comments_count += 1
                if no_new_comments_count >= 10:  # 10 kez üst üste yeni yorum gelmezse dur
                    print(f"Daha fazla yorum bulunamadı. Toplam: {len(all_comments)}")
                    break
            else:
                no_new_comments_count = 0
            
            last_count = len(all_comments)
            
            # Her 20 scroll'da bir sayfayı yenile (daha az sıklıkta)
            if i > 0 and i % 20 == 0:
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                self.driver.refresh()
                time.sleep(3)
                self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
                time.sleep(1)
        
        print(f"Toplam {len(all_comments)} benzersiz yorum toplandı.")
        return all_comments

    def force_load_all_comments(self):
        """Tüm yorumları zorla yükle"""
        print("=== Tüm yorumları zorla yüklemeye çalışıyor ===")
        
        # 1. Sayfanın en altına in
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 2. Yorumlar bölümünü bul ve odaklan
        comment_sections = [
            "#reviews",
            ".reviews",
            "[class*='review']",
            "[class*='comment']",
            "[data-testid*='review']"
        ]
        
        comment_section = None
        for selector in comment_sections:
            try:
                section = self.driver.find_element(By.CSS_SELECTOR, selector)
                comment_section = section
                print(f"Yorum bölümü bulundu: {selector}")
                break
            except:
                continue
        
        if comment_section:
            # Yorum bölümüne scroll yap
            self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_section)
            time.sleep(2)
        
        # 3. "Daha fazla" butonlarını tıkla (agresif mod)
        load_more_selectors = [
            "button[class*='more']",
            "button[class*='load']", 
            "button[class*='show']",
            "button[class*='daha']",
            "button[class*='fazla']",
            "a[class*='more']",
            "a[class*='load']",
            "div[class*='load-more']",
            "div[class*='show-more']",
            "*[class*='pagination']",
            "*[class*='next']",
            "*[class*='sonraki']"
        ]
        
        max_attempts = 20
        for attempt in range(max_attempts):
            print(f"Daha fazla yükleme denemesi {attempt + 1}/{max_attempts}")
            
            button_clicked = False
            for selector in load_more_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                # JavaScript ile tıkla
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"Buton tıklandı: {selector}")
                                button_clicked = True
                                time.sleep(3)  # Yüklenmesini bekle
                                break
                        except:
                            continue
                    if button_clicked:
                        break
                except:
                    continue
            
            if not button_clicked:
                print("Daha fazla buton bulunamadı")
                break
                
            # Scroll yap
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

    def bypass_anti_bot(self):
        """Anti-bot korumaları bypass et"""
        print("=== Anti-bot bypass çalışıyor ===")
        
        # 1. Mouse hareketleri simüle et
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.driver)
        
        # Random mouse movements
        import random
        for _ in range(5):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y).perform()
            time.sleep(0.5)
        
        # 2. Sayfa üzerinde dolaş
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # 3. Çerezleri kabul et
        cookie_selectors = [
            "button[class*='accept']",
            "button[class*='kabul']",
            "button[class*='cookie']",
            "#accept-cookies",
            ".cookie-accept"
        ]
        
        for selector in cookie_selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    button.click()
                    print(f"Çerez butonu tıklandı: {selector}")
                    time.sleep(2)
                    break
            except:
                continue

    def analyze_real_trendyol_structure(self):
        """Gerçek Trendyol sayfasının yapısını analiz et"""
        print("=== Trendyol Yapı Analizi ===")
        
        # Tüm metin içeren elementleri bul
        js_script = """
        let potentialComments = [];
        
        // Tüm text node'ları bul
        function getAllTextNodes(element) {
            let textNodes = [];
            let walker = document.createTreeWalker(
                element,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.trim().length > 20) {
                    textNodes.push({
                        text: node.textContent.trim(),
                        parent: node.parentElement.tagName,
                        parentClass: node.parentElement.className,
                        parentId: node.parentElement.id
                    });
                }
            }
            return textNodes;
        }
        
        let textNodes = getAllTextNodes(document.body);
        
        // Yorum benzeri metinleri filtrele
        textNodes.forEach(node => {
            let text = node.text.toLowerCase();
            // Türkçe yorum pattern'leri
            if (text.includes('aldım') || text.includes('güzel') || text.includes('beğen') || 
                text.includes('tavsiye') || text.includes('kalite') || text.includes('ürün') ||
                text.includes('memnun') || text.includes('çok') || text.length > 50) {
                potentialComments.push(node);
            }
        });
        
        return potentialComments.slice(0, 50); // İlk 50'yi döndür
        """
        
        try:
            results = self.driver.execute_script(js_script)
            print(f"Potansiyel yorum metinleri: {len(results)} adet")
            
            for i, comment in enumerate(results[:10]):
                print(f"\nPotansiyel Yorum {i+1}:")
                print(f"  Metin: {comment['text'][:100]}...")
                print(f"  Parent Tag: {comment['parent']}")
                print(f"  Parent Class: {comment['parentClass']}")
                print(f"  Parent ID: {comment['parentId']}")
                
        except Exception as e:
            print(f"Analiz hatası: {e}")

    def scrape_comments(self, product_url, min_comments=100, max_scrolls=50):
        max_retries = 3
        comments = []
        
        for attempt in range(max_retries):
            try:
                print(f"Deneme {attempt + 1}/{max_retries}")
                print(f"Sayfa yükleniyor: {product_url}")
                self.driver.get(product_url)
                
                # Sayfa yüklendikten sonra ekran boyutunu tekrar kontrol et
                self.driver.set_window_size(2560, 1440)
                self.driver.execute_script("document.body.style.zoom='1.0'")
                
                time.sleep(5)
                if not self.wait_for_comments_to_load():
                    print("Yorumlar yüklenemedi!")
                    continue
                    
                comments = self.scroll_and_collect_comments(min_comments=min_comments, max_scrolls=max_scrolls)
                
                if len(comments) >= 30:  # Başarılı sayılır
                    return comments
                else:
                    print(f"Yeterli yorum alınamadı ({len(comments)}), tekrar deneniyor...")
                    
            except Exception as e:
                print(f"Deneme {attempt + 1} başarısız: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Tekrar denemeden önce bekle
                    
        return comments

    def scrape_comments_with_fallback(self, product_url, min_comments=100):
        """Fallback stratejisi ile yorum çekme"""
        
        # İlk deneme: Normal metot
        comments = self.scrape_comments(product_url, min_comments, max_scrolls=50)
        
        if len(comments) < 30:  # Anti-bot tespit edilmiş olabilir
            print("Anti-bot tespit edilmiş olabilir, fallback stratejisi deneniyor...")
            
            # Sayfayı yenile ve tekrar dene
            self.driver.refresh()
            time.sleep(5)
            
            # Anti-bot bypass tekrar çalıştır
            self.bypass_anti_bot()
            
            # Tekrar dene
            comments = self.scrape_comments(product_url, min_comments, max_scrolls=100)
        
        return comments

    def save_to_csv(self, comments, filename='trendyol_comments.csv', min_comments=1000):
        if not comments:
            print("Kaydedilecek yorum bulunamadı!")
            return
        
        # Dinamik kaydetme stratejisi
        if len(comments) < min_comments:
            to_save = comments  # Tüm yorumları kaydet
            print(f"Yorum sayısı hedeften az ({len(comments)}), tümü kaydediliyor.")
        else:
            to_save = comments[:min_comments]  # Hedef sayıda yorum kaydet
            print(f"Yorum sayısı hedeften fazla ({len(comments)}), ilk {min_comments} tanesi kaydediliyor.")
            
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['user', 'date', 'comment', 'rating', 'seller']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for comment in to_save:
                writer.writerow(comment)
        print(f"Toplam {len(to_save)} yorum {filename} dosyasına kaydedildi.")

    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    url = input("Lütfen Trendyol ürününün URL'sini girin: ").strip()
    scraper = TrendyolSeleniumScraper()
    
    # Hedef yorum sayısını belirle
    target_comments = input("Hedef yorum sayısını girin (varsayılan: 1000): ").strip()
    if not target_comments:
        target_comments = 1000
    else:
        target_comments = int(target_comments)
    
    print(f"Hedef: {target_comments} yorum çekmek")
    
    # Yorumları çek
    comments = scraper.scrape_comments(url, min_comments=target_comments, max_scrolls=200)
    
    # Sonuçları kaydet
    if len(comments) < target_comments:
        scraper.save_to_csv(comments, min_comments=len(comments))
        print(f"Toplam {len(comments)} yorum bulundu ve hepsi kaydedildi.")
    else:
        scraper.save_to_csv(comments, min_comments=target_comments)
        print(f"Toplam {len(comments)} yorum bulundu, ilk {target_comments} tanesi kaydedildi.")
    
    scraper.close()
    print("İşlem tamamlandı.")