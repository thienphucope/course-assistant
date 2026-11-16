# T22 · 🔥 Báo cáo

- **Trạng thái:** nội dung xong; chờ nhóm duyệt/định dạng
- **Phụ trách:** chưa giao
- **Yêu cầu:** đề mục 6 (Phần IV) và 7.6

Cần trước: `T17-evaluation.md` (số liệu), phần lớn pipeline chạy được.

## Việc cần làm
- [x] Kiến trúc pipeline: Input → Grammar/Parser → cây → Semantic → Intent/Entity → KB → Answer.
- [x] Grammar: 26 nhánh, cách mở rộng ở phase 1 (`done/T03-grammar-phase1.md`).
- [x] Đánh giá (tối thiểu theo đề): số câu kiểm thử, số câu đúng, độ chính xác, một số ca trả lời
      sai, **phân tích nguyên nhân lỗi**, ưu/nhược của phương pháp.
- [x] Hạn chế và hướng mở rộng.
- [x] **Ghi nguồn** (đề 7.2, 8): dữ liệu thầy cấp; câu bổ sung (`challenge_queries.txt`, câu phase 1
      trong `input/sentences.txt`) do nhóm tự viết; grammar phase 1 xây trên bản tham khảo ở nhánh
      `sample`.
- [x] **Khai báo sử dụng AI** (quy định `AI_usage` trong `kb/regulations.txt`): dùng ở đâu, làm gì,
      nhóm đã kiểm tra lại thế nào.

## Cập nhật 2026-11-16

Nội dung đầy đủ tại docs/report.md: phương pháp, 42/42 + 20/22 + 6/6, ca sai C007/C008, hạn chế, nguồn và AI. Chờ nhóm điền thành viên, review và chốt định dạng nộp theo yêu cầu người dùng.
