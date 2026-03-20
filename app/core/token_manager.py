import os
import itertools
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Quản lý danh sách Token Facebook Graph API.
    Sử dụng cơ chế Round-Robin (Xoay vòng) để lấy token, giúp giảm tỷ lệ bị khoá (Rate Limit).
    Lý tưởng: Có thể thay thế list này bằng việc đọc từ Database/Redis.
    """
    def __init__(self):
        # Đọc tokens từ biến môi trường
        tokens_str = os.getenv("FB_GRAPH_TOKENS", "")
        self.tokens = [t.strip() for t in tokens_str.split(",") if t.strip()]
        
        if not self.tokens:
            logger.warning("CẢNH BÁO: Chưa cấu hình FB_GRAPH_TOKENS trong .env!")
            
        self._cycle = itertools.cycle(self.tokens) if self.tokens else None

    def get_token(self) -> Optional[str]:
        """Lấy 1 token tiếp theo trong danh sách"""
        if self._cycle:
            return next(self._cycle)
        return None

# Singleton instance để tái sử dụng trên toàn app
token_pool = TokenManager()
