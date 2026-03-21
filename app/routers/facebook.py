from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import FBCookie, CrawlTaskHistory
from app.core.celery_app import celery_app
from app.crawlers.facebook.post_crawler import FacebookGraphCrawler
from app.core.token_manager import token_pool

router = APIRouter(prefix="/facebook", tags=["Facebook Crawler"])

class CrawlPostRequest(BaseModel):
    post_id: str
    crawl_method: int = 1 # 1: Meta, 2: Comment, 3: Share

class CookieSyncRequest(BaseModel):
    cookie_text: str

class CrawlPageRequest(BaseModel):
    page_id: str
    limit: int = 10

@router.post("/crawl-post")
def crawl_single_post(request: CrawlPostRequest, db: Session = Depends(get_db)):
    """
    Kích hoạt task Celery để scrape 1 bài viết Facebook cụ thể.
    """
    task = celery_app.send_task(
        "facebook.crawl_meta",
        kwargs={
            "task_data": {
                "post_id": request.post_id,
                "CrawlMethod": request.crawl_method
            }
        },
        queue="facebook-meta"
    )
    
    history = CrawlTaskHistory(platform="facebook", target_id=request.post_id, task_type="crawl_post", celery_task_id=task.id)
    db.add(history)
    db.commit()
    
    return {"status": "Task Queued", "task_id": task.id, "post_id": request.post_id}

@router.post("/internal/sync-cookie", tags=["Internal"])
async def sync_cookie(request: CookieSyncRequest, db: Session = Depends(get_db)):
    """
    API nội sinh dành cho OmniScraper-Extension tự động ném Cookie lấy được lưu vào DB.
    """
    cookie_text = request.cookie_text
    
    existing_cookie = db.query(FBCookie).filter(FBCookie.cookie_string == cookie_text).first()
    if not existing_cookie:
        new_cookie = FBCookie(cookie_string=cookie_text)
        db.add(new_cookie)
        db.commit()
    
    total = db.query(FBCookie).count()
    return {
        "status": "success", 
        "message": "Cookie nhận an toàn và đã lưu DB!", 
        "total_active_cookies": total
    }

@router.post("/crawl-page")
def crawl_page_posts(request: CrawlPageRequest, background_tasks: BackgroundTasks):
    """
    Lấy danh sách các bài viết gần nhất của 1 Page và kích hoạt worker phân tán (Celery)
    để crawl song song từng bài.
    """
    token = token_pool.get_token()
    if not token:
        raise HTTPException(status_code=500, detail="Không lấy được Facebook Token từ hệ thống")
        
    def fetch_and_dispatch():
        # Gọi Graph API / ID Page để lấy list các bài viết mới
        crawler = FacebookGraphCrawler(token)
        # Mock logic lấy danh sách post_id:
        mock_posts = [f"{request.page_id}_post1", f"{request.page_id}_post2"]
        
        for p_id in mock_posts:
            # Gửi từng post vào Queue "facebook-meta" để các worker xử lý song song
            celery_app.send_task(
                "app.workers.facebook_worker.process_metadata",
                kwargs={
                    "task_payload": {
                        "post_id": p_id,
                        "CrawlMethod": 1 # Lấy Metadata
                    }
                },
                queue="facebook-meta"
            )
            
    # Chạy ngầm việc fetch d/s bài viết rồi nhồi vào Queue
    background_tasks.add_task(fetch_and_dispatch)
            
    return {"status": "Page Crawl Initiated", "message": f"Hệ thống đang fetch Max {request.limit} posts của Page {request.page_id} và gửi cho Worker."}
