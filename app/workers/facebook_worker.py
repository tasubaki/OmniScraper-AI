import logging
from app.core.celery_app import celery_app
from app.crawlers.facebook.post_crawler import FacebookGraphCrawler
from app.core.token_manager import token_pool

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, queue="facebook-meta")
def process_metadata(self, task_payload: dict):
    """
    Tương đương PostMetaConsumer trong C# (chế độ CrawlMethod: Metadata, Comment, Share)
    :param task_payload: {"url": "...", "post_id": "...", "CrawlMethod": 1}
    """
    logger.info(f"[{self.request.id}] Nhận task Facebook Meta: {task_payload}")
    
    crawl_method = task_payload.get("CrawlMethod")
    post_id = task_payload.get("post_id")
    
    try:
        # Lấy token từ pool
        token = token_pool.get_token()
        if not token:
            raise Exception("Không có Facebook Graph Token nào khả dụng!")
            
        crawler = FacebookGraphCrawler(token)
        result = None
        
        # Giả lập logic crawl
        if crawl_method == 1:
            logger.info(f"Crawl Metadata cho post {post_id}")
            result = crawler.get_meta(post_id)
        elif crawl_method == 2:
            logger.info(f"Crawl Comment cho post {post_id}")
            # result = crawler.get_comments(post_id)
        else:
            logger.info(f"Bỏ qua CrawlMethod không hỗ trợ: {crawl_method}")
            
        return {"status": "success", "post_id": post_id, "data": result}
        
    except Exception as e:
        logger.error(f"Lỗi khi crawl Facebook: {e}")
        raise self.retry(exc=e, countdown=60)
