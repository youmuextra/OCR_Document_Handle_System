import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 1. 自动处理路径依赖
# 确保项目根目录在 sys.path 中，防止 import app 失败
basedir = os.path.dirname(os.path.abspath(__file__))
if basedir not in sys.path:
    sys.path.append(basedir)

# 2. 导入自定义模块
from app.api.routes import router as doc_router
from app.models.database import init_db

# 3. 初始化 FastAPI 实例
app = FastAPI(
    title="政务公文智能管理平台",
    description="后端 API 服务 - 支持 OCR 识别、公文流转与统计分析",
    version="1.0.0"
)

# 4. 配置 CORS 跨域 (关键：解决 index.html 无法访问 API 的问题)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 挂载静态资源目录
# 这样通过 http://127.0.0.1:5000/scans/xxx.jpg 就能访问高拍仪图片
if not os.path.exists("data/scans"):
    os.makedirs("data/scans")
app.mount("/scans", StaticFiles(directory="data/scans"), name="scans")

# 6. 数据库初始化钩子
@app.on_event("startup")
def on_startup():
    print("--- 正在检查数据库表结构 ---")
    init_db()
    print("--- 数据库就绪 ---")

# 7. 注册业务路由
# 所有接口将以 /api/v1 开头
app.include_router(doc_router, prefix="/api/v1", tags=["业务接口"])

# 8. 根路径导航（可选：直接托管前端 index.html）
@app.get("/")
async def read_index():
    # 如果 index.html 在 main.py 同级目录，可以直接返回
    index_path = os.path.join(basedir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Service Running", "message": "请访问 /docs 查看接口文档"}

# 9. 启动入口
if __name__ == "__main__":
    # 使用 host="0.0.0.0" 可以让局域网内的设备（如移动端）访问
    # 端口 5000，不要与 ai_service 的 8000 冲突
    print("系统已启动，请在浏览器访问 http://127.0.0.1:5000")
    uvicorn.run(app, host="127.0.0.1", port=5000)