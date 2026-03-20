import httpx
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FacebookWebCrawler:
    """
    Cào dữ liệu Facebook bằng kỹ thuật Web Scraping truyền thống.
    Sử dụng mbasic.facebook.com hoặc www.facebook.com kèm Cookie.
    """
    def __init__(self):
        # Thiết lập httpx client giả lập trình duyệt trên mobile/mbasic
        self.client = httpx.AsyncClient(timeout=15.0)

    async def crawl_post(self, post_id: str, cookie_str: str) -> Dict[str, Any]:
        """
        Request vào mbasic.facebook.com để rà quét HTML của bài viết
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie_str,
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
        }
        
        # Mbasic siêu nhẹ, ít JS, dễ parse bằng BeautifulSoup hơn bản chuẩn
        url = f"https://mbasic.facebook.com/{post_id}"
        logger.info(f"Đang Cào HTML từ URL mbasic: {url} bằng Cookie ẩn danh.")
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            # Phân tích cú pháp HTML trả về
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Mock trích xuất dữ liệu: Thẻ Title bài viết
            title_tag = soup.find('title')
            content = title_tag.text if title_tag else "Không thể parse chi tiết Title bài viết"
            
            # Dò tìm element text thực tế trên trang mbasic (ID cấu trúc mbasic)
            # body_text = soup.find("div", {"id": "m_story_permalink_view"}) ...
            
            return {
                "id": post_id,
                "content": content,
                "status": "success",
                "method": "cookie_web_scraping",
                "html_length": len(response.text)
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code}")
            if e.response.status_code in [403, 401, 302]: # 302 ép login
                raise ValueError("Cookie bị Checkpoint chặn, khóa hoặc giới hạn.")
            return {"id": post_id, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Lỗi cào Web Scraping: {e}")
            return {"id": post_id, "error": str(e)}
            
    async def close(self):
        await self.client.aclose()
