import logging
from app.core.celery_app import celery_app
from app.crawlers.tiktok.profile_crawler import TikTokCrawler
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, queue="tiktok-keyword")
def process_keyword(self, task_payload: dict):
    """
    Tương đương TiktokConsumer trong C# (lắng nghe SearchInputKeyword)
    :param task_payload: {"Keyword": "...", "ScrapScheduleId": 123}
    """
    logger.info(f"[{self.request.id}] Nhận task TikTok Keyword: {task_payload}")
    
    keyword = task_payload.get("Keyword")
    if not keyword:
        return {"status": "ignored", "reason": "No keyword"}
        
    crawler = TikTokCrawler(loop_count=settings.TIKTOK_LOOP_COUNT)
    
    try:
        # Lấy trang thái html đầu tiên
        logger.info(f"Tiến hành parse dữ liệu từ khoá: {keyword}")
        posts = crawler.crawl_keyword(keyword)
        
        # Đẩy kết quả trả về list dict -> đẩy tiếp sang queue lưu db/solr
        # VD: send_task('save_post_content', args=[posts])
        
        logger.info(f"Đã crawl {len(posts)} posts cho từ khoá: {keyword}")
        return {"status": "success", "found": len(posts)}
        
    except Exception as e:
        logger.error(f"Lỗi khi crawl TikTok keyword {keyword}: {e}")
        raise self.retry(exc=e, countdown=60)
