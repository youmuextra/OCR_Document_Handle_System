from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.document import Document


class StatsService:
    @staticmethod
    def get_basic_stats(db: Session):
        # 1. 总收文量
        total_count = db.query(Document).count()
        # 2. 各状态统计 (待签收/已签收)
        status_distribution = db.query(
            Document.status, func.count(Document.id)
        ).group_by(Document.status).all()

        return {
            "total": total_count,
            "distribution": dict(status_distribution)
        }