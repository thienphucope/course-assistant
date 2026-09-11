# Dữ liệu của project mẫu

- `kb/` là knowledge base được truy vấn khi chạy. Nội dung sao chép từ bộ dữ liệu
  mẫu đi kèm đề CO3085.
- `scaffolding/entities.txt` là lexicon thiết kế grammar và chuẩn hóa entity.
- `scaffolding/sample_queries.txt` và `dialogues.txt` là test set do đề cung cấp;
  project bổ sung các câu nguyên văn trong PDF cùng expected query-status và các
  cụm fact bắt buộc để đánh giá end-to-end.
- `scaffolding/faq.txt` được giữ để bảo toàn bộ dữ liệu gốc nhưng không được dùng
  như bảng đáp án tắt.
- `scaffolding/challenge_queries.txt` do project này tự bổ sung để đánh giá các
  cách diễn đạt ngoài grammar, trạng thái not-found và error analysis; nguồn được
  ghi ngay trong file.
