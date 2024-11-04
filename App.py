import pdfplumber
import logging


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    text += page.extract_text() or ""
                except Exception as e:
                    logging.warning(f"Không thể đọc trang PDF: {str(e)}")
                    continue
    except Exception as e:
        raise Exception(f"Lỗi khi đọc file PDF: {str(e)}")

    if not text.strip():
        raise Exception("Không trích xuất được văn bản từ file PDF")

    return text


def main():
    text = extract_text_from_pdf(".\\data\\04.pdf")
    print(text)


main()