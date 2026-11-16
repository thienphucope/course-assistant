# T07 · 🔧 Các quyết định của nhóm

- **Trạng thái:** xong
- **Phụ trách:** Phúc (+ cả nhóm)

Chốt trước khi giao việc code; ghi kết quả vào đây rồi chuyển file sang `done/`.

## Việc cần làm
- [x] **Thành viên có được đọc code nhánh `sample` không?** **Có — khuyến khích đọc** để tham khảo
      cách làm từng tầng. Điều kiện: tự hiểu và giải thích lại được code mình nộp (đề mục 8, có thể
      bị gọi thuyết trình); code phải pass test hợp đồng; ghi nguồn tham khảo trong báo cáo (T22).
- [x] **Độ chặt của golden KB** (`docs/contracts.md` §4): đang khớp tuyệt đối `kb.json` (kể cả kiểu,
      ví dụ `chapter_number` là int). **Đã chốt: giữ so khớp tuyệt đối**, không nới thành chỉ kiểm khoá + kiểu.
- [x] **Hướng Phần II**: Lựa chọn 1 — Classical (luật/keyword). **Không làm** Lựa chọn 2
      (LLM/RAG): đề cho chọn 1 trong 2, và LLM/RAG không thay được phần NLP cốt lõi (đề 7.3, 9).
- [x] **Codebase chuẩn**: skeleton trên `main` (theo `sample`), không dùng code PR #2 làm nền —
      `done/T05-codebase-decision.md`.
- [x] **Định dạng 9 file output**: theo sample — ghi tại `docs/contracts.md` §9.
- [x] **Phân công đợt code**: ai nhận task nào trong `undone/`.

## Kết quả nghiệm thu 2026-11-16

Người dùng giao Codex hỗ trợ triển khai các task còn thiếu; giữ golden KB so khớp tuyệt đối theo xác nhận ngày 2026-11-16. Phân vai thuyết trình và thông tin thành viên bổ sung tại T20/T23.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Các quyết định đã chốt và hệ quả
| Quyết định | Cách code/tài liệu thể hiện | Lý do |
| --- | --- | --- |
| Classical NLP | CFG/Earley → semantic → KB/query → template answer | Giữ đầy đủ các bước Phần I/II, chạy offline. |
| Skeleton chung | Module và kiểu dữ liệu thống nhất, xem T05 | Thành viên triển khai từng tầng mà không đổi API tầng khác. |
| Được đọc `sample` | Tool golden lấy baseline, báo cáo ghi nguồn | Tham khảo kèm kiểm thử và tự giải thích thuật toán. |
| Golden KB so khớp tuyệt đối | `test_contract_kb` so bảy collection và kiểu | Phát hiện mất/sửa fact, không chỉ kiểm schema. |
| Chín output theo hợp đồng | `output.py`, CLI và renderer evaluation/dialogue | Đọc được quá trình xử lý, giữ thứ tự input và UTF-8/LF. |
| Codex hỗ trợ hoàn thiện và rà soát | Code, regression test, ticket thiết kế | Nhóm còn review, điền thành viên, phân vai thuyết trình. |

### Phạm vi nghiệm thu
T07 ghi lựa chọn của nhóm, không có implementation runtime riêng. Đối chiếu qua `requirements.txt`, `pipeline.py`, hợp đồng và báo cáo. Không thêm LLM/RAG, không đổi mức so khớp KB trong đợt rà soát này.

T20–T24 vẫn còn thông tin nhóm/định dạng bản nộp và kiểm chứng Docker. Người dùng đã yêu cầu để Docker lại; không đánh dấu T21 xong chỉ vì source hoặc gói giải nén chạy được. Nội dung thiết kế của T01–T19 và test code thuộc đợt rà soát từ `9096375`; không thay thế bước nhóm duyệt bài.
