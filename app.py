from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Optional
import asyncio

# Import your parser/scraper
try:
    from parser import YourScraperClass  # Replace with your actual scraper class
except ImportError:
    # Fallback if parser.py doesn't exist
    class YourScraperClass:
        def __init__(self):
            self.browser = None
        
        async def scrape(self, url: str):
            return {"message": "Scraper not implemented", "url": url}

app = FastAPI(
    title="Web Scraper API",
    description="FastAPI + Playwright web scraper service",
    version="1.0.0"
)

# Initialize scraper
scraper = YourScraperClass()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Web Scraper API is running!",
        "status": "healthy",
        "endpoints": {
            "scrape": "/scrape?url=<target_url>",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "web-scraper",
        "version": "1.0.0"
    }

@app.get("/scrape")
async def scrape_url(url: str):
    """
    Scrape a given URL using Playwright
    
    Args:
        url: The URL to scrape
        
    Returns:
        JSON response with scraped data
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    try:
        # Call your scraper
        result = await scraper.scrape(url)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/scrape")
async def scrape_url_post(url: str):
    """
    POST endpoint for scraping (same as GET but for POST requests)
    """
    return await scrape_url(url)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 