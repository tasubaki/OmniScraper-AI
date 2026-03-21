import logging
from typing import Optional
from app.db.session import SessionLocal
from app.db.models import FBCookie

logger = logging.getLogger(__name__)

class CookieManager:
    """
    Quản lý danh sách Cookies Facebook theo chiến lược Round-Robin.
    Kết nối thẳng vào Database để chấn chỉnh trạng thái is_active theo Real-time.
    """
    def __init__(self):
        self.current_index = 0

    def get_cookie(self) -> Optional[str]:
        db = SessionLocal()
        try:
            active_cookies = db.query(FBCookie).filter(FBCookie.is_active == True).all()
            if not active_cookies:
                logger.warning("Toàn bộ Cookies trong DB đã tử trận hoặc rỗng. Extension cần Sync đợt mới!")
                return None
            
            cookie = active_cookies[self.current_index % len(active_cookies)]
            self.current_index += 1
            return cookie.cookie_string
        except Exception as e:
            logger.error(f"Lỗi Query Cookie từ DB: {e}")
            return None
        finally:
            db.close()

    def mark_cookie_bad(self, cookie_str: str):
        """Đánh dấu Cookie này bị lỗi (Block hoặc hết hạn) thẳng vào DB"""
        db = SessionLocal()
        import re
        try:
            logger.warning(f"Bắn lệnh án tử vào DB (is_active=False) cho Cookie: {cookie_str[:30]}...")
            # Trích xuất c_user để query an toàn thay vì map toàn bộ chuỗi Text siêu dài
            match = re.search(r"c_user=(\d+)", cookie_str)
            if match:
                c_user = match.group(1)
                cookie_record = db.query(FBCookie).filter(FBCookie.cookie_string.like(f"%c_user={c_user}%")).first()
            else:
                cookie_record = db.query(FBCookie).filter(FBCookie.cookie_string == cookie_str).first()
                
            if cookie_record:
                cookie_record.is_active = False
                db.commit()
                logger.info(f"Đã cập nhật is_active=False cho Cookie chứa c_user={match.group(1) if match else 'N/A'}")
            else:
                logger.error("Không tìm thấy Cookie trong DB để đánh dấu BAD!")
        except Exception as e:
            logger.error(f"Lỗi khi sát hại Cookie trong DB: {e}")
        finally:
            db.close()
