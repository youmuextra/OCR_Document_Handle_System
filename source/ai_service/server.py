from fastapi import FastAPI, File, UploadFile
from predict import DocumentOCREngine
import uvicorn

app = FastAPI(title="MonkeyOCR/PaddleOCR Inference Server")
engine = DocumentOCREngine()


@app.post("/predict")
async def predict_document(file: UploadFile = File(...)):
    # 读取上传的文件内容
    content = await file.read()

    # 调用推理引擎
    try:
        results = engine.inference(content)
        return {"code": 200, "data": results, "msg": "success"}
    except Exception as e:
        return {"code": 500, "msg": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)