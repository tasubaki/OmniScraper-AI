from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey

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
    status = Column(Integer, default=1) # 1: PENDING, 2: SUCCESS, -1: FAILED
    message = Column(Text, nullable=True) # Ghi chú lỗi nếu có
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FacebookProfile(Base):
    """ Thông tin người dùng / Fanpage Facebook """
    __tablename__ = "fb_profiles"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    profile_url = Column(String(500))
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

class FacebookPost(Base):
    """ Thông tin Bài Post Facebook """
    __tablename__ = "fb_posts"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), unique=True, index=True, nullable=False)
    author_uid = Column(String(255), index=True) # ID người đăng
    content = Column(Text)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    posted_at = Column(DateTime(timezone=True))
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

class FacebookComment(Base):
    """ Thông tin Bình luận trong 1 bài Post Facebook """
    __tablename__ = "fb_comments"
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String(255), unique=True, index=True, nullable=False)
    post_id = Column(String(255), index=True, nullable=False)
    author_name = Column(String(255))
    author_uid = Column(String(255))
    content = Column(Text)
    like_count = Column(Integer, default=0)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

class TikTokUser(Base):
    """ Thông tin User TikTok """
    __tablename__ = "tiktok_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(255))
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    signature = Column(Text) # Tiểu sử
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

class TikTokVideo(Base):
    """ Thông tin Video TikTok """
    __tablename__ = "tiktok_videos"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(255), unique=True, index=True, nullable=False)
    author_username = Column(String(255), index=True)
    description = Column(Text)
    play_count = Column(Integer, default=0)
    digg_count = Column(Integer, default=0) # like
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    posted_at = Column(DateTime(timezone=True))
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

