import os
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from TextExtractor import extract_text


class DocumentHelper:
    def __init__(self, groq_api_key):
        os.environ["GROQ_API_KEY"] = groq_api_key
        self.embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatGroq(temperature = 0.7, model_name = "llama3-70b-8192")
        self.vectorstore = None


    @staticmethod
    def create_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,
                                                       chunk_overlap = 200,
                                                       length_function = len)
        chunks = text_splitter.split_text(text)

        return chunks


    def process_document(self, file_path):
        try:
            text = extract_text(file_path)
            chunks = self.create_chunks(text)
            self.vectorstore = FAISS.from_texts(texts = chunks, embedding = self.embeddings)

        except Exception as e:
            raise Exception(f"Đã xảy ra lỗi trong quá trình xử lý file: {str(e)}")


    def generate_quiz(self, num_questions):
        if not self.vectorstore:
            raise Exception("Vui lòng tải tài liệu lên trước khi tạo quiz")

        qa = RetrievalQA.from_chain_type(llm = self.llm,
                                         chain_type = "stuff",
                                         retriever = self.vectorstore.as_retriever())

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
        return quiz['result']


    def chat_about_document(self, question, chat_history):
        if not self.vectorstore:
            raise Exception("Vui lòng tải tài liệu lên trước khi đặt câu hỏi")

        qa = ConversationalRetrievalChain.from_llm(
            llm = self.llm,
            retriever = self.vectorstore.as_retriever(),
            return_source_documents = True
        )

        result = qa({"question": question, "chat_history": chat_history})
        return result["answer"]


def show_quiz_tab():
    st.header("📝 Tạo quiz từ tài liệu")
    num_questions = st.slider("Số lượng câu hỏi:", min_value = 5, max_value = 30, value = 5)
    if st.button("📝 Tạo quiz"):
        with st.spinner("⏳ Đang tạo quiz..."):
            try:
                quiz = st.session_state['document_helper'].generate_quiz(num_questions)
                st.session_state['generated_quiz'] = quiz

            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình tạo quiz: {str(e)}")

    if st.session_state['generated_quiz']:
        st.text_area("Quiz đã tạo:", value = st.session_state['generated_quiz'], height = 500)
        st_copy_to_clipboard(st.session_state['generated_quiz'], "📋 Sao chép Quiz", "📋 Đã sao chép!")


def show_chat_tab():
    st.header("💬 Hỏi đáp về tài liệu")
    chat_container = st.container()
    with st.container():
        user_question = st.text_input("Nhập câu hỏi của bạn:")
        if st.button("📤 Gửi câu hỏi"):
            with st.spinner("⏳ Đang xử lý..."):
                try:
                    response = st.session_state['document_helper'].chat_about_document(
                        user_question,
                        st.session_state['chat_history']
                    )
                    st.session_state['chat_history'].append((user_question, response))
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {str(e)}")

    with chat_container:
        if st.session_state['chat_history']:
            for q, a in st.session_state['chat_history']:
                st.markdown(f"**🙋 Bạn:** {q}")
                st.markdown(f"**🤖 AI:** {a}")
                st.markdown("---")


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

    if 'document_helper' not in st.session_state:
        st.session_state['document_helper'] = DocumentHelper(groq_api_key)
    if 'document_processed' not in st.session_state:
        st.session_state['document_processed'] = False
    if 'generated_quiz' not in st.session_state:
        st.session_state['generated_quiz'] = ""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = "Quiz"

    uploaded_file = st.file_uploader("📁 Tải lên file tài liệu: ", type = ["pdf", "pptx", "ppt", "docx"])

    if uploaded_file:
        if st.button("📄 Xử lý tài liệu"):
            st.session_state['document_helper'].vectorstore = None
            st.session_state['document_processed'] = False
            st.session_state['generated_quiz'] = ""
            st.session_state['chat_history'] = []

            with st.spinner("⏳ Đang xử lý tài liệu..."):
                try:
                    st.session_state['document_helper'].process_document(uploaded_file)
                    st.session_state['document_processed'] = True
                except Exception as e:
                    st.error({str(e)})
                    
    if st.session_state['document_processed']:
        tab1, tab2 = st.tabs(["📝 Tạo quiz từ tài liệu", "💬 Hỏi đáp về tài liệu"])

        with tab1:
            show_quiz_tab()
        with tab2:
            show_chat_tab()


main()