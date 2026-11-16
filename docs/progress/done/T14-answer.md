# T14 · 🔧 Answer + not-found (Phần II)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/answer.py`
- **Output:** `src/output/answer.txt`
- **Nghiệm thu:** `tests.test_contract_answer` pass (hợp đồng: `docs/contracts.md` §6 — đúng loại
  câu trả lời + đủ dữ kiện bắt buộc; câu chữ tự do). Test dùng frame + result golden.

## Việc cần làm
- [x] Hàm cần viết: `AnswerGenerator.generate` (một template cho mỗi `kind`).
- [x] Đổ template tiếng Việt cho từng `kind` (bảng `data` ở §5).
- [x] Không có dữ kiện → báo lịch sự, **không bịa**; dùng đúng 1 trong 3 hằng fallback.
- [x] `found = True` thì không bao giờ trả câu fallback. Bug của sample (output Phần II/III/IV:
      `found = True` nhưng answer "không tìm thấy") được sửa ở tầng query (§5) — answer không cần
      tự đoán.

## Ghi chú
- KB không có thông tin giảng viên → `Ai dạy NLP?` phải ra not-found (đúng như sample).

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu golden answer, đủ fact bắt buộc và 3 loại fallback; các ca thiếu KB trả NOT_FOUND, không suy đoán dữ kiện.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Ranh giới và dispatch
[`AnswerGenerator.generate`](../../../src/hcmut/iaslab/nlp/app/answer.py) chỉ đọc SemanticFrame và QueryResult. Không mở KB, không đọc lại câu hỏi, không dùng LLM. Khi found=False, kind UNKNOWN → NOT_UNDERSTOOD, UNRESOLVED_CONTEXT → MISSING_CONTEXT, các kind còn lại → NOT_FOUND nguyên văn đề. Khi found=True, dispatch `_answer_<kind>`.

### Template theo loại dữ kiện
Thông tin môn render credits, ba phần của bộ đề, mô tả, thời lượng thi và thành phần điểm. Lịch render tuần/chương/chủ đề cùng activity/milestone nếu có. Topic render chương, kết quả tìm chủ đề hoặc câu kết luận quan hệ Có/Không. LO render mô tả hay chương liên quan. BTL render overview, requirements/minimum_requirements/optional_or_extension hoặc suggested_outputs. Deadline liệt kê milestone; resource liệt kê title; rule dùng văn bản quy định.

Ví dụ TOPIC_RELATION có related=False trả câu phủ định có căn cứ, không trả NOT_FOUND. Ngược lại, output Phần II không có trong KB thì query phải found=False trước khi đến template. Tên phần và thời lượng dùng helper nhỏ để bỏ prefix Part hoặc lấy số phút trong format của bộ dữ liệu.

### Bất biến và lỗi tích hợp
Ba fallback là hằng riêng, không dùng lẫn không hiểu câu với thiếu dữ kiện. Query found=True phải có kind/data mà template hỗ trợ; fallback cho kind lạ là dấu hiệu lỗi tích hợp, được T19 bắt bằng kiểm found/fallback. Không xem mọi QueryResult tự dựng ngoài schema là đầu vào hợp lệ.

Template dùng dữ kiện query nhưng vẫn phụ thuộc truy vấn đúng đối tượng và field; dùng template không chứng minh hệ thống không thể trả sai. Sửa guard T13 giúp tránh câu trả lời có vẻ có căn cứ nhưng đang nói về BTL/chương khác. Không tự thêm dữ kiện thiếu để tránh fallback.

### Nghiệm thu và giới hạn
`test_contract_answer` có 205 result/frame, so category và các fact must_contain, không so toàn bộ reference_answer. `test_missing_facts_use_fallback` kiểm giảng viên/ngày thi/output thiếu qua pipeline. T17 nay kiểm đúng category fallback trước khi kiểm fact, để câu có cùng cụm từ nhưng chèn thông tin tự tạo không được tính đúng.

Câu chữ theo bộ KB hiện tại: ba phần chính, ID/tên môn và quy ước phút từ format tiếng Anh. Khi thay schema hay số phần của môn, cần sửa query/template/test đồng thời; không mặc định template là renderer cho một môn bất kỳ.
