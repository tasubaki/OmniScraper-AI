import asyncio
import logging
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.cookie_manager import CookieManager
from app.crawlers.facebook.web_crawler import FacebookWebCrawler
from app.db.session import SessionLocal
from app.db.models import CrawlTaskHistory

logger = logging.getLogger(__name__)

def update_task_status(task_id: str, st: int, msg: str = None):
    db = SessionLocal()
    try:
        task = db.query(CrawlTaskHistory).filter(CrawlTaskHistory.celery_task_id == task_id).first()
        if task:
            task.status = st
            if msg:
                task.message = str(msg)
            db.commit()
    except Exception as e:
        logger.error(f"Lỗi cập nhật CSDL: {e}")
    finally:
        db.close()


# Khởi tạo Pool Backend
cookie_manager = CookieManager()

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
        # Nhận biết sếp đang muốn Cào cái gì (Method 1: Post Meta, Method 2: Comment)
        crawl_method = task_data.get("CrawlMethod", 1)
        
        if crawl_method == 1:
            result = loop.run_until_complete(crawler.crawl_post(post_id, cookie))
        elif crawl_method == 2:
            result = loop.run_until_complete(crawler.crawl_comments(post_id, cookie))
        else:
            result = {"error": "CrawlMethod không hợp lệ"}

        # Bắt lỗi ngầm từ Data
        if "error" in result:
            logger.error(f"Lỗi ngầm từ Crawler: {result['error']}")
            update_task_status(self.request.id, -1, result["error"])
            return result
            
        logger.info(f"Kết quả Scraping bằng Cookie: {result}")
        
        # Lưu dữ liệu vào CSDL
        db = SessionLocal()
        try:
            if crawl_method == 1: # Lưu thành Bài Post
                from app.db.models import FacebookPost
                content_text = result.get("content", "")
                post = db.query(FacebookPost).filter(FacebookPost.post_id == post_id).first()
                if not post:
                    post = FacebookPost(post_id=post_id, content=content_text)
                    db.add(post)
                else:
                    post.content = content_text
                db.commit()
                
            elif crawl_method == 2: # Lưu danh sách Comment
                from app.db.models import FacebookComment
                comments_data = result.get("comments", [])
                
                for cmt in comments_data:
                    c_id = cmt.get("id")
                    comment_record = db.query(FacebookComment).filter(FacebookComment.comment_id == c_id).first()
                    if not comment_record:
                        new_comment = FacebookComment(
                            comment_id=c_id, 
                            post_id=post_id, 
                            content=cmt.get("text", ""), 
                            author_name=cmt.get("author", "Ẩn danh")
                        )
                        db.add(new_comment)
                db.commit()
                
        except Exception as db_e:
            logger.error(f"Lỗi khi save data {db_e}")
        finally:
            db.close()
            
        update_task_status(self.request.id, 2)
        return {"status": "success", "post_id": post_id, "data": result}
        
    except ValueError as e:
        logger.warning(f"Cookie bị Checkpoint hoặc Limit: {e}")
        cookie_manager.mark_cookie_bad(cookie)
        update_task_status(self.request.id, -1, str(e))
        raise self.retry(exc=e, countdown=30)
    except Exception as e:
        logger.error(f"Lỗi chưa xác định trong quá trình Cào: {e}")
        update_task_status(self.request.id, -1, str(e))
        raise self.retry(exc=e, countdown=10)
    finally:
        loop.run_until_complete(crawler.close())
