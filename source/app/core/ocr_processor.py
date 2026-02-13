import requests
import re


class OCRProcessor:
    def __init__(self, service_url="http://127.0.0.1:8000/predict"):
        self.url = service_url
        # 预编译公文号正则：匹配如 “发〔2026〕1号” 或 “办字[2025]12号”
        self.doc_num_pattern = re.compile(r'([^\s]+?〔\d{4}〕\d+号|[^\s]+?\[\d{4}\]\d+号)')
        # 预编译日期正则：匹配中文日期或阿拉伯数字日期
        self.date_pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|二〇\d{2}年.*日)')

    def extract_doc_info(self, image_path):
        try:
            with open(image_path, "rb") as f:
                response = requests.post(self.url, files={"file": f}, timeout=15)

            data = response.json()
            raw_lines = data.get("data", {}).get("raw_text", [])

            # 基础结果字典
            result = {"title": "", "doc_id": "", "date": "", "full_content": "\n".join(raw_lines)}

            if not raw_lines:
                return result

            # 1. 提取标题：通常红头公文标题在第1-3行之间，且字数较多
            # 过滤掉可能的“红头”机构名称，选取最像标题的行
            potential_titles = [line for line in raw_lines[:5] if len(line) > 5 and "第" not in line]
            if potential_titles:
                result["title"] = potential_titles[0]

            for line in raw_lines:
                # 2. 正则提取文号
                doc_num_match = self.doc_num_pattern.search(line)
                if doc_num_match:
                    result["doc_id"] = doc_num_match.group(1)

                # 3. 正则提取日期
                date_match = self.date_pattern.search(line)
                if date_match:
                    result["date"] = date_match.group(1)

            return result
        except Exception as e:
            return {"error": str(e)}