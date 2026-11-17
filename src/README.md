# CO3085 · Course Assistant

Trợ lý hỏi đáp môn Xử lý Ngôn ngữ Tự nhiên theo **Phần II, lựa chọn 1: Classical NLP**.
Nhóm dùng CFG, parser Earley và luật diễn giải cây để truy vấn KB. Chương trình chạy
offline bằng thư viện chuẩn Python. Phần III có bộ nhớ ngữ cảnh cục bộ theo loại thực thể.

## Thành viên

Tên và MSSV: **chờ nhóm bổ sung trước khi nộp**. Cần điền 3–4 thành viên, thứ tự MSSV
trong tên zip và người trình bày từng phần trong kịch bản demo.

## Cài đặt và chạy

Dùng Python 3.11 trở lên (Docker dùng 3.12). Không cần tải model hay cài thư viện NLP bên ngoài.
Chạy các lệnh tại thư mục chứa README này: `src/` trong repo phát triển,
hoặc `project/` sau khi giải nén gói nộp. File văn bản dùng UTF-8.

```bash
python run.py --help
python run.py answer "Môn NLP có bao nhiêu tín chỉ?" --trace
python run.py parse "Tuần 3 học gì?" "Hôm nay trời có mưa không?"
python run.py answer "Tuần 3 học gì?" "Nó có liên quan đến parsing không?" --trace
python run.py interactive
python run.py all
```

`interactive` giữ ngữ cảnh trong phiên; `/reset` xóa ngữ cảnh, `/quit` thoát.
`answer` nhận nhiều câu hoặc `--input input/sentences.txt`; mỗi lần gọi tạo phiên mới.
`all` đọc input, sinh tối đa 1.000 câu mặc định và ghi đủ 9 file trong `output/`.
Chạy từ vị trí khác bằng đường dẫn tới `run.py`; có thể đặt data root bằng `--root PATH`
**trước** tên lệnh.

```bash
python run.py generate --limit 1000 --output output/samples.txt
python run.py evaluate
python run.py all --samples 1000 --input input/sentences.txt --output output
```

## Docker

```bash
docker build -t course-assistant .
docker run --rm course-assistant
docker run --rm course-assistant answer "Môn NLP có bao nhiêu tín chỉ?" --trace
docker run --rm -it course-assistant interactive
```

Container mặc định chạy `all`. Muốn giữ output trên máy, tạo thư mục `output` rồi gắn volume:

```bash
# Linux/macOS
docker run --rm -v "$(pwd)/output:/app/output" course-assistant
```

```powershell
# PowerShell
docker run --rm --mount "type=bind,source=$((Get-Location).Path)/output,target=/app/output" course-assistant
```

Image nền: `python:3.12-slim`. Lần build đầu cần kết nối để tải image nền;
pipeline trong container chạy offline. Đã kiểm chứng ngày 17/11/2026 bằng Docker Engine
29.6.1 trong WSL2 (Ubuntu): build từ gói zip giải nén, chạy mặc định sinh đủ 9 output,
khớp byte với lần chạy Python trực tiếp.

## Kiến trúc

```text
Input → Tokenizer → CFG + Earley → Tree → SemanticFrame
  → DialogueContext → QueryEngine + KnowledgeBase → AnswerGenerator
  → parse / semantic / intent-entity / query / answer
```

| Thành phần | Cách xử lý |
| --- | --- |
| Tokenizer | Unicode NFC, chữ thường, tách dấu câu, giữ `context-free`, `llm/rag`, `lo2.5`, `TP.HCM`; chuẩn hóa `L.O.2.5`. |
| Grammar | `data/grammar.cfg`: `%start S`, luật `->`, lựa chọn `\|`, terminal trong ngoặc kép, alternative rỗng là ε. `QUESTION` có 26 nhánh `Q_*`. |
| Parser | Earley dùng predictor/scanner/completer, nhận khi tiêu thụ hết token; dựng cây nhãn có node ε. Câu bị từ chối xuất `()`. |
| Generator | Mở rộng non-terminal trái nhất, duyệt theo vòng giữa các nhánh, loại câu trùng; giới hạn token, trạng thái và tối đa 10.000 câu. CLI parse lại từng câu trước khi ghi. |
| Semantic | Handler theo `Q_*`, đọc node entity có tên rồi tạo `intent`, `entity`, `slots`, `source_branch`; không truy cập KB. |
| Entity | Lexicon `data/scaffolding/entities.txt` và bảng alias; ID như `WEEK_03`, `CH03`, `LO2.5`, `PART_II`. Nhóm `FEAT_*` xác định phần BTL. |
| KB | Đọc 6 file `.txt` vào collection có kiểu, kiểm tra dữ liệu và lập chỉ mục tuần/chương. Giữ dữ kiện được cấp. |
| Query | Lookup theo intent/slot với tuần, chương, LO, quy định; so khớp từ khóa tìm chủ đề/tài liệu. Trả `found`, `kind`, `data`, `sources`, `reason`. |
| Answer | Template tiếng Việt theo `kind`, dùng dữ kiện query. Phân biệt không hiểu câu, thiếu ngữ cảnh và thiếu dữ kiện. |

Ví dụ: `Tuần 3 học gì?` → `Q_SCHEDULE_WEEK` →
`GET_SCHEDULE(entity=WEEK_03, week=WEEK_03)` → `KB.weeks[WEEK_03]` →
câu trả lời về Chương 3, nguồn `kb/schedule.txt`.

`ASSIGNMENT_FEATURE` gồm `FEAT_PARSING`, `FEAT_SEMANTIC`, `FEAT_CONTEXT`,
`FEAT_EVAL`, tương ứng Phần I–IV. Thêm cách gọi trong nhóm giúp semantic dùng nhãn
cây thay cho danh sách từ khóa riêng. Grammar nhận `parse tree`, `intent`,
`kb`, `hội thoại`, `metric`, alias `dịch máy` và `thư viện có sẵn`.

## Ngữ cảnh và dữ kiện thiếu

Resolver giữ chương, phần BTL, LO gần nhất theo từng loại. Chỉ kết quả `found=True`
mới cập nhật bộ nhớ. Hỗ trợ: quan hệ với chương vừa nhắc, chương kế tiếp, output
phần BTL, tài liệu chương vừa nhắc, chương của LO. Lịch sử tối đa 20 entity.

KB không cung cấp giảng viên hoặc ngày thi cụ thể. `Ai dạy NLP?` vẫn có cây và
semantic `GET_INSTRUCTOR`, nhưng query không tìm thấy nên trả:

> Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học.

Danh sách output riêng của Phần II/III/IV cũng chưa có trong KB.
Tài liệu chương qua ngữ cảnh là tài liệu nền NLP trong KB; KB chưa có quan hệ
tài liệu–chương chi tiết.

## Dữ liệu và output

`data/kb/` chứa `course_info.txt`, `schedule.txt`, `topics.txt`, `assignments.txt`,
`resources.txt`, `regulations.txt`. `data/scaffolding/` chứa alias và bộ đánh giá.
`input/sentences.txt` chứa câu mẫu và cách hỏi bổ sung; bỏ dòng trống, dòng `#`.

| File trong `output/` | Nội dung |
| --- | --- |
| `grammar.txt` | Grammar dùng cho lần chạy. |
| `samples.txt` | Một câu sinh hợp lệ mỗi dòng, không quá 10.000 dòng. |
| `parse-results.txt` | Một cây hoặc `()` cho mỗi câu đầu vào. |
| `semantic.txt` | ID và predicate, kèm frame đã phân giải nếu có ngữ cảnh. |
| `intent-entity.txt` | JSONL gồm câu hỏi, intent gốc/đã giải và entity. |
| `query.txt` | Query, FOUND/NOT_FOUND và nguồn. |
| `answer.txt` | Câu hỏi và câu trả lời. |
| `dialogue.txt` | Trace và kết quả 6 hội thoại. |
| `evaluation.txt` | Chỉ số từng tầng, end-to-end và phân tích lỗi. |

Gói nộp có mã nguồn ở `project/src/hcmut/`; data/input/output/models, README,
Dockerfile và `run.py` ở `project/`. `ProjectPaths` hỗ trợ cả hai layout.
Không có model hoặc file lớn cần link ngoài.

## Đánh giá và kiểm thử

Chấm theo thứ tự câu, reset ngữ cảnh trước mỗi bộ. Một câu đúng end-to-end phải
đồng thời đúng intent, entity, trạng thái query và fact bắt buộc trong đáp án.
Intent ngữ cảnh chấm trước phân giải, entity chấm sau phân giải.

- Bộ đề: **42/42** câu đúng end-to-end.
- Bộ bổ sung: 22 câu, gồm C007/C008, alias mới, thiếu KB, đuôi lạ và nhiều câu hỏi
  trong một lượt. Kết quả chi tiết ở `evaluation.txt`.
- Hội thoại: **6/6** theo dữ liệu được cấp.
- Các bộ đã dùng trong phát triển; chỉ số chưa phản ánh tập kiểm thử độc lập.

Trong repo phát triển:

```bash
cd src
python -m unittest discover -s tests -t .
cd ..
python tools/check_grammar.py --samples 1000 --json docs/validation/grammar-check.json
python tools/package_submission.py
# Bản nộp cuối: thay MSSV bằng số thật (cần Docker; trên Windows chạy được trong WSL2):
python tools/package_submission.py --student-ids MSSV1 MSSV2 MSSV3 --verify-docker
```

Golden chạy code tham khảo nhánh `sample` với grammar hiện tại; adapter tường minh
cho extension và lỗi sample nằm trong `tools/make_golden.py`. Golden KB so khớp
tuyệt đối. Golden và tools chỉ dùng trong repo phát triển, không nằm trong gói nộp.

## Hạn chế và hướng mở rộng

Grammar chưa nhận C007 hỏi số buổi mỗi tuần, C008 dùng `tuần thứ ba`. KB cũng chưa
có số buổi mỗi tuần. Mỗi lượt chỉ nhận một intent; lỗi gõ và câu ghép có thể bị
từ chối. Resolver chọn chương đầu tiên khi có nhiều kết quả và chỉ hỗ trợ các
quan hệ định trước. So khớp tài liệu/chủ đề phụ thuộc từ khóa. Kiểm tra không có
mơ hồ chỉ áp dụng cho các câu đã chạy, chưa chứng minh toàn bộ ngôn ngữ CFG.

Nhóm có thể mở rộng alias/luật kèm hồi quy, bổ sung dữ liệu có nguồn cho thuộc tính
còn thiếu, rồi đánh giá trên câu mới tách khỏi tập phát triển.

## Nguồn và sử dụng AI

- Đề, KB/scaffolding: giảng viên cung cấp cho CO3085.
- Mã khung và cách triển khai tham khảo: nhánh `sample`, `docs/sample-src/`;
  grammar phase 1 tổng hợp đóng góp nhóm.
- Bộ challenge và cách diễn đạt bổ sung trong input: nhóm biên soạn;
  C009–C022 bổ sung trong đợt hoàn thiện với hỗ trợ Codex.
- **Claude Code** (Claude Opus 5.5, Claude Sonnet 5.5), 22/10–17/11/2026: gộp grammar
  phase 1 từ PR #1–#3, soạn hợp đồng giữa các tầng và golden test, điền
  `input/sentences.txt`, nối pipeline/CLI/output/evaluate (T16, T17), sửa tokenizer
  giữ viết tắt `TP.HCM`, chặn độ dài generator, công cụ minh hoạ `tools/visualizer/`,
  rà đề so với output, kiểm chứng Docker trong WSL2 và soạn tài liệu theo dõi task.
- **Codex**, 16–17/11/2026: rà task, sửa parser/semantic, mở rộng grammar, xây công cụ
  kiểm tra, đóng gói và soạn README/báo cáo/kịch bản demo.
- Runtime hỏi đáp không dùng LLM. Thay đổi có hỗ trợ AI được kiểm bằng test hợp đồng,
  hồi quy, round-trip, trace query có nguồn và chạy gói giải nén; nhóm review trước
  khi đưa vào bản nộp và chịu trách nhiệm giải thích được mã nguồn đã nộp.

Báo cáo và kịch bản demo: `report.md`, `demo-script.md` trong gói kiểm tra;
bản repo ở `docs/`. Gói có `demo.mp4`, video tự động từ trace thật, 2 phút 8 giây,
có phụ đề và không có tiếng. Tạo lại video bằng `python tools/render_demo.py`
trong repo (cần Pillow/ffmpeg cho công cụ phát triển). Thông tin thành viên còn chờ
nhóm bổ sung.
