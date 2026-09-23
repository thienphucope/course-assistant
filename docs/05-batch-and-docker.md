# Mốc 5 — Chạy theo lô và tái tạo đầu ra

Các mốc trước chạy từng phần hoặc một câu với `ask`. Mốc này nối các phần thành **một lệnh** để người chấm có thể tái tạo đầu ra Phần I–II từ bản `src/`.

## Lệnh chính

Từ thư mục `src/`:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py batch
```

Kết quả trên dữ liệu hiện tại:

```text
Batch: 29 questions, 26 parsed, 25 found, 1 not found, 3 outside; 10000 generated; evaluation 39/41
```

`29 questions` là 25 câu lõi, 3 câu ngoài miền, 1 câu hỏi deadline thiếu ngày. `26 parsed` là số câu có cây; `25 found` là số câu tìm được fact; `1 not found` là deadline; `3 outside` là ba câu không thuộc grammar. `10000 generated` là câu sinh từ CFG, **khác** 29 câu đầu vào.

## Các file được ghi

| File | Nội dung |
| --- | --- |
| `output/grammar.txt` | Bản grammar của lần chạy. |
| `output/samples.txt` | Tối đa 10.000 câu sinh từ chính grammar, mỗi dòng một câu. |
| `output/parse-results.txt` | Cây cú pháp hoặc `()` của từng câu đầu vào. |
| `output/semantic.txt` | Predicate như `GET_SCHEDULE(week=WEEK_03)` hoặc `UNKNOWN()`. |
| `output/intent-entity.txt` | JSON Lines: intent, entity, slots, nhánh `Q_*`. |
| `output/query.txt` | JSON Lines: số dòng, câu hỏi, đường tra, trạng thái, loại query, các nguồn, lý do nếu thiếu. |
| `output/answer.txt` | JSON Lines: số dòng, câu hỏi, câu trả lời và các nguồn hỗ trợ. |
| `output/evaluation.txt` | Báo cáo điểm trên bộ câu có nhãn và phân tích các ca sai. |

Năm file từ `parse-results.txt` đến `answer.txt` đều có **một dòng cho mỗi câu đầu vào**, cùng thứ tự. `input/sentences.txt` bỏ qua dòng trống và dòng bắt đầu bằng `#`; số dòng `line` trong JSON là **thứ tự câu được xử lý**, bắt đầu từ 1. Ghi UTF-8; file JSON Lines giữ nguyên dấu tiếng Việt.

Ví dụ dòng 5 của `query.txt` có `KB.chapter_weeks[CH04]`, `status=FOUND` và hai nguồn `schedule.txt:WEEK 04`, `schedule.txt:WEEK 05`. Dòng 5 của `answer.txt` chứa câu hỏi và đáp án tương ứng. Dòng 29 có `status=NOT_FOUND`, `sources=[]` và đáp án nói không tìm thấy ngày nộp cụ thể. Ba câu ngoài miền có `parse=()`, `status=OUT_OF_SCOPE`.

## Luồng mã nguồn

`cli.py` đọc câu hỏi một lần, tạo `CourseAssistant`, dùng cùng grammar để sinh câu và gọi `assistant.process(question, use_context=False)` cho từng dòng. `use_context=False` giữ các câu kiểm tra độc lập; nếu làm hội thoại, sẽ có luồng riêng. `output.py` nhận danh sách `PipelineResult` rồi ghi các file theo cùng thứ tự. `paths.py` tìm thư mục `src/` từ thư mục làm việc hoặc vị trí mã nguồn; `--root` vẫn cho phép chỉ định rõ project. Đường dẫn tương đối ở `--input` được hiểu dưới thư mục `src/` đã chọn.

Để chạy từ thư mục khác, gọi `run.py` bằng đường dẫn tuyệt đối và bỏ `--root`; chương trình vẫn tìm đúng `src/`. Với file câu hỏi khác, dùng `batch --input ten-file.txt`; file tương đối được tìm dưới `src/`. File rỗng sau khi bỏ dòng trống/chú thích báo lỗi và trả exit code 2.

## Docker

`src/Dockerfile` dùng Python 3.12, không cần thư viện ngoài và mặc định chạy `batch`. Từ thư mục repo gốc, trên máy có Docker:

```powershell
docker build -t course-assistant ./src
$courseOutput = (Resolve-Path ./src/output).Path
docker run --rm --mount "type=bind,source=$courseOutput,target=/app/output" course-assistant
```

Thư mục `output/` trên máy được gắn vào container để nhận file vừa tạo. Máy phát triển hiện tại **không có lệnh `docker` hoặc `podman`**, nên Dockerfile mới được kiểm tra tĩnh và luồng Python 3.12 đã chạy trực tiếp; build/run container cần được smoke test trên máy có Docker trước khi đóng gói nộp bài.

`evaluation.txt` được tạo từ hai bộ câu có nhãn trong `data/scaffolding/`, độc lập với 29 câu ở `input/sentences.txt`; xem `docs/06-evaluation.md`. Tổng cộng `batch` tạo tám file bắt buộc. `dialogue.txt` chỉ cần nếu làm phần mở rộng hội thoại.
