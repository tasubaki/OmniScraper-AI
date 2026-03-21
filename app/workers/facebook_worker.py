import asyncio
import logging
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.cookie_manager import CookieManager
from app.crawlers.facebook.web_crawler import FacebookWebCrawler
from app.db.session import SessionLocal
from app.db.models import CrawlTaskHistory

logger = logging.getLogger(__name__)

def update_task_status(task_id: str, st: str):
    db = SessionLocal()
    try:
        task = db.query(CrawlTaskHistory).filter(CrawlTaskHistory.celery_task_id == task_id).first()
        if task:
            task.status = st
            db.commit()
    except Exception as e:
        logger.error(f"Lỗi cập nhật CSDL: {e}")
    finally:
        db.close()


# Khởi tạo Pool Backend
cookie_manager = CookieManager(settings.fb_cookies)

@celery_app.task(name="facebook.crawl_meta", bind=True, max_retries=3)
def process_metadata(self, task_data: dict):
    """
    Xử lý tác vụ cào bài viết Facebook sử dụng kỹ thuật Web Scraping (truyền Cookie)
    thay vì Graph API Token. Kỹ thuật này giúp tránh rào cản Page Public Content Access.
    """
    logger.info(f"Worker nhận task Facebook Meta: {task_data}")
    post_id = task_data.get("post_id")
    
    # Rút một phiên bản Cookie từ kho đạn
    cookie = cookie_manager.get_cookie()
    if not cookie:
        logger.error("Pool hiện tại không có Cookie nào rảnh. Thử lại sau.")
        raise self.retry(countdown=60)

    # Khởi tạo Core HTTP Web Crawler ẩn danh
    crawler = FacebookWebCrawler()
    
    # Biến Celery Sync func thành Async chạy mượt mà
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        # Chạy logic Scrape HTTP Request
        result = loop.run_until_complete(crawler.crawl_post(post_id, cookie))
        logger.info(f"Kết quả Scraping bằng Cookie: {result}")
        update_task_status(self.request.id, "SUCCESS")
        return {"status": "success", "post_id": post_id, "data": result}
        
    except ValueError as e:
        logger.warning(f"Cookie bị Checkpoint hoặc Limit: {e}")
        cookie_manager.mark_cookie_bad(cookie)
        raise self.retry(exc=e, countdown=30)
    except Exception as e:
        logger.error(f"Lỗi chưa xác định trong quá trình Cào: {e}")
        update_task_status(self.request.id, "FAILED")
        raise self.retry(exc=e, countdown=10)
    finally:
        loop.run_until_complete(crawler.close())
