# T12 · 🔧 KB loader

- **Trạng thái:** xong (chờ review PR)
- **Phụ trách:** Nguyễn Huy Bách
- **Code:** `src/hcmut/iaslab/nlp/app/kb.py` (`KnowledgeBase.load`, `validate`)
- **Test:** `src/tests/test_kb.py`
- **Nghiệm thu:** `tests.test_contract_kb` pass — `KnowledgeBase` khớp tuyệt đối
  `src/tests/golden/kb.json`, `validate()` trả `[]` (hợp đồng: `docs/contracts.md` §4)

Nền của phần query — nên làm sớm, song song với Phần I.

## Việc cần làm
- [x] Hàm cần viết: `KnowledgeBase.load`, `KnowledgeBase.validate`.
- [x] Test mẫu `src/tests/test_kb.py`: thay 2 `skipTest` TODO (đếm bản ghi; KB hỏng phải báo lỗi).
- [x] Đọc 6 file `src/data/kb/*.txt` (mỗi file một format riêng) thành cấu trúc tra được (dict/index).
- [x] Index theo ID chuẩn: `WEEK_NN`, `CHNN`, `LOx.y`, `PART_I..IV`, ID resource/rule.
- [x] `validate()`: kiểm schema và tham chiếu chéo (chương trong lịch phải có trong topics, …).

## Ghi chú
- Tham khảo cách làm: `docs/knowledge/kb-loader.md`.
- Run time chỉ bước **query** mới mở KB; bước intent không đọc KB.

## Kết quả triển khai

- Ngày hoàn thành: 01/11/2026.
- Commit: xem lịch sử commit của PR T12–T13 (chưa commit tại thời điểm cập nhật).
- Tham khảo code nhánh đóng băng `upstream/sample`; giữ hợp đồng và golden hiện hành.
- Đọc đủ sáu file KB; so khớp tuyệt đối bảy collection golden; validation và test dữ liệu hỏng đạt.
- Kiểm tra T12/T13: 14 test đạt, không skip. Toàn bộ suite: 28 test, 16 đạt, 12 skip ở các task khác, không lỗi.
