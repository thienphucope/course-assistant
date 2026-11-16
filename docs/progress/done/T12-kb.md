# T12 · 🔧 KB loader

- **Trạng thái:** xong (đã tích hợp ở `95df6db`)
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
- Pipeline nạp KB khi khởi tạo; **query** tra đối tượng KB đã nạp, bước intent không đọc KB.

## Kết quả triển khai

- Ngày hoàn thành: 01/11/2026.
- Commit triển khai: `95df6db` (T12/T13).
- Tham khảo code nhánh đóng băng `sample`; giữ hợp đồng và golden hiện hành.
- Đọc đủ sáu file KB; so khớp tuyệt đối bảy collection golden; validation và test dữ liệu hỏng đạt.
- Kiểm tra T12/T13: 14 test đạt, không skip. Toàn bộ suite: 28 test, 16 đạt, 12 skip ở các task khác, không lỗi.

## Thiết kế triển khai hiện tại

### Schema và thời điểm nạp
[`KnowledgeBase.load`](../../../src/hcmut/iaslab/nlp/app/kb.py) được gọi khi `CourseAssistant.from_paths` khởi tạo, đọc đủ sáu file một lần. Query giữ tham chiếu KB đã nạp, không mở lại file mỗi câu. Semantic không đọc KB. Ghi chú cũ về 'chỉ query mới mở KB lúc runtime' cần hiểu là ranh giới sử dụng fact, không phải call flow I/O.

Aggregate có bảy field: course, weeks, chapter_weeks, topics, assignment, resources, regulations. Field frozen của dataclass chặn gán lại thuộc tính nhưng dict/list bên trong vẫn mutable; query được kiểm bằng deepcopy để bảo đảm không thay KB.

### Cách parse từng định dạng
- schedule: state machine theo heading WEEK, scalar part/chapter/activity/milestone và list topics. Bỏ preamble; chuẩn hóa WEEK_NN/CHNN; bắt duplicate và bullet ngoài list. Tạo chapter_weeks theo thứ tự nguồn; tuần không ghi chapter không bị gán đoán.
- topics: state machine theo CHAPTER, gom summary nhiều dòng, giữ subtopics, tách keywords thành keyword_list; chapter_number là int và phải khớp ID.
- course: flat fields tương thích baseline, section mô tả/các phần, LO tổng quát và chi tiết, assessment, exam_format. Credits giữ str theo golden, không ép thành int.
- assignment: metadata và goal, bốn section PART_I–IV với scalar/list khác nhau; tách LLM/RAG EXTENSION khỏi phần chính.
- resources: block TEXTBOOK/REFERENCE, thêm kind/resource_id; loại study_note khỏi record cuối.
- regulations: gom từng key case-sensitive thành chuỗi nhiều dòng; AI_usage giữ đúng kiểu viết khóa của dữ liệu.

### Validation và lỗi
`load()` gọi validate và raise ValueError khi có lỗi, FileNotFoundError nếu thiếu file. Validate kiểm các trường bắt buộc, 15 tuần/12 chương/8 tài liệu của bộ dữ liệu hiện tại, ID và kiểu chapter_number, tham chiếu tuần–chương/index ngược, bốn phần BTL, resource ID trùng và tám quy định. Đây là schema đặc thù bộ đề, không phải validator tổng quát cho mọi môn.

Helper `_simple_fields` giữ một số field phẳng tương thích sample ngoài các section chuẩn hóa; không xóa chúng chỉ vì query ít dùng, vì golden so khớp tuyệt đối. `_parse_field_block` xử lý continuation/list, các loader kiểm các duplicate thuộc định dạng của mình; không diễn giải validate như một JSON schema có thể nhận mọi kiểu dữ liệu tùy ý.

### Đối chiếu và nghiệm thu
Implementation T12/T13 ở `95df6db`, đã tích hợp, không còn trạng thái chờ PR của đợt cũ. `tests.test_kb` kiểm số record, index, tuần 15 không chapter, LO nhiều dòng, duplicate tuần, tham chiếu hỏng và thiếu file. `test_contract_kb` so bảy collection golden, bao gồm tương thích field/kiểu. Không mở rộng KB trong đợt rà soát; các fact thiếu được query trả NOT_FOUND.
