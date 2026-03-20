import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class CookieManager:
    """
    Quản lý danh sách Cookies Facebook theo chiến lược Round-Robin.
    Tự động loại bỏ tạm thời các Cookies bị block (403/429).
    """
    def __init__(self, cookies_str: str):
        self.cookies: List[str] = [c.strip() for c in cookies_str.split(',') if c.strip()]
        self.current_index = 0
        self.bad_cookies = set()

    def get_cookie(self) -> Optional[str]:
        if not self.cookies:
            logger.warning("Không có Cookies nào trong Pool để chạy Web Scraping.")
            return None
        
        available_cookies = [c for c in self.cookies if c not in self.bad_cookies]
        if not available_cookies:
            logger.warning("Toàn bộ Cookies hiện tại đã bị Block. Xóa trạng thái Block để thử lại từ đầu.")
            self.bad_cookies.clear()
            available_cookies = self.cookies

        cookie = available_cookies[self.current_index % len(available_cookies)]
        self.current_index += 1
        return cookie

    def mark_cookie_bad(self, cookie: str):
        """Đánh dấu Cookie này bị lỗi (Block hoặc hết hạn)"""
        logger.warning(f"Đánh dấu Cookie là BAD: {cookie[:20]}...")
        self.bad_cookies.add(cookie)
