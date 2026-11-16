# T07 · 🔧 Các quyết định đang treo

- **Trạng thái:** xong
- **Phụ trách:** Phúc (+ cả nhóm)

Chốt trước khi giao việc code; ghi kết quả vào đây rồi chuyển file sang `done/`.

## Việc cần làm
- [x] **Thành viên có được đọc code nhánh `sample` không?** **Có — khuyến khích đọc** để tham khảo
      cách làm từng tầng. Điều kiện: tự hiểu và giải thích lại được code mình nộp (đề mục 8, có thể
      bị gọi thuyết trình); code phải pass test hợp đồng; ghi nguồn tham khảo trong báo cáo (T22).
- [x] **Độ chặt của golden KB** (`docs/contracts.md` §4): đang khớp tuyệt đối `kb.json` (kể cả kiểu,
      ví dụ `chapter_number` là int). Giữ nguyên, hay nới thành "đúng khoá + kiểu"?
- [x] **Hướng Phần II**: Lựa chọn 1 — Classical (luật/keyword). **Không làm** Lựa chọn 2
      (LLM/RAG): đề cho chọn 1 trong 2, và LLM/RAG không thay được phần NLP cốt lõi (đề 7.3, 9).
- [x] **Codebase chuẩn**: skeleton trên `main` (theo `sample`), không dùng code PR #2 làm nền —
      `done/T05-codebase-decision.md`.
- [x] **Định dạng 9 file output**: theo sample — ghi tại `docs/contracts.md` §9.
- [x] **Phân công đợt code**: ai nhận task nào trong `undone/`.

## Kết quả nghiệm thu 2026-11-16

Người dùng giao Codex hỗ trợ triển khai các task còn thiếu; giữ golden KB so khớp tuyệt đối theo xác nhận ngày 2026-11-16. Phân vai thuyết trình và thông tin thành viên bổ sung tại T20/T23.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
