# T18 · 🔥 Grammar mở rộng sau phase 1

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/data/grammar.cfg`
- **Nghiệm thu:** 26 nhánh, 42/42 câu mẫu, 0 câu mơ hồ; chạy lại `python tools/make_golden.py`

Phase 1 đã xong (`done/T03-grammar-phase1.md`). Bản sao `output/grammar.txt` do T16 ghi. Còn lại:

## Việc cần làm
- [x] Khi `T11-semantic.md` xong phần FEAT_*: thêm cách gọi tính năng BTL của Khoa
      (`grammar`, `parse tree`, `intent`, `entity`, `kb`, `hội thoại`, `test set`, `metric`, …)
      vào `ASSIGNMENT_FEATURE`, gom theo `FEAT_PARSING` / `FEAT_SEMANTIC` / `FEAT_CONTEXT` / `FEAT_EVAL`.
- [x] Khi lexicon có alias mới: thêm `dịch máy` vào `RESOURCE_TOPIC`, `thư viện có sẵn` vào `RULE_TOPIC`.
- [ ] (tuỳ chọn) C007 `Môn NLP học mấy buổi mỗi tuần?`, C008 `Tuần thứ ba tụi mình học bài gì vậy?`
      — sample cố ý để ngoài grammar; chỉ thêm nếu KB trả lời được.

## Ghi chú
- Mọi thay đổi phải giữ: 26 nhánh, 42/42 câu mẫu, 0 câu mơ hồ (xem quy ước ở `docs/progress/README.md`).

## Kết quả nghiệm thu 2026-11-16

Giữ 26 nhánh; bổ sung FEAT và 2 alias. Bộ đề 42/42, hội thoại 6/6; 1.000 câu sinh round-trip. Không phát hiện mơ hồ trong 1.047 câu khác nhau đã kiểm. C007/C008 là phần tùy chọn chưa triển khai, ghi phân tích trong báo cáo.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
