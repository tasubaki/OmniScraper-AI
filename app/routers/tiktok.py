from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CrawlTaskHistory
from typing import Optional
from app.workers.tiktok_worker import process_keyword
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tiktok",
    tags=["TikTok Crawler"]
)

class TikTokUserRequest(BaseModel):
    username: str
    loop_count: Optional[int] = 3

class TikTokVideoRequest(BaseModel):
    video_id: str

class CookieSyncRequest(BaseModel):
    cookie_text: str

@router.post("/sync-cookie")
def sync_tiktok_cookie(request: CookieSyncRequest):
    """
    (Dummy) Nhận cookie từ Extension. 
    Hiện tại TikTok Crawler chưa cần dùng Cookie DB để chạy, nhưng mở Endpoint để Extension không bị 404.
    """
    return {
        "status": "success", 
        "message": "Đã nhận Cookie TikTok (Chưa lưu DB vì chưa cần thiết)"
    }

@router.post("/crawl-user")
def crawl_user(request: TikTokUserRequest, db: Session = Depends(get_db)):
    """
    Kích hoạt Worker thu thập dữ liệu User TikTok (Profile & Videos)
    """
    try:
        # Gửi task vào RabbitMQ queue -> Celery Worker xử lý
        task = process_keyword.delay({"Keyword": request.username, "LoopCount": request.loop_count})
        
        history = CrawlTaskHistory(
            platform="tiktok",
            target_id=request.username,
            task_type="crawl_user",
            celery_task_id=task.id
        )
        db.add(history)
        db.commit()
        
        return {
            "status": "success", 
            "task_id": task.id, 
            "message": f"Đã gửi lệnh crawl user '{request.username}' cho TikTok Worker"
        }
    except Exception as e:
        logger.error(f"Error triggering tiktok user task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl-video")
def crawl_video(request: TikTokVideoRequest):
    """
    (Chức năng mở rộng) Tiến hành Crawl thông tin cụ thể của 1 Video TikTok
    """
    return {
        "status": "success", 
        "message": f"Đã nhận lệnh crawl video {request.video_id} (Tính năng đang chờ mở rộng Core API TikTok)"
    }
