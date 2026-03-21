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
        # Thiết lập httpx client giả lập trình duyệt trên mobile/mbasic (Tự động bám đuổi Redirect)
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def crawl_post(self, post_id: str, cookie_str: str) -> Dict[str, Any]:
        """
        Request vào mbasic.facebook.com để rà quét HTML của bài viết
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Cookie": cookie_str,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Đổi URL sang mbasic.facebook.com (Bản web siêu nhẹ, không có Javascript rườm rà, rất dễ parse DOM với BeautifulSoup)
        if post_id.startswith("http"):
            url = post_id.replace("www.facebook.com", "mbasic.facebook.com").replace("m.facebook.com", "mbasic.facebook.com").replace("://facebook.com", "://mbasic.facebook.com")
        else:
            url = f"https://mbasic.facebook.com/{post_id}"
            
        logger.info(f"Đang Cào HTML từ URL: {url} bằng Cookie ẩn danh.")
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            # Phân tích URL cuối cùng xem có bị trôi về trang Đăng nhập hay không (Dấu hiệu Checkpoint)
            if "/login/" in str(response.url):
                raise ValueError("Cookie bị Checkpoint chặn, khóa hoặc giới hạn (Bắt được qua Redirect).")
            
            # BÍ KÍP CHO SẾP: Lưu file HTML thô ra để mở bằng Trình duyệt soi thẻ (Inspect)
            # Sếp tha hồ xem Facebook nó trả về cấu trúc HTML như thế nào!
            with open(f"/tmp/debug_fb_post_{post_id[:10]}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            # Phân tích cú pháp HTML trả về
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- KHU VỰC SẾP TỰ DO BÓC TÁCH HTML (POST META) ---
            # Ví dụ: Facebook hay giấu nội dung trong thẻ có thuộc tính data-ft
            # content_div = soup.find("div", {"data-ft": True})
            
            title_tag = soup.find('title')
            content = title_tag.text if title_tag else "Không thể parse chi tiết Title bài viết"
            like_count = 0 # Tự viết logic bóc số Like
            
            return {
                "id": post_id,
                "content": content,
                "like_count": like_count,
                "status": "success",
                "method": "cookie_web_scraping",
                "html_length": len(response.text)
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.url}")
            location = e.response.headers.get("Location", "")
            if e.response.status_code in [403, 401] or "/login/" in location or "/cookie/" in location:
                raise ValueError("Cookie bị Checkpoint chặn, khóa hoặc giới hạn.")
            return {"id": post_id, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Lỗi cào Web Scraping: {e}")
            return {"id": post_id, "error": str(e)}

    async def crawl_comments(self, post_id: str, cookie_str: str) -> Dict[str, Any]:
        """
        Request vào m.facebook.com để tách xuất riêng mảng Bình Luận.
        Thường URL của mbasic có dạng chứa 'story.php' hoặc thêm tham số để hiện Full Comment.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Cookie": cookie_str,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        # Link cào Comment (Dùng mbasic cho siêu nhẹ)
        if post_id.startswith("http"):
            url = post_id.replace("www.facebook.com", "mbasic.facebook.com").replace("m.facebook.com", "mbasic.facebook.com").replace("://facebook.com", "://mbasic.facebook.com")
        else:
            url = f"https://mbasic.facebook.com/{post_id}"
        
        logger.info(f"Đang bóc tách COMMENTS từ URL: {url}")
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            if "/login/" in str(response.url):
                raise ValueError("Cookie bị Checkpoint chặn khi bóc Comment.")
                
            # BÍ KÍP CHO SẾP: Lưu file HTML thô ra để mở bằng Trình duyệt soi thẻ (Inspect)
            with open(f"/tmp/debug_fb_comments_{post_id[:10]}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- KHU VỰC SẾP TỰ DO BÓC TÁCH HTML (COMMENTS) ---
            # Ví dụ: mbasic facebook thường parse comment qua các div có id cụ thể
            comments_extracted = []
            
            # Giả lập lặp qua danh sách Element:
            # for cmt_div in soup.find_all("div", class_="...")
            #    comments_extracted.append({"id": "123", "text": cmt_div.text})
            
            # Trả về Mảng chứa các Comment
            return {
                "id": post_id,
                "status": "success",
                "method": "cookie_web_scraping_comments",
                "comments": [{"id": f"{post_id}_c1", "author": "Demo", "text": "Dữ liệu Comment cần sếp tự bổ sung Logic bóc."}]
            }
        except Exception as e:
            logger.error(f"Lỗi cào Web Scraping Comment: {e}")
            return {"id": post_id, "error": str(e)}
            
    async def close(self):
        await self.client.aclose()
