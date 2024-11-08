# Document Helper
## 1. Giới thiệu về ứng dụng
- Document Helper là một ứng dụng Streamlit cho phép tạo câu hỏi trắc nghiệm tự động và tương tác với tài liệu thông qua chat bot, sử dụng Groq API và mô hình ngôn ngữ lớn.
- Tính năng chính:
  + Tạo bộ câu hỏi trắc nghiệm tự động từ tài liệu
  + Chat bot để hỏi đáp về nội dung tài liệu
  + Hỗ trợ nhiều định dạng tài liệu (PDF, PPTX, PPT, DOCX)
  + Lọc bỏ thông tin cá nhân (email, số điện thoại) từ tài liệu
  + Không lưu trữ tài liệu người dùng sau khi xử lý
  + Xử lý file tạm thời an toàn

## 2. Yêu cầu
- Cài đặt các thư viện cần thiết:
  ```
  pip install comtypes faiss-cpu groq pdfplumber python-docx python-pptx streamlit st_copy_to_clipboard
  pip install -U langchain_community
  ```
- Groq API Key
  
## 3. Sử dụng
- Clone repo này về:
  ```
  git clone https://github.com/shineamond/DocumentHelper.git
  ```
- Mở cmd trong thư mục vừa clone về và nhập lệnh
  ```
  streamlit run App.py
  ```
  ![image](https://github.com/user-attachments/assets/3b3ba435-be09-4bf6-95c5-a19d2a16065e)
- Nhập Groq API Key vào thanh bên trái của màn hình
  ![image](https://github.com/user-attachments/assets/820caaf0-eadc-4ee9-90c8-9ea5912cdeb6)
- Tải lên tài liệu với định dạng cho phép và nhấn "Xử lý tài liệu"
  ![image](https://github.com/user-attachments/assets/33ffc483-dab9-4ab0-be6d-d50e56286b0f)
- Sau khi xử lý xong, người dùng có thể tạo quiz từ tài liệu hoặc trò chuyện về tài liệu
  ![image](https://github.com/user-attachments/assets/3448f98f-eaa8-4904-848b-ac4bf56e6919)
  ![image](https://github.com/user-attachments/assets/053a5811-e08c-48de-9964-f6014b2d3de3)
  ![image](https://github.com/user-attachments/assets/df99a52d-6d13-4520-a3d6-4dc4f2cb85d9)

## 4. Về mã nguồn
- Trích xuất văn bản từ các loại file: pdfplumber cho file PDF, comtypes chuyển đổi file PPT sang PPTX, python-pptx cho file PPTX, python-docx cho file DOCX.
- Phân chia văn bản đã trích xuất thành các đoạn nhỏ hơn.
- Tạo vector cho các đoạn văn bản bằng mô hình "sentence-transformers/all-MiniLM-L6-v" của HuggingFaceEmbeddings.
- Sử dụng mô hình ngôn ngữ lớn "llama3-70b-8192" thông qua Groq để tạo quiz và trò chuyện về tài liệu.
- Sử dụng Streamlit để tạo giao diện cho ứng dụng.
