# T15 · ✨ Phần III — Dialogue (optional)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/dialogue.py`
- **Output:** `src/output/dialogue.txt`
- **Nghiệm thu:** `tests.test_contract_dialogue` pass (hợp đồng: `docs/contracts.md` §7 — bảng
  `action` → frame sau khi giải)

## Việc cần làm
- [x] Hàm cần viết: `DialogueContext.resolve`, `DialogueContext.update`.
- [x] Test mẫu `src/tests/test_pipeline.py`: thay `skipTest` TODO về ngữ cảnh hội thoại.
- [x] Giữ ngữ cảnh cục bộ theo loại: chương / phần BTL / LO vừa nhắc.
- [x] Giải tham chiếu: `nó`, `chương này/đó`, `phần này/đó`, `nội dung này`.
- [x] Chạy 6 hội thoại trong `src/data/scaffolding/dialogues.txt`.

## Ghi chú
- Grammar phase 1 chỉ nhận đại từ hợp với loại thực thể resolver cần (đã bỏ `cái này`, `bài
  này`, `còn tuần sau`…). Muốn nhận thêm thì resolver phải hỗ trợ trước.

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu golden dialogue và 6/6 hội thoại; kiểm thử nhớ chương độc lập với phần BTL, không cập nhật khi query thất bại và reset phiên.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
