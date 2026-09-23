# Course Assistant — Classical NLP

Course Assistant trả lời câu hỏi về môn NLP bằng một pipeline dựa trên luật:

```text
Câu hỏi → Tokenizer → CFG/Earley Parser → Semantic Frame
         → Intent & Entity → Truy vấn KB → Câu trả lời có nguồn
```

Hệ thống dùng Python và thư viện chuẩn, không dùng LLM để thay thế các bước NLP
cốt lõi. Grammar, semantic và KB được tách riêng để có thể biết một câu thất bại
ở bước nào và tránh tạo thông tin không có trong dữ liệu.

## Thành viên

Nhóm cần thay các ô **CHƯA CUNG CẤP** trước khi đóng gói bản nộp.

| STT | Họ và tên | MSSV | Phụ trách |
| ---: | --- | --- | --- |
| 1 | **Nguyễn Huy Bách** | **2310198** | Grammar, tokenizer, parser, generator |
| 2 | **CHƯA CUNG CẤP** | **CHƯA CUNG CẤP** | Semantic, intent, entity |
| 3 | **CHƯA CUNG CẤP** | **CHƯA CUNG CẤP** | KB, query, answer |
| 4 | **CHƯA CUNG CẤP** | **CHƯA CUNG CẤP** | Tích hợp, đánh giá, Docker, tài liệu |

## Yêu cầu môi trường

Chọn một trong hai cách:

- Python 3.10 trở lên. Chương trình không có thư viện runtime bên thứ ba.
- Docker, dùng để tái tạo môi trường chấm theo yêu cầu đề bài.

Tất cả file văn bản dùng UTF-8. Trên Windows nên thêm `-X utf8` vào lệnh Python.

## Chạy nhanh bằng Python

Mở terminal tại thư mục chứa README này.

```powershell
python -X utf8 run.py ask --trace "Tuần 3 học gì?"
```

Kết quả trace gồm token, cây cú pháp, semantic predicate, intent/entity, đường
truy vấn KB, trạng thái, nguồn và câu trả lời. Ví dụ chính:

```text
Semantic: GET_SCHEDULE(week=WEEK_03)
Intent: GET_SCHEDULE
Entity: WEEK_03
Query: KB.weeks[WEEK_03]
KB result: FOUND
Source: schedule.txt:WEEK 03
```

Tạo lại toàn bộ tám file đầu ra bắt buộc:

```powershell
python -X utf8 run.py batch
```

Chạy riêng bộ đánh giá:

```powershell
python -X utf8 run.py evaluate
```

Chạy kiểm thử hồi quy:

```powershell
python -X utf8 -m unittest discover -s tests -v
```

Các lệnh còn lại:

| Lệnh | Công dụng |
| --- | --- |
| `run.py part1` | Sinh câu từ CFG và ghi grammar, câu sinh, cây parse. |
| `run.py semantic` | Ghi semantic và intent/entity cho input mẫu. |
| `run.py generate --limit 100` | In tối đa 100 câu sinh từ grammar. |
| `run.py ask --trace "..."` | Xử lý một câu và hiển thị toàn bộ pipeline. |
| `run.py batch --input other.txt` | Chạy theo lô với file đầu vào khác. |
| `run.py evaluate --strict` | Trả exit code 1 nếu còn ca đánh giá sai. |

## Chạy bằng Docker

Docker cố định phiên bản Python và thư mục làm việc để máy chấm chạy giống máy
phát triển. Từ thư mục chứa `Dockerfile`:

```powershell
docker build -t course-assistant .
$courseOutput = (Resolve-Path ./output).Path
docker run --rm --mount "type=bind,source=$courseOutput,target=/app/output" course-assistant
```

Container mặc định gọi `python run.py --root /app batch`. Bind mount giúp tám
file được ghi vào `output/` trên máy chủ. Có thể chạy một câu trực tiếp:

```powershell
docker run --rm course-assistant ask --trace "Tuần 3 học gì?"
```

## Kiến trúc và luồng xử lý

1. `tokenizer.py` chuẩn hóa Unicode, chữ hoa/thường, dấu câu và tách token.
2. `grammar.py` đọc, kiểm tra `data/grammar.cfg` và tạo một nguồn CFG dùng chung.
3. `parser.py` dùng thuật toán Earley để tìm cây phủ hết chuỗi token.
4. `semantic.py` đọc nhánh `Q_*` và các node thực thể trên cây.
5. `entities.py` đổi alias như “tuần 3” thành ID chuẩn `WEEK_03`.
6. `query.py` chỉ nhận `SemanticFrame`, chọn chỉ mục thích hợp trong KB.
7. `answer.py` tạo câu tiếng Việt từ dữ kiện và giữ lại nguồn truy vết.
8. `pipeline.py` nối các bước thành một `PipelineResult` quan sát được.
9. `output.py` và `evaluate.py` ghi đầu ra, đo từng tầng và liệt kê ca sai.

Nếu parser không nhận câu, các bước sau trả `UNKNOWN`/`OUT_OF_SCOPE`. Nếu parser
và semantic hợp lệ nhưng KB thiếu fact, query trả `NOT_FOUND`. Hai trạng thái này
được giữ riêng để không nhầm câu ngoài phạm vi với câu hỏi hợp lệ nhưng thiếu dữ liệu.

## Grammar và parser

`data/grammar.cfg` là CFG duy nhất cho cả parser và generator. Grammar bao phủ bảy
nhóm câu hỏi bắt buộc: thông tin môn học, chủ đề, lịch học, bài tập, deadline,
tài liệu và quy định. Nonterminal `Q_*` biểu diễn loại câu hỏi, còn các node như
`WEEK_ENTITY`, `CHAPTER_ENTITY` hoặc `TOPIC_ENTITY` cung cấp slot cho semantic.
Grammar không chứa câu trả lời hay dữ kiện khóa học.

Parser Earley dùng ba thao tác chính: predictor mở rộng nonterminal, scanner khớp
terminal với token, completer ghép các constituent đã hoàn thành. Câu chỉ được
chấp nhận khi parse bắt đầu từ `S` và tiêu thụ toàn bộ token; token dư cho kết quả
`()`. Thuật toán này hỗ trợ đệ quy trái và epsilon trong CFG hiện tại.

`generator.py` duyệt chính CFG đó với giới hạn số trạng thái, độ dài và tối đa
10.000 câu duy nhất. Kiểm tra round trip bảo đảm câu đã sinh có thể parse lại.

## Semantic, intent và entity

Kết quả semantic có hợp đồng:

```text
SemanticFrame(intent, entity, slots, source_branch)
```

Ví dụ cây chứa `Q_SCHEDULE_WEEK` và `WEEK_NUMBER 3` được ánh xạ thành:

```text
GET_SCHEDULE(week=WEEK_03)
```

`source_branch` cho biết nhánh grammar đã kích hoạt. `entity` và các giá trị slot
dùng ID chuẩn trong `data/scaffolding/entities.txt`, giúp semantic và KB không
phụ thuộc vào đúng một cách viết của người dùng.

## Knowledge Base và truy vấn

Sáu file trong `data/kb/` chứa dữ kiện mẫu:

| File | Nội dung |
| --- | --- |
| `course_info.txt` | Mã môn, số tín chỉ, các phần, learning outcome. |
| `schedule.txt` | Tuần, chương và nội dung học. |
| `topics.txt` | Chủ đề và vị trí xuất hiện. |
| `assignments.txt` | Cấu trúc và yêu cầu bài tập. |
| `resources.txt` | Tài liệu được cung cấp. |
| `regulations.txt` | Quy định thư viện, nộp bài và học thuật. |

`kb.py` đọc, chuẩn hóa, tạo chỉ mục và kiểm tra tham chiếu giữa các record.
`query.py` ánh xạ semantic frame sang đường tra như `KB.weeks[WEEK_03]` và trả
`QueryResult` gồm status, data, sources và reason. `answer.py` chỉ diễn đạt dữ kiện
từ kết quả đó. Ví dụ KB hiện không có ngày nộp BTL cụ thể, nên hệ thống trả
`NOT_FOUND` thay vì tự đoán một deadline.

## Đánh giá

`data/scaffolding/gold_queries.txt` chứa 28 câu lõi/ngoài miền có nhãn đầy đủ.
`challenge_queries.txt` chứa 13 câu nhóm tự viết và được báo riêng để tránh xem
bộ phát triển là dữ liệu hoàn toàn mới. Mỗi câu được đo ở năm tầng:

- parse;
- intent;
- entity;
- query status và nguồn;
- các mảnh bằng chứng bắt buộc trong đáp án.

Kết quả hiện tại:

| Bộ đánh giá | Đạt |
| --- | ---: |
| Q001–Q028 có nhãn | 28/28 (100%) |
| Bộ challenge | 11/13 (84,6%) |
| Gộp các nhãn đã khai báo | 39/41 (95,1%) |

Hai lỗi challenge hiện tại đều bắt đầu ở parser: `Tuan 3 hoc gi?` thiếu dấu và
`Số tín chỉ của môn NLP là bao nhiêu?` có trật tự chưa được grammar liệt kê.
Con số 39/41 mô tả hai bộ kiểm thử hiện có, không đại diện cho mọi câu tự nhiên.
Chi tiết được tái tạo trong `output/evaluation.txt`.

## File đầu ra

`run.py batch` ghi:

| File | Nội dung |
| --- | --- |
| `grammar.txt` | CFG dùng trong lần chạy. |
| `samples.txt` | Tối đa 10.000 câu sinh từ CFG. |
| `parse-results.txt` | Cây parse hoặc `()` cho mỗi câu input. |
| `semantic.txt` | Predicate semantic. |
| `intent-entity.txt` | Intent, entity, slots và nhánh nguồn dạng JSON Lines. |
| `query.txt` | Đường tra, status, nguồn và lý do dạng JSON Lines. |
| `answer.txt` | Câu trả lời và nguồn dạng JSON Lines. |
| `evaluation.txt` | Số liệu, ca sai, nguyên nhân, ưu điểm và giới hạn. |

Năm file từ `parse-results.txt` đến `answer.txt` giữ cùng thứ tự câu trong
`input/sentences.txt` để có thể đối chiếu từng tầng.

## Nguồn dữ liệu

Sáu file KB, `sample_queries.txt`, `dialogues.txt` và `faq.txt` bắt nguồn từ bộ
dữ liệu mẫu do ban tổ chức môn học cung cấp. `grammar.cfg`, alias chuẩn hóa,
`gold_queries.txt` và `challenge_queries.txt` do nhóm xây dựng cho hệ thống này.
Dữ liệu lịch, bài tập và quy định là dữ liệu mẫu, không phải thông báo hành chính.

## Hạn chế

- CFG dựa trên luật chỉ nhận các cấu trúc và alias đã được mô hình hóa.
- Câu thiếu dấu hoặc có cách diễn đạt mới có thể bị xếp `OUT_OF_SCOPE`.
- KB mẫu không chứa ngày thi, giảng viên hoặc deadline cụ thể.
- Kiểm tra mảnh đáp án không thay thế việc con người đọc và đánh giá cách diễn đạt.
- Ngữ cảnh hội thoại là phần mở rộng tùy chọn và chưa được tính vào kết quả chính.

## Cấu trúc dự án

```text
project/
├── hcmut/iaslab/nlp/app/   mã nguồn pipeline
├── data/                   grammar, KB và dữ liệu đánh giá
├── input/                  câu hỏi đầu vào mẫu
├── output/                 tám file kết quả bắt buộc
├── models/                 giải thích vì sao không cần model đã huấn luyện
├── tests/                  kiểm thử hồi quy
├── Dockerfile
├── requirements.txt
├── run.py
└── README.md
```

Mã Python mẫu do giảng viên cung cấp cũng đặt package `hcmut/` ngay dưới gốc dự
án. Vì vậy nội dung thư mục này được đặt dưới `project/` khi tạo ZIP; không cần
thêm một lớp `src/` làm thay đổi các đường dẫn đã kiểm thử.

## Kiểm tra và đóng gói

Kiểm tra cấu trúc, output và các thông tin còn thiếu:

```powershell
python -X utf8 package_submission.py check
```

Sau khi điền thành viên và có MSSV thật, tạo ZIP đúng tên đề yêu cầu:

```powershell
python -X utf8 package_submission.py build --student-ids MSSV1 MSSV2 MSSV3 MSSV4
```

File ZIP được tạo trong `../submission/`, có một thư mục gốc `project/` và phải
nhỏ hơn 10 MB. Luôn chạy lại `batch`, test, kiểm tra Docker và mở thử ZIP trước
khi nộp.
