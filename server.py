import http.server
import socketserver
import json
import subprocess
import traceback
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/analyze'):
            print("\n--- Analiz İsteği Alındı ---")
            query_components = parse_qs(urlparse(self.path).query)
            product_url = query_components.get('url', [None])[0]

            if not product_url:
                print("Hata: URL parametresi eksik.")
                self.send_error_response(400, 'URL is required')
                return

            print(f"Analiz edilecek URL: {product_url}")

            try:
                # 1. Scraper betiğini URL ile güncelle
                print("1. src/scrapers/trendyol_selenium_scraper.py güncelleniyor...")
                with open('src/scrapers/trendyol_selenium_scraper.py', 'r', encoding='utf-8') as f:
                    scraper_code = f.read()
                
                # URL'yi bul ve değiştir (daha esnek hale getirildi)
                import re
                new_scraper_code = re.sub(r'url = ".*"', f'url = "{product_url}"', scraper_code)

                with open('src/scrapers/trendyol_selenium_scraper.py', 'w', encoding='utf-8') as f:
                    f.write(new_scraper_code)
                print("Scraper güncellendi.")

                # 2. Scraper'ı çalıştır
                print("2. Yorumlar çekiliyor (scraper çalıştırılıyor)...")
                scraper_process = subprocess.run(['python', 'src/scrapers/trendyol_selenium_scraper.py'], capture_output=True, text=True, check=True, encoding='utf-8')
                print("Scraper stdout:", scraper_process.stdout)
                print("Scraper stderr:", scraper_process.stderr)
                print("Yorumlar çekildi.")

                # 3. Özetleyiciyi çalıştır
                print("3. Yorumlar özetleniyor (summarizer çalıştırılıyor)...")
                summarizer_process = subprocess.run(['python', 'src/analyzers/comment_summarizer.py'], capture_output=True, text=True, check=True, encoding='utf-8')
                print("Summarizer stdout:", summarizer_process.stdout)
                print("Summarizer stderr:", summarizer_process.stderr)
                print("Yorumlar özetlendi.")

                # 4. Özeti oku ve gönder
                print("4. Özet okunuyor ve gönderiliyor...")
                with open('comment_summary.txt', 'r', encoding='utf-8') as f:
                    summary = f.read()

                self.send_success_response({'summary': summary})
                print("--- Analiz Başarıyla Tamamlandı ---")

            except subprocess.CalledProcessError as e:
                print("HATA: Alt süreçlerden biri hata verdi.")
                print(f"Return code: {e.returncode}")
                print(f"Stdout: {e.stdout}")
                print(f"Stderr: {e.stderr}")
                self.send_error_response(500, f'Bir betik çalıştırılırken hata oluştu: {e.stderr}')
            except Exception as e:
                print(f"BEKLENMEDİK HATA: {e}")
                traceback.print_exc() # Print full traceback to the console
                self.send_error_response(500, f'Sunucuda beklenmedik bir hata oluştu: {e}')

        else:
            # Statik dosyaları sun
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

Handler = MyHttpRequestHandler

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f"Sunucu http://localhost:{PORT} adresinde başlatıldı")
    httpd.serve_forever()