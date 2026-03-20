from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.session import Base

class FBCookie(Base):
    """
    Lưu trữ Cookie của Facebook đẩy từ Extension về.
    """
    __tablename__ = "fb_cookies"

    id = Column(Integer, primary_key=True, index=True)
    cookie_string = Column(Text, nullable=False, unique=True)
    is_active = Column(Boolean, default=True) # Đánh dấu cookie còn sống hay đã bị chặn thảm đỏ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CrawlTaskHistory(Base):
    """
    Lưu lại lịch sử các lệnh Crawl được gọi từ Extension hoặc Swagger.
    """
    __tablename__ = "crawl_task_history"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False) # 'facebook' hoặc 'tiktok'
    target_id = Column(String(255), nullable=False) # username tiktok hoặc post_id facebook
    task_type = Column(String(100), nullable=False) # 'crawl_user', 'crawl_post'
    celery_task_id = Column(String(255), nullable=True) # ID của task trong RabbitMQ/Celery
    status = Column(String(50), default="PENDING") # PENDING, SUCCESS, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
