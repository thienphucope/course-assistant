# T22 · 🔥 Báo cáo

- **Trạng thái:** PDF LaTeX xong (18/11); đang dò lại
- **Phụ trách:** Phúc (dò lại bản PDF)
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

## Cập nhật 2026-11-18

Đã điền tên/MSSV 4 thành viên vào đầu báo cáo. Còn: phân công, nhóm duyệt và chọn định dạng nộp (PDF/DOCX).

Cùng ngày: chuyển báo cáo sang LaTeX theo mẫu `hcmut-report` (template IOT252 của nhóm, chỉnh bìa/footer
cho CO3085, GV Võ Thanh Hùng, lớp L01). Nguồn ở `report/` (`report.tex` + `chapters/*.tex`), build
bằng `pdflatex` 2 lần (MiKTeX portable, không cần shell-escape) → `report/report.pdf`, 27 trang.
Nội dung mở rộng từ `docs/report.md`: sơ đồ pipeline (TikZ), cây cú pháp (forest), bảng 26 nhánh →
intent, bảng truy vấn/fallback, trace thật, kết quả đánh giá, khai báo AI. Bảng phân công lấy theo
lịch sử commit/PR — **nhóm cần xác nhận**. Gói nộp dùng `report.pdf` thay `report.md`.

## Việc tiếp theo (chốt 18/11)

Phúc dò lại `report/report.pdf`. Những chỗ cần soát kỹ:
- [ ] Bảng 1.2 phân công: suy từ lịch sử commit/PR, cả nhóm xác nhận.
- [ ] Bảng 10.1 khai báo AI: phạm vi và mốc thời gian đúng thực tế.
- [ ] Đọc toàn bộ nội dung, số liệu (42/42, 20/22, 6/6, 49 test, 1.000 câu sinh), chính tả.
- [ ] Sửa xong: build lại (`pdflatex report.tex` ×2 trong `report/`) rồi đóng gói lại (T24).
