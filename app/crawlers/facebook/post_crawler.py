import logging
import httpx

logger = logging.getLogger(__name__)

class FacebookGraphCrawler:
    """
    Class thay thế các method gọi Graph API (FeedPostService, UserDetailService...) 
    bên dự án FacebookCrawl (C#).
    """
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://graph.facebook.com/v19.0"
        self.client = httpx.Client(timeout=30.0)
        
    def get_meta(self, post_id: str) -> dict:
        """
        Lấy thông tin tổng quan của một bài viết (Số like, share, comment, content...)
        Tương đương logic lấy bài post trong C# sử dụng Graph API.
        """
        url = f"{self.base_url}/{post_id}"
        params = {
            "access_token": self.token,
            "fields": "id,message,created_time,shares,comments.summary(true),reactions.summary(true)"
        }
        
        try:
            logger.info(f"Crawl Meta cho Post ID: {post_id}")
            # response = self.client.get(url, params=params)
            # if response.status_code == 200:
            #     return response.json()
            # else:
            #     logger.error(f"Lỗi Graph API: {response.text}")
            #     return {}
            
            # Mock Data
            return {
                "id": post_id,
                "message": "Mock Facebook Post Content",
                "shares": {"count": 12},
                "comments": {"summary": {"total_count": 5}},
                "reactions": {"summary": {"total_count": 100}}
            }
            
        except httpx.RequestError as e:
            logger.error(f"Lỗi HTTP Request FB Graph: {e}")
            return {}
