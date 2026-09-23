# Mốc 1 - câu hỏi đầu tiên chạy trọn pipeline

Mốc này dùng một câu duy nhất để kiểm tra các module đã nối với nhau đúng cách: **“Tuần 3 học gì?”**. Đây là lát cắt đầu tiên, chưa phải hệ thống hỏi đáp hoàn chỉnh cho mọi nhóm câu.

## Chạy thử

Từ thư mục `src/`, với Python 3.12 có trên PATH:

```powershell
python -X utf8 run.py --root . ask --trace 'Tuần 3 học gì?'
```

Trong môi trường Codex hiện tại, Python không có trên PATH; lệnh tương đương đã được kiểm tra là:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py --root . ask --trace 'Tuần 3 học gì?'
```

Muốn chỉ xem đáp án, bỏ `--trace`. Muốn thấy trường hợp ngoài miền, đổi câu hỏi thành `Hôm nay ở TP.HCM có mưa không?`.

## Các bước và vai trò từng file

```text
“Tuần 3 học gì?”
  ├─ tokenizer.py                 → ['tuần', '3', 'học', 'gì', '?']
  ├─ grammar.py + grammar.cfg      → đọc các luật câu hỏi
  ├─ parser.py + tree.py           → cây có nhánh Q_SCHEDULE_WEEK
  ├─ entities.py + semantic.py     → GET_SCHEDULE(week=WEEK_03)
  ├─ kb.py + schedule.txt          → bản ghi WEEK 03
  ├─ query.py                      → KB.weeks[WEEK_03], nguồn schedule.txt
  └─ answer.py                     → câu trả lời ghép từ các topic trong bản ghi
```

`pipeline.py` tạo các thành phần và gọi đúng thứ tự; `cli.py` in dấu vết khi có `--trace`.

Đoạn cây quan trọng là:

```text
(S
  (PREFIX ε)
  (QUESTION
    (Q_SCHEDULE_WEEK (WEEK_ENTITY tuần (WEEK_NUMBER 3)) học gì))
  (SUFFIX (END_MARK ?)))
```

- `S` là câu hoàn chỉnh.
- `PREFIX ε` nghĩa là không có lời mở đầu như “cho mình hỏi”.
- `Q_SCHEDULE_WEEK` cho biết đây là dạng hỏi lịch theo tuần.
- `WEEK_ENTITY` chứa “tuần 3”; từ điển chuẩn hóa nó thành `WEEK_03`.
- `SUFFIX` chứa dấu `?`; parser phải tiêu thụ cả dấu này và mọi token khác mới chấp nhận câu.

`SemanticFrame` chỉ nói **cần tra gì**; nó không chứa thông tin tuần 3 học gì. `query.py` lấy `WEEK_03` để tra `KnowledgeBase.weeks`, còn `answer.py` chỉ dùng dữ kiện tìm được để tạo câu trả lời. `Source: schedule.txt:WEEK 03` trong trace cho biết đáp án dựa vào mục nào của KB.

## Ba kết quả cần phân biệt

| Câu hỏi | Parse | Ý nghĩa | Kết quả |
| --- | --- | --- | --- |
| “Tuần 3 học gì?” | Có cây | `GET_SCHEDULE(week=WEEK_03)` | Trả các chủ đề có trong lịch tuần 3 |
| “Hôm nay ở TP.HCM có mưa không?” | `()` | `UNKNOWN` | Báo ngoài văn phạm/phạm vi |
| “CO3085 có bao nhiêu tín chỉ?” | Có cây | `UNSUPPORTED` ở mốc này | Báo loại câu hỏi này chưa được nối semantic/KB |

Trường hợp cuối rất quan trọng: grammar đã nhận ra cấu trúc câu, nhưng handler trả lời tín chỉ thuộc các mốc sau. Không nên gọi đó là câu ngoài grammar hoặc tự lấy dữ kiện bằng cách bỏ qua pipeline.

## Kiểm tra và giới hạn hiện tại

Từ `src/`, chạy:

```powershell
python -X utf8 -m unittest discover -s tests -v
```

Lần kiểm tra mốc 1 có **21 test, 0 lỗi, 3 test cũ còn skip**: generator round-trip, toàn bộ intent end-to-end và dialogue. CFG seed hiện parse được **10/25** câu đơn lõi Q001–Q025; đây là độ phủ *cú pháp*, chưa phải accuracy trả lời. Generator, các intent khác, dialogue và lệnh batch ghi đủ file `output/` còn ở các mốc tiếp theo.
