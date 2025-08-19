import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Any
import time

class WebScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        
    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with cloud-optimized settings
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        
        # Create new page
        self.page = await self.browser.new_page()
        
        # Set user agent
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("✅ Browser initialized successfully")
    
    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Main scraping method
        
        Args:
            url: Target URL to scrape
            
        Returns:
            Dictionary with scraped data
        """
        try:
            # Initialize browser if not already done
            if not self.browser:
                await self.init_browser()
            
            print(f"🌐 Scraping: {url}")
            
            # Navigate to URL
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit for dynamic content
            await asyncio.sleep(2)
            
            # Get page content
            content = await self.page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract data (customize based on your needs)
            scraped_data = {
                "url": url,
                "title": soup.title.string if soup.title else "No title",
                "text_content": self.extract_text(soup),
                "links": self.extract_links(soup),
                "images": self.extract_images(soup),
                "timestamp": time.time()
            }
            
            print(f"✅ Successfully scraped {url}")
            return scraped_data
            
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return {
                "error": str(e),
                "url": url,
                "timestamp": time.time()
            }
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:1000]  # Limit to first 1000 chars
    
    def extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                links.append(href)
        return links[:10]  # Limit to first 10 links
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract all image URLs"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('http'):
                images.append(src)
        return images[:5]  # Limit to first 5 images
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

# For compatibility with app.py
YourScraperClass = WebScraper

# Example usage
async def main():
    scraper = WebScraper()
    try:
        result = await scraper.scrape("https://example.com")
        print(json.dumps(result, indent=2))
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 