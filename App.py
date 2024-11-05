import os
import pdfplumber
import logging
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS


class QuizGenerator:
    def __init__(self, groq_api_key):
        os.environ["GROQ_API_KEY"] = groq_api_key
        self.embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatGroq(temperature = 0.7, model_name = "llama3-70b-8192")

    @staticmethod
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

    @staticmethod
    def create_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=200,
                                                       length_function=len)
        chunks = text_splitter.split_text(text)

        return chunks

    def generate_quiz(self, vectorstore, num_questions):
        qa = RetrievalQA.from_chain_type(llm=self.llm,
                                         chain_type="stuff",
                                         retriever=vectorstore.as_retriever())

        prompt = f"""Dựa trên nội dung văn bản được cung cấp, hãy tạo {num_questions} câu hỏi trắc nghiệm.
        Mỗi câu hỏi phải có 4 lựa chọn và chỉ có 1 đáp án đúng.
        Format cho mỗi câu hỏi như sau:

        Câu hỏi N: [câu hỏi]
        A. [lựa chọn]
        B. [lựa chọn]
        C. [lựa chọn]
        D. [lựa chọn]
        Đáp án đúng: [A/B/C/D]
        """

        quiz = qa.invoke(prompt)
        return quiz

    def process_and_generate(self, file_path, num_questions=10):
        try:
            text = self.extract_text_from_pdf(file_path)

            chunks = self.create_chunks(text)

            vectorstore = FAISS.from_texts(texts=chunks, embedding=self.embeddings)

            quiz = self.generate_quiz(vectorstore, num_questions)

            return quiz['result']

        except Exception as e:
            logging.error(f"Lỗi trong quá trình xử lý file và tạo quiz: {str(e)}")


def main():
    quiz_generator = QuizGenerator("GROQ_API_KEY")
    quiz = quiz_generator.process_and_generate("./data/04.pdf")
    print(quiz)


main()