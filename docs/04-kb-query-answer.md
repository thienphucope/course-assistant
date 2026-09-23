# Mốc 4 — Tra kho tri thức và tạo câu trả lời

Mốc 3 tạo `SemanticFrame(intent, entity, slots)`. Mốc 4 dùng frame đó để **tra fact trong sáu file `src/data/kb/`** và tạo câu trả lời. Query không phân tích lại câu gốc; answer không tự tìm dữ liệu. Nhờ vậy có thể truy vết từng kết luận về đúng bản ghi nguồn.

## Cách chạy và đọc trace

Từ thư mục `src/`:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py --root . ask --trace 'Chương 4 học vào tuần nào?'
```

Các dòng chính:

```text
Semantic: GET_SCHEDULE(chapter=CH04)
Query: KB.chapter_weeks[CH04]
KB result: FOUND
Source: schedule.txt:WEEK 04, schedule.txt:WEEK 05
Answer: Chương 4 học vào tuần 4, tuần 5.
```

`Semantic` là yêu cầu chuẩn hóa; `Query` là đường tra trên dữ liệu đã đọc; `Source` là những bản ghi đã hỗ trợ đáp án. Nếu không có fact, `KB result` không phải `FOUND` và `answer.py` dùng thông báo thiếu dữ liệu.

## Ba lớp mã nguồn

1. `kb.py:KnowledgeBase.load` đọc `course_info.txt`, `schedule.txt`, `topics.txt`, `assignments.txt`, `resources.txt`, `regulations.txt`. Nó chuyển heading và khóa text thành dict/list theo ID chuẩn, kiểm tra bản ghi trùng, trường bắt buộc và tham chiếu tuần → chương. Chương 4 trong lịch có hai bản ghi tuần; `chapter_weeks[CH04]` vì thế chứa cả `WEEK_04` và `WEEK_05`.
2. `query.py:QueryEngine.execute` chọn handler theo intent rồi dùng các slot như `week`, `chapter`, `topic`, `field`. Nó trả `QueryResult(query, found, kind, data, sources, reason)`. Với một chủ đề xuất hiện ở nhiều nơi, handler giữ **toàn bộ** bản ghi khớp. Alias trong `entities.txt` hỗ trợ tìm tên chủ đề trong văn bản KB; các từ viết tắt như `CFG` được so khớp nguyên từ để tránh nhận nhầm trong `PCFG`.
3. `answer.py:AnswerGenerator.generate` biến `QueryResult.data` thành câu tiếng Việt. Mỗi loại kết quả có mẫu câu riêng. Nó không lấy thêm fact từ bên ngoài `QueryResult`.

## Ba trường hợp dễ nhầm

- **Nhiều kết quả đúng:** `PCFG` nằm ở `CH03` và `CH06`; lịch mẫu nhắc ở tuần 3 và tuần 7. Câu trả lời giữ cả bốn nguồn. Tài liệu về statistical NLP khớp hai record tài liệu, nên trả cả hai.
- **Hiểu câu nhưng thiếu fact:** “Deadline của bài tập lớn là khi nào?” → `GET_DEADLINE(BTL01)` → `KB.assignment[BTL01].deadline`. File `assignments.txt` không có ngày nộp; checkpoint và “final submission” trong lịch tuần không được tự đổi thành một ngày cụ thể. Câu “Midterm thi khi nào?” cũng không được suy từ `60 minutes`, vì đó là **thời lượng**, không phải lịch thi. Tên giảng viên cũng chưa có trong KB.
- **Ngoài miền:** câu hỏi thời tiết cho cây `()`, intent `UNKNOWN` và query `OUT_OF_SCOPE`, không gọi handler môn học.

## Mức hoàn thành

25/25 câu đơn lõi Q001–Q025 có query `FOUND`, nguồn KB và đáp án chứa nội dung cần thiết. Bảy nhóm bắt buộc đều có ít nhất một ca end-to-end. Bộ test còn kiểm tra các nguồn nhiều bản ghi, câu thiếu fact và dữ liệu sai định dạng. Các nhánh hội thoại `Q_CONTEXT_*` vẫn thuộc phần mở rộng tùy chọn.

Lệnh `ask` dùng để kiểm tra từng câu. Từ Mốc 5, lệnh `batch` đọc toàn bộ `input/sentences.txt` và ghi `output/query.txt`, `output/answer.txt` theo đúng thứ tự câu hỏi; xem `docs/05-batch-and-docker.md`.
