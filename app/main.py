from fastapi import FastAPI
from app.core.config import settings
from app.routers import facebook

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="OmniScraper-AI API to trigger and monitor scraping tasks via Celery",
    version="1.0.0"
)

app.include_router(facebook.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
