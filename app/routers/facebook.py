from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from app.core.celery_app import celery_app
from app.crawlers.facebook.post_crawler import FacebookGraphCrawler
from app.core.token_manager import token_pool

router = APIRouter(prefix="/facebook", tags=["Facebook Crawler"])

class CrawlPostRequest(BaseModel):
    post_id: str
    crawl_method: int = 1 # 1: Meta, 2: Comment, 3: Share

class CrawlPageRequest(BaseModel):
    page_id: str
    limit: int = 10

@router.post("/crawl-post")
def crawl_single_post(request: CrawlPostRequest):
    """
    Kích hoạt task Celery để scrape 1 bài viết Facebook cụ thể.
    """
    task = celery_app.send_task(
        "app.workers.facebook_worker.process_metadata",
        kwargs={
            "task_payload": {
                "post_id": request.post_id,
                "CrawlMethod": request.crawl_method
            }
        },
        queue="facebook-meta"
    )
    return {"status": "Task Queued", "task_id": task.id, "post_id": request.post_id}

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
