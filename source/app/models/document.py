from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)      # 公文标题
    doc_num = Column(String(100), nullable=True)    # 发文字号 (如: [2026] 1号)
    doc_date = Column(String(50), nullable=True)    # 公文日期
    file_path = Column(String(500))                 # 高拍仪图片存储路径
    raw_content = Column(Text)                      # OCR 全文识别内容
    status = Column(String(20), default="待签收")   # 流转状态: 待签收/已签收
    create_at = Column(DateTime, default=datetime.now)

    # 预留给手写板签名的字段
    sign_img_path = Column(String(500), nullable=True)