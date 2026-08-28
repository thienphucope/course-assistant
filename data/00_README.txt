NLP COURSE ASSISTANT - SAMPLE DATASET
=====================================

Mục đích
--------
Bộ dữ liệu này được thiết kế làm dữ liệu mẫu cho bài tập lớn:
"Trợ lý hỗ trợ học tập thông minh – Course Assistant" của môn Xử lý
ngôn ngữ tự nhiên (NLP).

Bộ dữ liệu được thiết kế để sinh viên có thể xây dựng:
- Grammar / Parser
- Semantic representation
- Intent / Entity recognition
- Knowledge-base Question Answering
- Local discourse context / reference
- Retrieval hoặc RAG ở mức mở rộng

Nguồn và phạm vi
----------------
1. Nội dung kiến thức môn học được xây dựng dựa trên đề cương CO3085
   Natural Language Processing, HK261, phiên bản DCMH.CO3085.6.1.
2. Một số thông tin phục vụ bài tập lớn như lịch 15 tuần, các mốc BTL,
   câu hỏi mẫu và quy định giả lập là DỮ LIỆU MẪU, không phải thông tin
   hành chính chính thức của học phần.
3. Sinh viên không cần xây dựng grammar/parser từ dữ liệu này. Các file
   kiến thức là nguồn dữ liệu để hệ thống Course Assistant truy vấn.

Cấu trúc
--------
course_info.txt       : thông tin chung về môn học
schedule.txt           : kế hoạch học tập mẫu 15 tuần
topics.txt             : kiến thức/chủ đề của 12 chương
assignments.txt        : bài tập lớn và các mốc mẫu
resources.txt          : giáo trình và tài liệu tham khảo
regulations.txt        : quy định học tập mẫu
faq.txt                : các câu hỏi - trả lời thường gặp
dialogues.txt          : hội thoại mẫu có tham chiếu/ngữ cảnh
sample_queries.txt     : bộ truy vấn kiểm thử có nhãn kỳ vọng
entities.txt           : từ điển thực thể và từ đồng nghĩa mẫu

Gợi ý sử dụng
-------------
- Classical NLP:
  dùng các file trên làm Knowledge Base; xây dựng intent, entity,
  semantic representation và cơ chế truy vấn.
- LLM/RAG:
  chia các file thành document/chunk; thực hiện retrieval rồi cung cấp
  context cho LLM.
- Dialogue:
  dùng dialogues.txt để kiểm tra local discourse context, pronoun,
  definite description và ellipsis đơn giản.

Lưu ý
-----
Các câu hỏi trong sample_queries.txt có trường EXPECTED_INTENT và
EXPECTED_ENTITY để hỗ trợ xây dựng/evaluate hệ thống. Không bắt buộc
phải dùng đúng tên intent/entity này nếu nhóm tự thiết kế schema khác.
