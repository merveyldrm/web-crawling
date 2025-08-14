
import sys
import os
import time
import json
import requests
sys.path.append('./src/scrapers')

from trendyol_selenium_scraper import TrendyolSeleniumScraper

# URL from Streamlit
url = "https://www.trendyol.com/zuhre-ana/karadut-ozu-670-gr-p-712245449/yorumlar?boutiqueId=61&merchantId=123388"
min_comments = 100
max_scrolls = 50

# Real-time logging function
def send_log_to_streamlit(message, log_type="info"):
    try:
        log_data = {
            "message": message,
            "type": log_type,
            "timestamp": time.strftime("%H:%M:%S")
        }
        
        # Write to a file that Streamlit can read
        with open("scraping_logs.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
            
    except Exception as e:
        print(f"Log error: {e}")

try:
    send_log_to_streamlit("🚀 Scraping başlatılıyor...", "info")
    
    scraper = TrendyolSeleniumScraper(enable_logging=False)  # Disable built-in logging
    
    # Override scraper's logging methods
    original_send_log = scraper.send_log
    scraper.send_log = send_log_to_streamlit
    
    send_log_to_streamlit(f"📊 Scraping parametreleri:", "info")
    send_log_to_streamlit(f"   URL: {url}", "info")
    send_log_to_streamlit(f"   Min Comments: {min_comments}", "info")
    send_log_to_streamlit(f"   Max Scrolls: {max_scrolls}", "info")
    
    send_log_to_streamlit("1️⃣ Scraper betiği güncelleniyor...", "progress")
    
    # Update scraper script
    scraper_file = 'src/scrapers/trendyol_selenium_scraper.py'
    with open(scraper_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    content = re.sub(r'url = ".*"', f'url = "{url}"', content)
    content = re.sub(r'min_comments = \d+', f'min_comments = {min_comments}', content)
    content = re.sub(r'max_scrolls = \d+', f'max_scrolls = {max_scrolls}', content)
    
    with open(scraper_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    send_log_to_streamlit("✅ Scraper betiği güncellendi", "success")
    
    send_log_to_streamlit("2️⃣ Yorumlar çekiliyor...", "progress")
    
    # Start scraping
    comments = scraper.scrape_comments_with_fallback(url, min_comments=min_comments)
    
    if comments:
        send_log_to_streamlit(f"✅ Scraping tamamlandı! {len(comments)} yorum toplandı", "success")
        
        # Save to CSV
        csv_filename = "trendyol_comments.csv"
        scraper.save_to_csv(comments, filename=csv_filename)
        
        send_log_to_streamlit(f"💾 Yorumlar {csv_filename} dosyasına kaydedildi", "success")
        
        result = {
            "success": True,
            "comments_count": len(comments),
            "csv_filename": csv_filename
        }
    else:
        send_log_to_streamlit("❌ Hiç yorum bulunamadı", "error")
        result = {"success": False, "error": "No comments found"}
    
    scraper.close()
    
except Exception as e:
    send_log_to_streamlit(f"❌ Scraping hatası: {str(e)}", "error")
    result = {"success": False, "error": str(e)}

# Final result
with open("scraping_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
