import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Try to import the Selenium scraper from multiple paths
TrendyolSeleniumScraper = None
try:
	from src.scrapers.trendyol_selenium_scraper import TrendyolSeleniumScraper as _Scraper
	TrendyolSeleniumScraper = _Scraper
except Exception:
	try:
		from trendyol_selenium_scraper import TrendyolSeleniumScraper as _Scraper
		TrendyolSeleniumScraper = _Scraper
	except Exception:
		TrendyolSeleniumScraper = None

app = FastAPI(title="Trendyol Selenium Scraper API", version="1.0.0")

class ScrapeRequest(BaseModel):
	url: str
	min_comments: int = 100
	max_scrolls: int = 50

class ScrapeResponse(BaseModel):
	source: str
	count: int
	comments: List[Dict[str, Any]]

@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}

@app.post("/scrape/trendyol", response_model=ScrapeResponse)
async def scrape_trendyol(req: ScrapeRequest):
	if not TrendyolSeleniumScraper:
		raise HTTPException(status_code=500, detail="Selenium scraper not available on this server")
	if not req.url or not req.url.startswith("https://www.trendyol.com"):
		raise HTTPException(status_code=400, detail="Provide a valid Trendyol product URL")
	
	scraper = None
	try:
		scraper = TrendyolSeleniumScraper()
		comments = scraper.scrape_comments_with_fallback(
			req.url,
			min_comments=req.min_comments
		)
		comments = comments or []
		# Normalize to expected fields
		normalized: List[Dict[str, Any]] = []
		for c in comments:
			normalized.append({
				"user": c.get("user", "Anonim"),
				"date": c.get("date", ""),
				"comment": c.get("comment", ""),
				"rating": c.get("rating", ""),
				"seller": c.get("seller", "")
			})
		return ScrapeResponse(source="selenium", count=len(normalized), comments=normalized)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")
	finally:
		try:
			if scraper:
				scraper.close()
		except Exception:
			pass

if __name__ == "__main__":
	port = int(os.getenv("PORT", 8001))
	uvicorn.run(app, host="0.0.0.0", port=port) 