# T04 · 🔧 Kết thúc PR #1, #2, #3 của phase 1

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Ngày xong / Commit:** 22/10/2026 · `f8ff31e` (merge tay)

## Đã làm

- [x] Nội dung grammar của 3 PR được **merge tay** có chọn lọc vào `main` ở `f8ff31e` (ghi
      `Co-authored-by` cho Bảo, Bách, Khoa) — chi tiết nhận / bỏ: `T03-grammar-phase1.md`.
- [x] Pipeline của PR #2 không merge — `T05-codebase-decision.md`.

## Ghi chú

- Ghi nhận lịch sử ngày 22/10/2026: 3 PR còn Open tại thời điểm review. Đây không phải
  trạng thái GitHub hiện tại. Nội dung đã tích hợp chọn lọc ở T03; không merge lại nguyên
  pipeline PR #2 vì sẽ đưa vào các thay đổi ngoài phạm vi.

## Thiết kế triển khai hiện tại

### Thiết kế tích hợp
T04 kết thúc việc tiếp nhận nội dung phase 1 bằng commit `f8ff31e`: chọn alternative grammar, sửa constituent chung và giữ hợp đồng 26 nhánh. T03 lưu lý do nhận/bỏ theo từng người. T05 xác định skeleton làm nền cho các tầng sau.

### Vì sao không merge nguyên nhánh PR
Ba PR sửa cùng `grammar.cfg`; merge cả nhánh mang theo thay đổi ngoài ranh giới và có thể ghi đè tokenizer, dữ liệu, output hoặc API của skeleton. Đích tích hợp là **nội dung grammar được chấp nhận**, không phải toàn bộ cây file của từng PR. Lịch sử tác giả và quyết định tích hợp cần giữ để truy nguồn, không tái áp patch cũ lên trạng thái hiện tại.

### Đối chiếu Git
`git show f8ff31e -- src/data/grammar.cfg` kiểm được kết quả tích hợp grammar; `git log -- src/data/grammar.cfg` cho các bước mở rộng sau đó. `b104437` là mốc tích hợp T08–T17, `ebe53eb` hoàn thiện phần còn thiếu và `9096375` dọn layout. Những mốc này là commit local đã đối chiếu; không dùng ghi chú Open ngày 22/10 để kết luận trạng thái PR hiện tại trên GitHub.

### Nghiệm thu
Kiểm lại grammar bằng T19 và golden parser/semantic của T06. T04 không có thuật toán runtime hay bài test riêng: bằng chứng chính là lịch sử Git, nội dung grammar đã gộp và kiểm thử hồi quy. Đợt rà soát này không mở/đóng PR hoặc push remote.
