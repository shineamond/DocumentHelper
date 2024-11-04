import pdfplumber
import logging
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_text_from_pdf(pdf_path):
    sensitive_info_patterns = [
        r'\b\d{9,12}\b',
        r'\b\d{10}\b',
        r'\b[\w\.-]+@[\w\.-]+\.\w+\b'
    ]
    sensitive_info_patterns = [re.compile(pattern) for pattern in sensitive_info_patterns]

    bullet_patterns = [
        r'^\s*[\u2022\u25E6\u26AB]\s+',
        r'^\s*[-•∙◦◎⦿⦾]\s+'
    ]
    bullet_patterns = [re.compile(pattern, re.MULTILINE) for pattern in bullet_patterns]

    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    filtered_text = page.extract_text() or ""

                    for pattern in sensitive_info_patterns:
                        filtered_text = pattern.sub('', filtered_text)

                    for pattern in bullet_patterns:
                        filtered_text = pattern.sub('', filtered_text)

                    text += filtered_text

                except Exception as e:
                    logging.warning(f"Không thể đọc trang PDF: {str(e)}")
                    continue
    except Exception as e:
        raise Exception(f"Lỗi khi đọc file PDF: {str(e)}")

    if not text.strip():
        raise Exception("Không trích xuất được văn bản từ file PDF")

    return text


def create_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200, length_function = len)
    chunks = text_splitter.split_text(text)

    return chunks


def main():
    text = extract_text_from_pdf(".\\data\\04.pdf")
    chunks = create_chunks(text)
    print(chunks)

main()