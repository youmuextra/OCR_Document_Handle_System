import cv2
import numpy as np
from paddleocr import PaddleOCR

class DocumentOCREngine:
    def __init__(self):
        # 初始化 PaddleOCR，使用中文模型
        # use_angle_cls=True 自动旋转纠正，适合高拍仪场景
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        print("AI Service: PaddleOCR Engine Loaded.")

    def inference(self, image_bytes):
        # 1. 将字节流转换为 OpenCV 格式
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2. 执行识别
        result = self.ocr.ocr(img, cls=True)

        # 3. 结果清洗与结构化 (简单示例)
        # 实际公文场景需结合版面分析提取：文号、标题、日期
        parsed_data = {
            "raw_text": [],
            "structured": {
                "doc_title": "",
                "doc_num": "",
                "date": ""
            }
        }

        if result[0]:
            for line in result[0]:
                text = line[1][0]
                parsed_data["raw_text"].append(text)
                # 示例简单逻辑：包含“第”和“号”的通常是文号
                if "第" in text and "号" in text:
                    parsed_data["structured"]["doc_num"] = text

        return parsed_data