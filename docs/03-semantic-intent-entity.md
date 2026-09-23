# Mốc 3 — Từ cây cú pháp đến intent và entity

Mốc 2 trả lời câu hỏi **“câu có khớp một khuôn trong grammar không?”**. Mốc 3 trả lời **“nếu có, người hỏi đang yêu cầu loại thông tin gì và đang nói đến thực thể nào?”**. Mốc này không tra dữ kiện môn học; tra KB và tạo đáp án cho mọi nhóm là Mốc 4.

## Chạy và đọc đầu ra

Từ thư mục `src/`:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py --root . semantic
```

Lệnh đọc `data/grammar.cfg`, `data/scaffolding/entities.txt` và `input/sentences.txt`, rồi ghi hai file UTF-8:

| File | Mỗi dòng |
| --- | --- |
| `output/semantic.txt` | Một predicate như `GET_SCHEDULE(week=WEEK_03)` hoặc `UNKNOWN()`. |
| `output/intent-entity.txt` | Một JSON object gồm `intent`, `entity`, `slots`, `source_branch`. |

Dòng thứ *n* trong hai file này tương ứng dòng câu hỏi thứ *n* trong `input/sentences.txt`, sau khi bỏ dòng trống và dòng chú thích. Có thể dùng `semantic --input đường-dẫn-file.txt` để xử lý danh sách khác.

## Ví dụ đọc mã nguồn

Với câu **“Chương 4 học vào tuần nào?”**:

1. `tokenizer.py` tạo các token `chương`, `4`, `học`, `vào`, `tuần`, `nào`, `?`.
2. `parser.py` áp dụng `grammar.cfg`, tạo cây có nhánh `Q_SCHEDULE_CHAPTER` và nút con `CHAPTER_ENTITY` chứa `chương 4`.
3. `semantic.py` xem bảng `_SIMPLE_BRANCHES`: nhánh này nghĩa là intent `GET_SCHEDULE`, cần lấy `CHAPTER_ENTITY` từ họ `CHAPTER`, đưa vào slot `chapter`.
4. `entities.py` đối chiếu alias `Chương 4 = CH04`, nên kết quả là `GET_SCHEDULE(chapter=CH04)` và entity chính `CH04`.

Như vậy parser xác định **vị trí/cấu trúc** của cụm `chương 4`, còn lexicon xác định **ID chuẩn** của cụm ấy. `semantic.py` không tìm tên chương bằng cách dò toàn bộ chuỗi câu hỏi và không đọc KB.

Các nhánh có nhiều thực thể dùng hàm riêng trong `semantic.py`. Ví dụ “Chương 11 có liên quan đến hỏi đáp không?” cho entity chính `CH11` và thêm slot `topic=QUESTION_ANSWERING`; “Bài tập lớn có phần hỏi đáp không?” cho entity chính `PART_II`, vì alias `hỏi đáp` trong họ `ASSIGNMENT_FEATURE` trỏ tới phần II của BTL. Việc chọn **họ thực thể theo nhánh cây** giúp tránh nhầm “Phần I” của môn học với “Phần I” của bài tập lớn.

`Q001–Q025` khớp intent/entity đã ghi trong `sample_queries.txt`. Câu deadline C001 được hiểu thành `GET_DEADLINE(assignment=BTL01, field=deadline)`; điều này chỉ nói hệ thống hiểu câu hỏi, chưa nói KB có ngày nộp. Ba câu Q026–Q028 không có cây nên nhận `UNKNOWN()` và entity `null`. Các nhánh `Q_CONTEXT_*` thuộc hội thoại tùy chọn vẫn là `UNSUPPORTED` cho tới khi có bộ nhớ ngữ cảnh.

## Ranh giới với bước tra KB

Sau Mốc 4, `ask` chạy tiếp từ semantic sang `query.py` và `answer.py` cho cả bảy nhóm bắt buộc. Ví dụ `GET_SCHEDULE(chapter=CH04)` tra ra tuần 4 và tuần 5. Ranh giới trách nhiệm vẫn tách biệt: semantic chỉ tạo yêu cầu; query mới tìm dữ kiện. Phân biệt rõ ba trạng thái:

- `UNKNOWN`: parser không nhận câu hoặc không tìm được thực thể trong cây.
- `UNSUPPORTED_INTENT`: loại truy vấn chưa có handler, hiện chủ yếu là nhánh hội thoại tùy chọn.
- `NOT_FOUND`: handler đã tra nguồn dữ liệu nhưng không có fact cần hỏi. Câu deadline hiện thuộc trường hợp này.

## Khi bổ sung grammar

Thêm cách diễn đạt mới cho nhánh `Q_*` cũ: kiểm tra cây vẫn giữ nút thực thể mà semantic đang dùng, rồi thêm alias nếu tên thực thể mới. Thêm nhánh `Q_*` mới: thêm mapping trong `semantic.py` và ca kiểm tra; khi cần đáp án, thêm handler ở Mốc 4. Test `test_semantic_coverage.py` đối chiếu mọi nhánh bắt buộc trong grammar với các câu kiểm tra, nên nhánh mới chưa có ca sẽ làm test thất bại.
