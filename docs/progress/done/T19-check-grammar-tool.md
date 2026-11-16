# T19 · 🔧 Script kiểm tra grammar dùng chung

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **File đề xuất:** `tools/check_grammar.py`

Hai lỗi nặng nhất phase 1 (#3 crash, #2 lệch tokenizer) script này bắt được ngay. Mỗi người chạy
trước khi mở PR.

## Việc cần làm
- [x] Load grammar bằng code chuẩn của nhóm; báo non-terminal chưa định nghĩa / không dùng tới /
      định nghĩa 2 lần / terminal viết hoa; đếm đủ 26 nhánh.
- [x] Chạy câu mẫu, câu thách thức và hội thoại; in câu rớt theo nhánh.
- [x] Sinh câu → parse lại; đếm số cây parse (> 1 = mơ hồ).
- [x] Chạy cả pipeline trên câu sinh ra: intent ≠ UNKNOWN; entity có ID (trừ frame ngữ cảnh); query tìm thấy hoặc fallback có nguyên nhân rõ.

## Ghi chú
- Các bước đã dùng để gộp phase 1: `done/T03-grammar-phase1.md`, mục "Cách kiểm tra". Khi code
  của nhóm chưa xong thì chạy bằng code của nhánh `sample`.
- `tools/make_golden.py` đã có sẵn phần lấy code `sample` qua `git archive` và chạy trên
  `src/data/` — dùng lại cách đó. Sau khi đổi grammar, chạy lại nó rồi chạy test hợp đồng.

## Kết quả nghiệm thu 2026-11-16

Đã thêm tools/check_grammar.py: kiểm cấu trúc, token, suite, hội thoại, 26 nhánh sinh, ambiguity và pipeline. Ca thiếu KB/ngữ cảnh có chủ đích được báo riêng; --strict-kb yêu cầu toàn bộ query tìm thấy. Không coi các fallback đúng là lỗi grammar. Bằng chứng: docs/validation/grammar-check.json.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
