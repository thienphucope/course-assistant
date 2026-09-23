# Evaluation — ghi chú cũ

Kế hoạch ban đầu ở tài liệu này đã được triển khai và cập nhật trong
`docs/06-evaluation.md`. Bộ câu mẫu có bốn cột `ID | QUERY | EXPECTED_INTENT |
EXPECTED_ENTITY`; bản `gold_queries.txt` thêm hai cột kiểm tra query/đáp án.
Chạy `python run.py evaluate` từ `src/` để tái tạo `output/evaluation.txt`.
