# T01 · ✅ Dữ liệu thầy cho sẵn

- **Trạng thái:** xong (có sẵn từ đề, không phải làm)
- **Nguồn:** bộ dữ liệu mẫu đi kèm đề CO3085, nay nằm ở `src/data/`

## Gồm

- [x] **List intent** — `src/data/scaffolding/entities.txt` (GET_SCHEDULE, GET_TOPIC, GET_DEADLINE, …)
- [x] **Entity vocab + đồng nghĩa** — `entities.txt` (NLP = CO3085 = Natural Language Processing; CFG, PCFG, …)
- [x] **Nội dung KB** — `src/data/kb/*.txt` (course_info, schedule, topics, assignments, resources, regulations)
- [x] **Test có đáp án** — `src/data/scaffolding/sample_queries.txt` (EXPECTED_INTENT | EXPECTED_ENTITY | query status | answer facts)

## Ghi chú

`entities.txt` cung cấp từ vựng và tên intent để thiết kế; runtime vẫn phải dùng
parser và semantic để xác định intent/entity của từng câu hỏi.

## Thiết kế triển khai hiện tại

### Phạm vi và nguồn dữ liệu
Ticket này xác định dữ liệu đầu vào của hệ thống, không nhận công việc cài thuật toán. Bản gốc nằm trong `docs/materials/NLP_Course_Assistant_Sample_Data.zip`; bản ứng dụng dùng nằm ở [`src/data/`](../../../src/data). Sáu file KB gồm thông tin môn, lịch học, nội dung chương, bài tập, tài liệu và quy định. Dữ kiện KB giữ nguyên nội dung bản gốc; khác biệt dòng trống cuối file không thay đổi fact.

### Vai trò từng loại dữ liệu
- `kb/`: nguồn fact cho câu trả lời; T12 nạp vào `KnowledgeBase`, T13 truy vấn đối tượng đã nạp.
- `scaffolding/entities.txt`: gợi ý từ vựng/alias và intent để thiết kế; không phải một bộ câu hỏi đã gán nhãn. T11 kết hợp các section trong file với bảng ID trong code.
- `sample_queries.txt`: Q001–Q034 là câu gốc; nhóm thêm S001–S008 từ ví dụ của đề và cột query-status/required-answer-terms. Bộ ứng dụng hiện có 42 câu.
- `dialogues.txt`: 5 hội thoại gốc và D06 bổ sung trong bản tham khảo, tổng 6 phiên.
- `faq.txt`: tài liệu hướng dẫn, không dùng tra đáp án thay cho pipeline.
- `challenge_queries.txt` và `grammar.cfg`: phần bổ sung cho ứng dụng, không gán nguồn là dữ kiện KB do thầy cấp.

### Đối chiếu và giới hạn
Đường dẫn mặc định do [`ProjectPaths`](../../../src/hcmut/iaslab/nlp/app/paths.py) tìm từ vị trí module, trỏ tới `src/data/`. Thư mục `data/` ngoài repo đã bỏ ở `9096375`; gói nộp tạo `project/data/` từ `src/data/`. Không lấy file test làm kho đáp án. Thiếu thông tin giảng viên/ngày thi/số buổi học vẫn là thiếu KB, không tự bổ sung fact để nâng điểm.

**Kiểm chứng:** T12 so bảy collection với `kb.json`; T17 chấm riêng bộ 42 câu, 22 challenge và 6 hội thoại. Việc kiểm toàn văn dữ kiện gốc dùng archive trong `docs/materials/`, không cần khôi phục thư mục `data/` ngoài.
