import json
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class TikTokCrawler:
    """
    Class thay thế ParseToProfile & ServiceGetLink cho TikTok trong dự án gốc (C#).
    """
    def __init__(self, loop_count: int = 5):
        self.loop_count = loop_count
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=30.0
        )
        
    def _extract_next_data(self, html_content: str) -> dict:
        """
        Dùng BeautifulSoup tìm thẻ script id="__NEXT_DATA__"
        """
        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        
        if not script_tag or not script_tag.string:
            logger.warning("Không tìm thấy thẻ __NEXT_DATA__ trong HTML.")
            return {}
            
        try:
            return json.loads(script_tag.string)
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi Parse JSON: {e}")
            return {}
            
    def _parse_posts_from_json(self, json_data: dict) -> list:
        """Trích xuất post metadata từ cục JSON"""
        # Logic bóc chi tiết Data từ __NEXT_DATA__ (ItemList -> items)
        # Sẽ tuỳ thuộc vào cấu trúc TikTok JSON hiện tại
        posts = []
        try:
            item_module = json_data.get("props", {}).get("pageProps", {}).get("itemModule", {})
            for video_id, data in item_module.items():
                posts.append({
                    "id": video_id,
                    "desc": data.get("desc", ""),
                    "author": data.get("author", "")
                })
        except Exception as e:
            logger.error(f"Lỗi extract itemModule: {e}")
        return posts

    def call_api_scroll(self, cursor: str, sec_uid: str) -> dict:
        """
        Gọi API Scroll như service.callApiScroll trong C#
        """
        # Đây là mock url API thật của TikTok tuỳ thuộc request Params
        url = f"https://www.tiktok.com/api/post/item_list/?secUid={sec_uid}&cursor={cursor}&count=30"
        res = self.client.get(url)
        if res.status_code == 200:
            return res.json()
        return {}

    def crawl_keyword(self, keyword: str) -> list:
        # Đây là URL test search / profile
        # Tuỳ thuộc Input mà ta đổi URL. (Ví dụ URL search)
        url = f"https://www.tiktok.com/search?q={keyword}"
        response = self.client.get(url)
        
        if response.status_code != 200:
            logger.error(f"Khởi tạo Fetch HTML thất bại: {response.status_code}")
            return []
            
        json_data = self._extract_next_data(response.text)
        if not json_data:
            return []
            
        # Lấy được lượng post đầu tiên
        all_posts = self._parse_posts_from_json(json_data)
        
        # Giả lập scroll API (giống vòng lặp bên C#)
        # dataNextRequest = service.getDataNextRequest(...)
        cursor = "mock_cursor"
        sec_uid = "mock_secUid"
        
        for _ in range(self.loop_count):
            if cursor:
                logger.info(f"Cuộn trang TikTok bằng Cursor: {cursor}")
                # dataResult = self.call_api_scroll(cursor, sec_uid)
                # Parse further
            else:
                break
                
        return all_posts
