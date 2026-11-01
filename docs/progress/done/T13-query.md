# T13 · 🔧 Query builder (Phần II)

- **Trạng thái:** xong (chờ review PR)
- **Phụ trách:** Nguyễn Huy Bách
- **Code:** `src/hcmut/iaslab/nlp/app/query.py` (`QueryEngine.execute`)
- **Output:** `src/output/query.txt`

- **Nghiệm thu:** `tests.test_contract_query` pass (hợp đồng: `docs/contracts.md` §5 — bảng
  `kind` / `data` / `sources`). Test dùng frame + KB golden nên **không phải chờ** semantic hay KB
  loader; chạy end-to-end mới cần hai task đó.

## Việc cần làm
- [x] Hàm cần viết: `QueryEngine.execute` (một nhánh cho mỗi intent).
- [x] Predicate → truy vấn KB theo intent, **không đọc lại câu hỏi gốc**.
- [x] Trả `QueryResult` có `found`, dữ kiện và nguồn (`kb/<file>.txt`).
- [x] `found = False` khi dữ kiện rỗng — ví dụ output của Phần II/III/IV không có trong KB (bug
      của sample, golden đã sửa; xem §5).

## Ghi chú
- Lý thuyết: `docs/knowledge/06-query-kb-answer.md`.

## Kết quả triển khai

- Ngày hoàn thành: 01/11/2026.
- Commit: xem lịch sử commit của PR T12–T13 (chưa commit tại thời điểm cập nhật).
- Tham khảo code nhánh đóng băng `upstream/sample`; giữ hợp đồng và golden hiện hành.
- 192/192 frame khớp golden, kể cả khi dùng KB đọc từ file thật; query không thay đổi KB.
- Sửa trường hợp section tồn tại nhưng không có output: `found=False`, giữ nguồn assignments theo golden.
- Kiểm tra T12/T13: 14 test đạt, không skip. Toàn bộ suite: 28 test, 16 đạt, 12 skip ở các task khác, không lỗi.
