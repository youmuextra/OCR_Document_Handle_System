import requests
import re

import requests
import re


class OCRProcessor:
    def __init__(self, service_url="http://127.0.0.1:8000/predict"):
        self.url = service_url
        self.doc_num_pattern = re.compile(r'([^\s]+?〔\d{4}〕\d+号|[^\s]+?\[\d{4}\]\d+号)')
        self.date_pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|二〇\d{2}年.*日)')

    def extract_doc_info(self, image_path):
        try:
            with open(image_path, "rb") as f:
                # 这里的 files={"file": f} 必须对应 server.py 中的 file: UploadFile
                response = requests.post(self.url, files={"file": f}, timeout=60)

            res_json = response.json()
            # 获取 server.py 返回的 results
            raw_data = res_json.get("data", [])

            # --- 关键修复：处理不同的数据格式 ---
            raw_lines = []
            if isinstance(raw_data, list):
                for item in raw_data:
                    # 如果 item 是字符串，直接添加
                    if isinstance(item, str):
                        raw_lines.append(item)
                    # 如果 item 是 PaddleOCR 的标准格式 [ [坐标], (文字, 置信度) ]
                    elif isinstance(item, list) and len(item) > 1 and isinstance(item[1], tuple):
                        raw_lines.append(item[1][0])
                    # 如果你的 engine 返回的是 {'raw_text': [...]}
                    elif isinstance(item, dict):
                        # 尝试取可能的文字字段
                        text = item.get("text") or item.get("raw_text")
                        if text: raw_lines.append(text)

            # 如果上面还没取到，尝试检查整体结构
            if not raw_lines and isinstance(raw_data, dict):
                raw_lines = raw_data.get("raw_text", [])

            # 打印调试，确保后端能看到文字
            print(f"DEBUG: 识别到的文字列表: {raw_lines}")

            result = {
                "title": "未识别标题",
                "doc_id": "无",
                "date": "无",
                "full_content": "\n".join(raw_lines)
            }

            if not raw_lines:
                return result

            # 提取标题逻辑
            potential_titles = [line for line in raw_lines[:6] if
                                len(line) > 5 and "〔" not in line and "号" not in line]
            if potential_titles:
                result["title"] = potential_titles[0]

            for line in raw_lines:
                # 正则提取文号
                doc_num_match = self.doc_num_pattern.search(line)
                if doc_num_match:
                    result["doc_id"] = doc_num_match.group(1)

                # 正则提取日期
                date_match = self.date_pattern.search(line)
                if date_match:
                    result["date"] = date_match.group(1)

            return result
        except Exception as e:
            print(f"OCRProcessor 发生错误: {e}")
            return {"title": "识别失败", "doc_id": "无", "date": "无", "full_content": str(e)}