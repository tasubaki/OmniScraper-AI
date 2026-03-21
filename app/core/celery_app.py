from celery import Celery
from kombu import Queue
from app.core.config import settings

celery_app = Celery(
    "omni_scraper",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=[
        "app.workers.facebook_worker",
        "app.workers.tiktok_worker"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    # Cấu hình worker concurrency (VD: 4 luồng)
    worker_concurrency=4,
    # Khai báo tập trung danh sách các Queue tại đây để Worker tự động dỏng tai lên nghe
    task_queues=(
        Queue('celery', routing_key='celery'),
        Queue('facebook-meta', routing_key='facebook-meta'),
        Queue('tiktok-keyword', routing_key='tiktok-keyword'),
    ),
    # Route tasks vào các queue tương ứng
    task_routes={
        "facebook.crawl_meta": {"queue": "facebook-meta"},
        "app.workers.tiktok_worker.process_keyword": {"queue": "tiktok-keyword"},
    }
)
