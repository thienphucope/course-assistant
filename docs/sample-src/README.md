# CO3085 Course Assistant — Classical NLP

Project mẫu hoàn chỉnh cho bài tập lớn **Trợ lý hỗ trợ học tập**. Hệ thống chạy
offline bằng Python, dùng một semantic CFG, Earley chart parser, luật diễn giải
ngữ nghĩa và truy vấn knowledge base. Project **không dùng LLM/RAG**.

## 1. Thành viên

Điền thông tin thật trước khi nộp:

| MSSV | Họ tên | Phần phụ trách |
|---|---|---|
| `<MSSV-1>` | `<Họ tên>` | Grammar, parser |
| `<MSSV-2>` | `<Họ tên>` | Semantic, intent/entity |
| `<MSSV-3>` | `<Họ tên>` | KB, QA, evaluation |
| `<MSSV-4>` | `<Họ tên>` | Dialogue, Docker, báo cáo |

## 2. Hướng đã chọn

- Ngôn ngữ: Python 3.10 trở lên.
- Phần II: Classical NLP dựa trên CFG và luật; không huấn luyện ML.
- Phần III: có xử lý ngữ cảnh hội thoại cục bộ.
- LLM/RAG: không triển khai.
- Dependency: chỉ dùng Python standard library.

## 3. Kiến trúc

```text
Natural-language input
        │
        ▼
Unicode tokenizer ──► Earley parser ──► constituency tree / ()
                                           │
                                           ▼
                                  semantic interpreter
                                  intent + entity + slots
                                           │
                       history-list ────────┤  (câu có tham chiếu)
                                           ▼
                                      predicate
                                           │
                                           ▼
                                  deterministic query
                                           │
                                           ▼
                              indexed text Knowledge Base
                                           │
                                           ▼
                              grounded answer templates
```

Mỗi tầng trả ra cấu trúc riêng. Vì vậy có thể xem chính xác câu bị từ chối ở
parser, sai intent/entity, thiếu dữ liệu ở KB hay sai tại template trả lời.

## 4. Cấu trúc project

```text
sample-src/
├── conf/app.json
├── data/
│   ├── grammar.cfg
│   ├── kb/                       # dữ liệu được query lúc chạy
│   └── scaffolding/              # lexicon và test set
├── input/sentences.txt
├── models/README.md              # không có trained model
├── output/                       # kết quả do lệnh `all` sinh
├── src/hcmut/iaslab/nlp/app/
│   ├── tokenizer.py
│   ├── grammar.py
│   ├── parser.py
│   ├── generator.py
│   ├── entities.py
│   ├── semantic.py
│   ├── kb.py
│   ├── query.py
│   ├── answer.py
│   ├── dialogue.py
│   ├── pipeline.py
│   ├── evaluate.py
│   └── cli.py
├── tests/
├── Dockerfile
├── pyproject.toml
└── run.py
```

Mọi đường dẫn đều được tìm từ project root, nên lệnh không phụ thuộc thư mục làm
việc hiện tại. `faq.txt` được giữ nguyên như dữ liệu nguồn nhưng không được dùng
làm bảng đáp án tắt.

## 5. Grammar và parser

Grammar nằm duy nhất tại `data/grammar.cfg`; parser và generator cùng đọc file
này. Grammar là bộ bốn `G = (V, Σ, R, S)`:

- `V`: các non-terminal viết hoa như `QUESTION`, `Q_SCHEDULE_WEEK`.
- `Σ`: terminal đặt trong dấu nháy như `"tuần"`, `"học"`, `"gì"`.
- `R`: các luật `A -> B C | ...`.
- `S`: start symbol khai báo bởi `%start S`.

Các nhánh `Q_*` mang thông tin semantic. Ví dụ:

```text
Q_SCHEDULE_WEEK -> WEEK_ENTITY WEEK_CONTENT_QUESTION
WEEK_ENTITY -> "tuần" WEEK_NUMBER
```

Câu `Tuần 3 học gì?` tạo cây có nút `Q_SCHEDULE_WEEK` và `WEEK_ENTITY`. Semantic
interpreter vì thế lấy intent từ nhãn nhánh, entity từ slot, thay vì đoán bằng
một API hoặc dò đáp án trong KB.

Parser dùng thuật toán Earley chart:

1. **Predict** các luật khi state đang chờ một non-terminal.
2. **Scan** khi terminal kế tiếp khớp token đầu vào.
3. **Complete** state cha khi một constituent đã hoàn tất.
4. Chỉ nhận câu nếu start state hoàn tất và đã ăn hết token.

Thuật toán xử lý được epsilon, grammar nhập nhằng và đệ quy trái. Cận trên tổng
quát là `O(n³)` theo độ dài câu; với grammar miền hẹp và câu ngắn, chi phí thực tế
rất nhỏ. Nếu không tìm được cây hoàn chỉnh, output bắt buộc là `()`.

## 6. Sinh câu

`generator.py` khai triển non-terminal theo chiều trái sang phải, phân bổ mẫu
theo từng nhánh `Q_*` để các intent đều xuất hiện. Có ba lớp phanh:

- `limit` bắt buộc trong khoảng 1–10.000;
- giới hạn số token;
- giới hạn số sentential form đã duyệt.

Mỗi câu sinh ra được parse lại bằng chính Earley parser trước khi ghi file. Lệnh
`all` dừng với lỗi nếu round-trip `grammar → sentence → tree` thất bại.

## 7. Semantic, intent và entity

`semantic.py` duyệt cây và sinh predicate, ví dụ:

```text
GET_COURSE_INFO(entity=CO3085, course=CO3085, field=CREDITS)
GET_SCHEDULE(entity=WEEK_03, week=WEEK_03)
GET_TOPIC(entity=CH04, chapter=CH04, relation=PARSING)
GET_ASSIGNMENT(entity=PART_I, assignment=BTL01, section=PART_I)
```

Các intent được hỗ trợ:

- `GET_COURSE_INFO`
- `GET_SCHEDULE`
- `GET_TOPIC`
- `GET_LO`
- `GET_ASSIGNMENT`
- `GET_DEADLINE`
- `GET_RESOURCE`
- `GET_RULE`
- `GET_INSTRUCTOR` — nhận diện được nhưng trả not-found vì KB không có dữ liệu
- `CONTEXT_DEPENDENT`
- `UNKNOWN`

Entity được chuẩn hóa thành ID ổn định như `CO3085`, `WEEK_03`, `CH04`, `LO2.5`,
`PART_I`, `SEMANTIC_GRAMMAR`, `AI_USAGE`. Lexicon nguồn nằm trong
`data/scaffolding/entities.txt`; các alias máy dùng được định nghĩa rõ trong
`entities.py`.

## 8. Knowledge base, query và chống bịa thông tin

`kb.py` có loader riêng cho từng dạng dữ liệu bán cấu trúc:

- course info và learning outcomes;
- 15 week records và reverse index `chapter → weeks`;
- 12 chapter records và keyword index;
- các phần của BTL;
- resources;
- regulations.

KB được đọc và kiểm tra một lần khi khởi động. `query.py` chỉ nhận semantic frame,
tra index rồi trả `QueryResult` có query, trạng thái, dữ liệu và source file.
`answer.py` chỉ đổ dữ liệu đó vào template.

Hai trường hợp được tách rõ:

```text
"Tuần 99 học gì?"       → parse thành công → KB không có → not-found
"Ai là tổng thống Pháp?" → parser trả ()    → ngoài miền
```

Không tầng nào tự tạo fact ngoài sáu file `data/kb/*.txt`.

## 9. Ngữ cảnh hội thoại cục bộ

`dialogue.py` lưu history-list ngắn gồm chương, phần BTL, learning outcome và
entity gần nhất. Các phép phân giải được hỗ trợ:

- `nó`, `chương này`, `nội dung này` → chương/entity gần nhất;
- `chương sau` → tăng chapter ID một đơn vị;
- `phần này` → phần BTL gần nhất;
- câu hỏi tài liệu sau một câu lịch học → chapter lấy từ kết quả schedule;
- nội dung của LO nằm ở chương nào → ánh xạ LO sang chương tương ứng.

Lệnh `/reset` trong chế độ interactive xóa toàn bộ ngữ cảnh.

## 10. Cài đặt và chạy

Không bắt buộc cài package:

```bash
python run.py all
```

Hoặc cài editable để có console command:

```bash
python -m pip install -e .
course-assistant all
```

Sinh toàn bộ output với 1.000 câu mẫu:

```bash
python run.py all --input input/sentences.txt --output output --samples 1000
```

Chạy từng chức năng:

```bash
python run.py parse "Tuần 3 học gì?"
python run.py answer --trace "Môn NLP có bao nhiêu tín chỉ?"
python run.py answer "Chương 11 có hỏi đáp không?" "Còn chương sau?"
python run.py generate --limit 100
python run.py evaluate
python run.py interactive
```

Chạy kiểm thử:

```bash
python -m unittest discover -s tests -v
```

## 11. Docker

Image không tải model và không cần network lúc chạy:

```bash
docker build -t co3085-course-assistant .
docker run --rm co3085-course-assistant
```

Để lấy output ra máy host trên Linux/macOS:

```bash
docker run --rm -v "$(pwd)/output:/app/output" co3085-course-assistant
```

PowerShell:

```powershell
docker run --rm -v "${PWD}/output:/app/output" co3085-course-assistant
```

## 12. Các output

Lệnh `all` sinh đúng các artifact của đề:

| File | Nội dung |
|---|---|
| `grammar.txt` | grammar nguồn duy nhất |
| `samples.txt` | các câu sinh hợp lệ, không quá 10.000 dòng |
| `parse-results.txt` | một cây ngoặc hoặc `()` cho mỗi input |
| `semantic.txt` | predicate; có cả bước resolve nếu dùng ngữ cảnh |
| `intent-entity.txt` | JSON Lines chứa intent/entity |
| `query.txt` | truy vấn logic, trạng thái và source KB |
| `answer.txt` | câu hỏi và câu trả lời cuối |
| `evaluation.txt` | metric, bảng từng ca, error analysis |
| `dialogue.txt` | trace và kết quả sáu hội thoại nhiều lượt |

## 13. Đánh giá

Các metric chính:

- intent accuracy;
- entity accuracy;
- query/status accuracy;
- answer/fact accuracy dựa trên các cụm dữ kiện bắt buộc;
- end-to-end accuracy: intent + entity + query + answer cùng đúng;
- out-of-scope rejection;
- dialogue reference accuracy;
- generator/parser round-trip.

`sample_queries.txt` gồm test do đề cung cấp, tám câu được chép nguyên văn từ PDF
và expected query-status/answer terms để chấm full pipeline. `challenge_queries.txt`
là test bổ sung do project tự viết và ghi rõ nguồn; nó cố ý giữ hai cách nói ngoài
grammar để báo cáo ca sai và giới hạn thật.

Kết quả hiện tại: 42/42 case chính thức đúng end-to-end, 6/8 challenge đúng
end-to-end, 6/6 hội thoại phân giải đúng và 18/18 unit test pass.

## 14. Hạn chế

- CFG đóng không thể phủ mọi cách diễn đạt tự nhiên. Mẫu mới phải được thêm vào
  grammar và test lại.
- Topic/resource retrieval dựa trên exact phrase và điểm keyword, chưa có semantic
  similarity.
- Một câu nhập nhằng lấy cây đầu tiên theo thứ tự luật.
- Dialogue chỉ xử lý tham chiếu gần và một số mẫu định trước; không phải Dialogue
  Manager tổng quát.
- KB hiện không có tên giảng viên và ngày tháng hành chính chính thức; hệ thống
  chủ động trả not-found.
