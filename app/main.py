from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import facebook, tiktok, history
from app.db.session import engine, Base
import app.db.models
from sqlalchemy import text

# Migration tự động: Ép kiểu cột status thành integer và thêm message
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE crawl_task_history DROP COLUMN IF EXISTS status CASCADE;"))
        conn.execute(text("ALTER TABLE crawl_task_history ADD COLUMN status INTEGER DEFAULT 1;"))
        conn.execute(text("ALTER TABLE crawl_task_history ADD COLUMN message TEXT;"))
except Exception as e:
    pass

# Tự động tạo bảng dựa trên Model nếu DB chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniScraper-AI",
    description="OmniScraper-AI API to trigger and monitor scraping tasks via Celery",
    version="1.0.0"
)

# Cấu hình CORS để Extension (React/Browser) có thể gọi API mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép gọi từ mọi Nguồn (kể cả Extension chrome-extension://)
    allow_credentials=True,
    allow_methods=["*"], # Cho phép GET, POST, OPTIONS...
    allow_headers=["*"],
)

app.include_router(facebook.router, prefix="/api")
app.include_router(tiktok.router, prefix="/api")
app.include_router(history.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "project": "OmniScraper-AI"}
