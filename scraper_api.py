from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import traceback

# Mevcut kazıyıcı sınıfımızı import edelim
from trendyol_selenium_scraper import TrendyolSeleniumScraper

app = FastAPI(
    title="Trendyol Scraper API",
    description="Trendyol ürün sayfalarından yorum kazımak için bir API.",
    version="1.0.0"
)

# API'ye gönderilecek istek gövdesinin modelini tanımlayalım
class ScrapeRequest(BaseModel):
    product_url: str = Field(..., example="https://www.trendyol.com/casio/saat-p-12345")
    min_comments: int = Field(100, description="Toplanması hedeflenen minimum yorum sayısı.")

# API'nin ana endpoint'i
@app.post("/scrape/", summary="Bir ürünün yorumlarını kazır", tags=["Scraping"])
async def scrape_product_comments(request: ScrapeRequest):
    """
    Verilen Trendyol ürün URL'sinden yorumları kazır.

    - **product_url**: Kazınacak ürünün tam URL'si.
    - **min_comments**: Toplanacak minimum yorum sayısı.
    """
    scraper = None
    try:
        print(f"Scraping started for URL: {request.product_url}")
        # Kazıyıcı sınıfından bir nesne oluştur
        scraper = TrendyolSeleniumScraper()
        
        # Yorumları kazı
        comments = scraper.scrape_comments(
            product_url=request.product_url,
            min_comments=request.min_comments
        )
        
        print(f"Found {len(comments)} comments.")
        
        if not comments:
            # Yorum bulunamazsa 404 Not Found hatası yerine, durumu belirten bir mesajla boş liste döndürmek daha iyi olabilir.
            return {"message": "No comments found or scraping failed.", "comments": []}
            
        return {"message": f"Successfully scraped {len(comments)} comments.", "comments": comments}

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        # Bir hata oluşursa, sunucunun çökmemesi için hatayı yakalayıp HTTP hatası olarak döndürelim
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
    finally:
        # Hata olsa da olmasa da tarayıcıyı kapatmayı garanti edelim
        if scraper:
            print("Closing scraper driver.")
            scraper.close()

@app.get("/", summary="API Sağlık Durumu", tags=["General"])
async def root():
    return {"message": "Scraper API is running."}
