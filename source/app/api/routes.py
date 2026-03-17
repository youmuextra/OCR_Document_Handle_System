from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

# 导入数据库配置与模型
from ..models.database import get_db
from ..models.document import Document, User, Dispatch
from ..core.workflow import WorkflowManager

import os

router = APIRouter()


# --- 1. 采集与入库模块 ---

@router.post("/simulate_capture", summary="模拟高拍仪采集")
def simulate_capture(db: Session = Depends(get_db)):
    """
    模拟逻辑：读取本地 data/scans/test_doc.jpg -> AI识别 -> 存入数据库
    """
    manager = WorkflowManager()

    # 模拟图片路径（实际开发中这里由 hardware/camera.py 生成）
    test_image_path = "data/scans/File03_01.jpg"

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

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # 1. 统计收文总数
    total_docs = db.query(Document).count()

    # 2. 统计发文总数 (Dispatch 表)
    total_dispatches = db.query(Dispatch).count()

    # 3. 统计待办事项 (状态为“待签收”的收文)
    pending_docs = db.query(Document).filter(Document.status == "待签收").count()

    return {
        "code": 200,
        "data": {
            "total_docs": total_docs,
            "total_dispatches": total_dispatches,
            "pending_docs": pending_docs
        }
    }

# --- 5. 删除数据模块 ---

@router.delete("/documents/{doc_id}", summary="删除指定公文")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    # 1. 查找记录
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="未找到该公文记录")

    try:
        # 2. (可选) 删除对应的物理图片文件
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                print(f"警告：物理文件删除失败: {e}")

        # 3. 删除数据库记录
        db.delete(doc)
        db.commit()
        return {"code": 200, "msg": "公文及其附件已成功删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")




@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.get("username")).first()
    if not user or user.password != data.get("password"):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"code": 200, "msg": "登录成功", "data": {"user_id": user.id, "username": user.username}}

@router.post("/dispatches")
def create_dispatch(data: dict, db: Session = Depends(get_db)):
    new_dispatch = Dispatch(
        doc_num=data.get("doc_num"),
        title=data.get("title"),
        receiver_unit=data.get("receiver_unit"),
        handler=data.get("handler"),
        date=data.get("date"),
        remark=data.get("remark")
    )
    db.add(new_dispatch)
    db.commit()
    return {"code": 200, "msg": "发文登记成功"}

# 别忘了更新原来的 list_documents 接口，增加一个 list_dispatches 接口查看发文
@router.get("/dispatches")
def list_dispatches(db: Session = Depends(get_db)):
    return {"code": 200, "data": db.query(Dispatch).order_by(Dispatch.created_at.desc()).all()}