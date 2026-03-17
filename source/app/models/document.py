from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 用户表
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String) # 建议实际开发用哈希加密

# 发文表（新增）
class Dispatch(Base):
    __tablename__ = "dispatches"
    id = Column(Integer, primary_key=True, index=True)
    doc_num = Column(String)       # 文号
    title = Column(String)         # 标题
    receiver_unit = Column(String)  # 发往单位
    handler = Column(String)       # 经办人
    date = Column(String)          # 日期
    remark = Column(Text)          # 备注
    created_at = Column(DateTime, default=datetime.now)

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