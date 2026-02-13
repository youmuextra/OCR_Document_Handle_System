from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.document import Base

# 在项目根目录下创建数据库文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./gov_doc.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # 自动根据 Document 模型创建表结构
    Base.metadata.create_all(bind=engine)

# 依赖注入函数：用于在 FastAPI 路由中获取数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()