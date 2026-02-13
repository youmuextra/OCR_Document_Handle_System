from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

# 导入数据库配置与模型
from ..models.database import get_db
from ..models.document import Document
from ..core.workflow import WorkflowManager

router = APIRouter()


# --- 1. 采集与入库模块 ---

@router.post("/simulate_capture", summary="模拟高拍仪采集")
def simulate_capture(db: Session = Depends(get_db)):
    """
    模拟逻辑：读取本地 data/scans/test_doc.jpg -> AI识别 -> 存入数据库
    """
    manager = WorkflowManager()

    # 模拟图片路径（实际开发中这里由 hardware/camera.py 生成）
    test_image_path = "data/scans/test_doc.jpg"

    success, result = manager.process_new_scan(db, test_image_path)

    if success:
        return {"code": 200, "msg": "采集识别成功", "data": result}
    else:
        raise HTTPException(status_code=500, detail=f"识别失败: {result}")


# --- 2. 公文查询模块 ---

@router.get("/documents", summary="获取公文列表")
def list_documents(db: Session = Depends(get_db)):
    """
    获取所有公文，按时间倒序排列（最新的在最上面）
    """
    docs = db.query(Document).order_by(Document.create_at.desc()).all()
    return {"code": 200, "data": docs}


@router.get("/documents/{doc_id}", summary="获取单篇公文详情")
def get_document_detail(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="未找到该公文")
    return {"code": 200, "data": doc}


# --- 3. 业务流转模块 ---

@router.post("/documents/{doc_id}/sign", summary="确认签收公文")
def sign_document(
        doc_id: int = Path(..., description="公文记录的唯一ID"),
        db: Session = Depends(get_db)
):
    """
    将公文状态从 '待签收' 修改为 '已签收'
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="公文记录不存在")

    if doc.status == "已签收":
        return {"code": 200, "msg": "该公文此前已完成签收"}

    try:
        doc.status = "已签收"
        db.commit()
        db.refresh(doc)
        return {"code": 200, "msg": f"《{doc.title}》签收成功", "data": doc}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"签收失败: {str(e)}")


# --- 4. 统计看板模块 ---

@router.get("/stats", summary="获取首页统计看板")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    统计各项指标，供前端图表使用
    """
    total = db.query(Document).count()
    pending = db.query(Document).filter(Document.status == "待签收").count()
    signed = db.query(Document).filter(Document.status == "已签收").count()

    # 计算签收率
    rate = f"{(signed / total * 100):.1f}%" if total > 0 else "0%"

    return {
        "code": 200,
        "data": {
            "total_count": total,
            "pending_count": pending,
            "signed_count": signed,
            "completion_rate": rate
        }
    }