from fastapi import FastAPI
from app.core.config import settings
from app.routers import facebook, tiktok, history
from app.db.session import engine, Base
import app.db.models

# Tự động tạo bảng dựa trên Model nếu DB chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniScraper-AI",
    description="OmniScraper-AI API to trigger and monitor scraping tasks via Celery",
    version="1.0.0"
)

app.include_router(facebook.router, prefix="/api")
app.include_router(tiktok.router, prefix="/api")
app.include_router(history.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "project": "OmniScraper-AI"}
