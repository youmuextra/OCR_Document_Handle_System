from ..core.ocr_processor import OCRProcessor
from ..models.document import Document
from sqlalchemy.orm import Session
import os

class WorkflowManager:
    def __init__(self):
        self.ocr_engine = OCRProcessor()

    def process_new_scan(self, db: Session, image_path: str):
        """
        全流程逻辑：识别 -> 数据清洗 -> 数据库持久化
        """
        if not os.path.exists(image_path):
            return False, "文件路径不存在"

        # 执行 OCR 解析
        ocr_result = self.ocr_engine.extract_doc_info(image_path)
        if "error" in ocr_result:
            return False, ocr_result["error"]

        # 映射到数据库模型
        new_doc = Document(
            title=ocr_result.get("title", "未识别标题"),
            doc_num=ocr_result.get("doc_id"),
            doc_date=ocr_result.get("date"),
            file_path=image_path,
            raw_content=ocr_result.get("full_content"),
            status="待签收"
        )

        try:
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            return True, new_doc
        except Exception as e:
            db.rollback()
            return False, f"数据库写入失败: {str(e)}"