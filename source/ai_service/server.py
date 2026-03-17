from fastapi import FastAPI, File, UploadFile
from predict import DocumentOCREngine
import uvicorn

app = FastAPI(title="MonkeyOCR/PaddleOCR Inference Server")
engine = DocumentOCREngine()


@app.post("/predict")
async def predict_document(file: UploadFile = File(...)):
    content = await file.read()
    try:
        results = engine.inference(content)
        # --- 添加这行调试打印 ---
        print(f"DEBUG AI ENGINE OUTPUT: {results}")
        # -----------------------
        return {"code": 200, "data": results, "msg": "success"}
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()  # 获取详细的错误堆栈
        print(f"CRITICAL ERROR:\n{error_msg}")  # 在黑窗口打印
        return {"code": 500, "msg": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)