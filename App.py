import logging
import os
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from TextExtractor import extract_text


class QuizGenerator:
    def __init__(self, groq_api_key):
        os.environ["GROQ_API_KEY"] = groq_api_key
        self.embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatGroq(temperature = 0.7, model_name = "llama3-70b-8192")


    @staticmethod
    def create_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,
                                                       chunk_overlap = 200,
                                                       length_function = len)
        chunks = text_splitter.split_text(text)

        return chunks


    def generate_quiz(self, vectorstore, num_questions):
        qa = RetrievalQA.from_chain_type(llm = self.llm,
                                         chain_type = "stuff",
                                         retriever = vectorstore.as_retriever())

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


    def process_and_generate(self, file_path, num_questions = 10):
        try:
            text = extract_text(file_path)

            chunks = self.create_chunks(text)

            vectorstore = FAISS.from_texts(texts = chunks, embedding = self.embeddings)

            quiz = self.generate_quiz(vectorstore, num_questions)

            return quiz['result']

        except Exception as e:
            logging.error(f"Lỗi trong quá trình xử lý file và tạo quiz: {str(e)}")


def main():
    st.set_page_config(page_title = "Quiz Generator", layout = "wide")
    st.title("Quiz Generator")

    with st.sidebar:
        st.header("⚙️ Cấu hình")
        groq_api_key = st.text_input("Nhập Groq API Key: ", type = "password")

        st.markdown("---")

    if not groq_api_key:
        st.warning("⚠️ Vui lòng nhập Groq API key để bắt đầu.")
        return

    uploaded_file = st.file_uploader("📁 Upload PDF file: ", type = ["pdf", "pptx", "ppt", "docx"])

    if uploaded_file:
        num_questions = st.slider("Số lượng câu hỏi: ", min_value = 5, max_value = 30, value = 5)

        if st.button("📃 Tạo Quiz"):
            with st.spinner("⏳ Đang xử lý. Vui lòng chờ..."):
                try:
                    quiz_generator = QuizGenerator(groq_api_key)
                    quiz = quiz_generator.process_and_generate(uploaded_file, num_questions)
                    st.session_state['generated_quiz'] = quiz

                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {str(e)}")

    if 'generated_quiz' in st.session_state:
        st.subheader("Quiz được tạo: ")
        st.text_area("", value = st.session_state['generated_quiz'], height = 400)

        st_copy_to_clipboard(st.session_state['generated_quiz'], "📋 Sao chép Quiz", "📋 Đã sao chép!")


main()