from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CrawlTaskHistory

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/")
def get_crawl_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Lấy danh sách lịch sử các task đã crawl, sắp xếp theo thời gian mới nhất lên đầu.
    Giúp Extension có thể hiển thị trạng thái PENDING (Vàng), SUCCESS (Xanh), FAILED (Đỏ).
    """
    history = db.query(CrawlTaskHistory).order_by(CrawlTaskHistory.created_at.desc()).limit(limit).all()
    return {"status": "success", "data": history}
