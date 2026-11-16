# Báo cáo BTL CO3085: Course Assistant

**Phiên bản nội dung:** 2026-11-16. **Hướng thực hiện:** Classical NLP, Phần II lựa chọn 1.
**Thành viên/MSSV:** nhóm bổ sung trước khi nộp. Phân công và định dạng bản nộp chờ nhóm chốt.

## 1. Bài toán và phạm vi

Nhóm xây trợ lý hỏi đáp về môn Xử lý Ngôn ngữ Tự nhiên từ KB giảng viên cung cấp.
Người dùng hỏi thông tin môn, chương/chủ đề, lịch học, bài tập lớn, deadline,
tài liệu và quy định. Hệ thống phải thể hiện cây cú pháp, biểu diễn ngữ nghĩa,
intent/entity, truy vấn và câu trả lời. Nếu thiếu dữ kiện, chương trình báo thiếu.

Nhóm chọn xử lý dựa luật. Runtime dùng thư viện chuẩn Python, không gọi API hay
model ngôn ngữ. Nhóm có triển khai phần mở rộng ngữ cảnh cục bộ cho các dạng
tham chiếu định trước; không xây dialogue manager tổng quát.

## 2. Dữ liệu và nguồn

Sáu file trong `data/kb/` là nguồn dữ kiện: `course_info.txt`, `schedule.txt`,
`topics.txt`, `assignments.txt`, `resources.txt`, `regulations.txt`. Scaffolding
của đề cung cấp alias, 42 câu mẫu và 6 hội thoại. Nhóm bổ sung các cách diễn đạt
trong input và bộ challenge 22 câu; header bộ challenge ghi rõ nguồn biên soạn.

Loader tạo collection cho môn học, 15 tuần, 12 chương, BTL, 8 tài liệu và quy định;
lập chỉ mục `chapter_weeks` và kiểm tra tính nhất quán. Ví dụ `chapter_number`
là số nguyên, entity chương có ID `CH03`. Nhóm giữ golden KB so khớp tuyệt đối
để phát hiện thay đổi dữ kiện hoặc kiểu.

KB không có tên giảng viên, ngày thi, số buổi học mỗi tuần hoặc danh sách output
riêng cho mọi phần BTL. Hệ thống không điền các trường này bằng suy đoán.

## 3. Kiến trúc và ranh giới các tầng

```text
Input → normalize/tokenize → CFG + Earley → Tree
      → SemanticInterpreter + EntityLexicon → SemanticFrame
      → DialogueContext.resolve → QueryEngine(KnowledgeBase)
      → AnswerGenerator → DialogueContext.update → Output/Evaluation
```

`PipelineResult` lưu câu gốc, token/cây, frame gốc, frame đã giải ngữ cảnh, query,
nguồn và answer. Từng tầng nhận dữ liệu từ tầng trước qua kiểu tường minh.
Semantic không đọc KB; query không đọc lại câu gốc; answer chỉ dùng `QueryResult`.
Nhóm kiểm các ranh giới này bằng test hợp đồng độc lập với tầng trước.

## 4. Phần I: grammar, parser và sinh câu

### 4.1 Tokenizer

Tokenizer chuẩn hóa Unicode NFC và chữ thường, bỏ khoảng trắng thừa, tách dấu
câu `? ! . , : ;`, bỏ dấu ngoặc kép và giữ từ ghép kỹ thuật như `context-free`,
`llm/rag`, `lo2.5`, `TP.HCM`. `L.O.2.5` được chuẩn hóa thành `lo2.5`.
Grammar và entity dùng cùng quy ước token để tránh lỗi nhận câu sau khi sinh.

### 4.2 Thiết kế grammar

Grammar có **26 nhánh `Q_*`**, tương ứng các loại yêu cầu hoặc hành động ngữ cảnh.
Luật gốc `S → PREFIX QUESTION SUFFIX` tách lời mở đầu và từ lịch sự khỏi nội dung.
Nhánh lịch học dùng `WEEK_ENTITY`, nhánh chương dùng `CHAPTER_ENTITY`; semantic
đọc các node này mà không phải tìm lại từ khóa trong câu thô.

Ví dụ:

```text
Q_SCHEDULE_WEEK → WEEK_ENTITY WEEK_CONTENT_QUESTION
WEEK_ENTITY → "tuần" WEEK_NUMBER
WEEK_CONTENT_QUESTION → "học" "gì" | ...
```

Phase 1 giữ cấu trúc grammar tham khảo và gộp các cách diễn đạt từ đóng góp nhóm.
Đợt T18 giữ nguyên 26 nhánh và bổ sung nhóm tính năng:

| Node | Phần BTL | Ví dụ |
| --- | --- | --- |
| `FEAT_PARSING` | I | parser, grammar, parse tree, phân tích cú pháp |
| `FEAT_SEMANTIC` | II | semantic, hỏi đáp, intent, entity, KB |
| `FEAT_CONTEXT` | III | ngữ cảnh, hội thoại, tham chiếu |
| `FEAT_EVAL` | IV | đánh giá, test set, metric, kiểm thử |

Nhóm cũng thêm `dịch máy` vào resource topic và `thư viện có sẵn` vào rule topic.
Việc thêm từ trong đúng nhóm giữ ổn định phần BTL mà handler trả về.

### 4.3 Parser Earley

Mỗi trạng thái lưu luật, vị trí dấu chấm, vị trí bắt đầu và các con đã dựng.
Predictor mở các luật của non-terminal kế tiếp; scanner khớp terminal và tiến
sang vị trí token tiếp theo; completer ghép node hoàn chỉnh vào trạng thái chờ.
Chỉ trạng thái gốc hoàn tất tại cuối input mới tạo kết quả chấp nhận.

Luật ε tạo node không có con. Khi một trạng thái chờ mới xuất hiện sau khi node
ε đã hoàn tất, predictor lấy node từ chỉ mục nullable tại vị trí đó. Cách này
xử lý trường hợp completer đã chạy trước trạng thái chờ.

`parse()` chọn cây đầu tiên theo thứ tự luật/agenda. `parse_trees(limit=2)` tìm
tối đa hai cây khác nhau để phát hiện mơ hồ trong kiểm tra. Parser giới hạn
số dẫn xuất cho mỗi chart item để tránh lặp vô hạn với chu trình nullable.
Đây là cơ chế phát hiện có giới hạn, không phải thuật toán đếm mọi cây của CFG.

Ví dụ cây:

```text
(S (PREFIX ε)
   (QUESTION (Q_SCHEDULE_WEEK (WEEK_ENTITY tuần (WEEK_NUMBER 3))
                              (WEEK_CONTENT_QUESTION học gì)))
   (SUFFIX (END_MARK ?)))
```

Câu `Tuần 3 học gì? xyz` bị từ chối vì còn token chưa tiêu thụ. Câu ngoài miền
`Hôm nay trời có mưa không?` cho `()` và intent `UNKNOWN`.

### 4.4 Sinh câu và kiểm tra grammar

Generator mở rộng non-terminal trái nhất, duyệt các nhánh theo vòng, giới hạn
token/trạng thái và loại câu trùng. Nó chuẩn hóa câu hỏi theo các suffix mà CFG
cho phép, viết hoa đầu câu và giữ chữ viết tắt kỹ thuật. CLI parse lại toàn bộ
câu sinh trước khi ghi. `samples.txt` có tối đa 10.000 dòng.

`tools/check_grammar.py` kiểm tra định nghĩa lặp, luật lặp, non-terminal chưa định
nghĩa/không tới được, terminal hoa, lệch tokenizer và đủ 26 nhánh. Công cụ chạy
câu mẫu, challenge, hội thoại, rồi round-trip câu sinh và kiểm cả semantic/query.
Thiếu KB hoặc thiếu ngữ cảnh cho câu đứng riêng được liệt kê với nguyên nhân;
đó là kết quả hợp lệ của các nhánh chủ đích hỗ trợ fallback.

## 5. Phần II: diễn giải ngữ nghĩa và hỏi đáp

### 5.1 Từ cây sang frame

`SemanticInterpreter` tìm nhánh con `Q_*` của `QUESTION`, chọn handler, trích
slot từ node có tên và dùng lexicon để lấy ID chuẩn. Ví dụ:

```text
Tuần 3 học gì?
→ Q_SCHEDULE_WEEK
→ GET_SCHEDULE(entity=WEEK_03, week=WEEK_03)
→ KB.weeks[WEEK_03]
```

Frame có `intent`, `entity`, `slots`, `source_branch`. `BTL có phần parse tree
không?` dùng nhãn `FEAT_PARSING` để tạo `GET_ASSIGNMENT`, entity `PART_I`, slot
`feature=parse tree`. Cụm từ gốc được giữ để giải thích kết quả.

### 5.2 Truy vấn và trả lời

Query dispatch theo intent/slot. Tuần, chương, LO và rule dùng ID để tra collection.
Topic search ưu tiên từ khóa khớp nguyên cụm rồi nội dung; resource search chấm
điểm tên tài liệu và mô tả sử dụng. Quan hệ LO–chương dùng bảng ánh xạ cố định
trong miền này. Kết quả gồm trạng thái, loại dữ kiện, dữ liệu và đường dẫn nguồn.

Answer chọn template theo `kind`; ví dụ `SCHEDULE_WEEK` chứa tuần, chương, chủ đề
và milestone nếu có. Một query `found=True` phải sinh câu trả lời chứa dữ kiện.
Nhóm sửa trường hợp sample đánh dấu found dù phần BTL không có output trong KB.

Ba fallback phân biệt lỗi cú pháp/ngoài miền, thiếu ngữ cảnh và thiếu dữ kiện.
Với dữ kiện không có, hệ thống trả nguyên văn thông báo của đề:

> Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học.

Nguồn trong trace giúp người dùng kiểm lại dữ kiện. Quy tắc truy vấn vẫn có thể
chọn tài liệu/chủ đề chưa phù hợp; việc dùng template không bảo đảm mọi đáp án
đều đúng ngữ nghĩa.

## 6. Phần III: ngữ cảnh cục bộ

Resolver giữ riêng chương, phần BTL và LO gần nhất. Một lần hỏi phần BTL không
ghi đè chương đang nhớ. `update()` chỉ lưu khi query tìm thấy; câu thiếu dữ kiện
không thay thực thể đã có. `/reset` xóa bộ nhớ của phiên.

Hỗ trợ năm hành động: quan hệ với chương đang nhớ; chương tiếp theo trong 1–12;
output của phần BTL; tài liệu cho chương; chương của LO.

Ví dụ `Tuần 3 học gì?` cung cấp `chapter_id=CH03`. Câu `Nó có liên quan đến
parsing không?` tạo frame ngữ cảnh, sau đó resolver trả:

```text
GET_TOPIC(entity=CH03, chapter=CH03, relation=PARSING)
```

Trace giữ cả frame gốc và frame đã giải cùng giải thích tham chiếu.
Nếu chưa có chương, frame ngữ cảnh giữ nguyên và answer yêu cầu bổ sung ngữ cảnh.

## 7. Phần IV: phương pháp và kết quả đánh giá

Một câu đúng end-to-end phải đồng thời đúng intent, entity, query/status và các
fact bắt buộc trong câu trả lời. Không so câu trả lời bằng chuỗi nguyên văn.
Các bộ chạy theo thứ tự, reset ngữ cảnh một lần trước mỗi bộ; hội thoại reset
giữa các phiên. Intent ngữ cảnh chấm trước resolve, entity chấm sau resolve.

| Bộ | Số câu/phiên | Đúng | Tỷ lệ |
| --- | ---: | ---: | ---: |
| Câu mẫu của đề | 42 | 42 | 100% |
| Challenge nhóm bổ sung | 22 | 20 | 90,91% |
| Tổng câu hỏi hai bộ | 64 | 62 | 96,88% |
| Hội thoại của đề | 6 | 6 | 100% |

Trong cả hai bộ câu hỏi, số đúng intent/entity/query-status/answer-fact bằng số
đúng end-to-end nêu trên. File `output/evaluation.txt` lưu kết quả từng ca và
nguyên nhân lỗi; `output/dialogue.txt` lưu từng lượt và thực thể đã giải.

Kiểm thử tự động kiểm các tầng trên golden, các ca hồi quy nullable/left recursion,
mơ hồ, trailing token, context reset và thiếu KB. Golden tham khảo độc lập chạy
nhánh `sample` với grammar hiện tại; adapter T18 tường minh bổ sung nhãn FEAT và
alias, đồng thời sửa ba kết quả found/fallback sai của sample. Không sửa tay golden.

Kiểm tra 1.000 câu sinh phủ 26/26 nhánh, parse lại được và không có `UNKNOWN`
hoặc entity rỗng ngoài nhánh ngữ cảnh. Công cụ kiểm ít nhất hai cây để tìm mơ hồ
trên hợp các câu đã chạy; số chính xác và trace lưu ở `docs/validation/grammar-check.json`.
Không diễn giải kết quả này thành chứng minh CFG không mơ hồ.

### 7.1 Phân tích ca sai và giới hạn

| Ca | Mong đợi | Kết quả và nguyên nhân | Hướng xử lý |
| --- | --- | --- | --- |
| C007: “Môn NLP học mấy buổi mỗi tuần?” | Nhận yêu cầu trong miền, báo thiếu KB | Grammar chưa có field số buổi nên `()`/UNKNOWN. | Thêm field và nhánh diễn đạt trong intent môn học; KB vẫn thiếu nên phải NOT_FOUND. |
| C008: “Tuần thứ ba tụi mình học bài gì vậy?” | Tuần 3, Chương 3 | Grammar mới nhận số tuần dạng chữ số. | Thêm ordinal vào constituent tuần và resolver tương ứng; kiểm tra hồi quy. |

C015 (tuần 99), C016 (chương 13), C017 (LO9.9), C018 (output Phần II) kiểm cách
báo thiếu dữ kiện đúng; đó không phải ca hệ thống trả lời sai. C019 kiểm đuôi lạ,
C020 kiểm hai câu hỏi trong một lượt; hệ thống từ chối theo phạm vi một intent.
C009–C014 kiểm các feature/alias bổ sung. Không dùng dữ kiện tự tạo để tăng điểm.

Các bộ này đã dùng khi phát triển grammar và luật, chưa có tập giữ lại độc lập.
Tỷ lệ 96,88% phản ánh bộ 64 câu hiện tại; không dùng nó để dự đoán chất lượng
trên câu hỏi bất kỳ. Golden dùng cùng baseline tham khảo nên cũng có thể kế thừa
giới hạn baseline; nhóm bổ sung kiểm tra trực tiếp trên dữ kiện KB và ca phản ví dụ.

## 8. Ưu điểm, hạn chế và hướng mở rộng

Nhóm có thể lần ngược một đáp án về query, frame và cây; chương trình chạy offline,
không cần model, phân biệt được thiếu cú pháp với thiếu dữ kiện. Các hợp đồng
cho phép kiểm từng tầng và thay thuật toán bên trong mà giữ ranh giới dữ liệu.

Grammar đóng nên độ phủ cách diễn đạt còn hẹp. Tách token giữ `chữ.chữ` giúp nhận
`TP.HCM` nhưng cũng giữ lỗi gõ dính dấu chấm. Generator thiên về các cách diễn đạt
ngắn và không đại diện phân bố câu hỏi tự nhiên. Quy tắc topic/resource phụ thuộc
từ khóa; tài liệu cho chương qua ngữ cảnh mới là tài liệu nền, chưa gắn chương cụ
thể. Resolver chỉ xử lý quan hệ định trước, có thể chọn chương đầu tiên khi có
nhiều kết quả. Parser kiểm mơ hồ có giới hạn, chưa cung cấp parse forest tổng quát.

Hướng mở rộng: thu câu hỏi mới có nhãn và tách tập đánh giá; bổ sung ordinal,
alias và quy tắc với test hồi quy; bổ sung dữ kiện có nguồn; yêu cầu làm rõ khi
tham chiếu có nhiều ứng viên; xây liên kết tài liệu–chương để truy vấn chính xác hơn.

## 9. Chạy lại và sản phẩm

Trong thư mục ứng dụng: `python run.py all` sinh 9 file output; `python run.py
answer "Tuần 3 học gì?" --trace` thể hiện các bước. README hướng dẫn đầy đủ lệnh
Python/Docker. Gói kiểm tra có đúng cấu trúc `project/src`, `data`, `models`,
`input`, `output`, README và Dockerfile; loại golden, tools, cache và data gốc cũ.

`tools/package_submission.py` chạy source, đóng zip, giải nén sang thư mục mới,
chạy lại từ cwd khác và đối chiếu cả 9 output theo byte. `--verify-docker` thêm
build/run container và đối chiếu output. Máy thực hiện đợt này chưa có Docker;
nhóm phải hoàn tất bước đó trước nộp. Tên/MSSV và định dạng bản báo cáo chờ bổ sung.

Kịch bản video và lời trình bày: `docs/demo-script.md`. `tools/demo.py` tạo trace
thực thi 7 câu, có trường hợp không có KB và ngoài miền; bản lưu là
`docs/demo-transcript.txt`. `tools/render_demo.py` tạo video MP4 dài 2 phút 8 giây,
1280×720, có phụ đề, không có tiếng, từ kết quả thực thi thật. Đây là bản phát lại
tự động, không phải quay màn hình. Gói kiểm tra có `demo.mp4`. Nhóm bổ sung thông
tin thành viên và có thể quay/thuyết minh theo kịch bản trước khi nộp.

## 10. Tài liệu tham khảo và khai báo AI

1. Đề BTL CO3085 “Trợ lý hỗ trợ học tập”, bản đọc tại `docs/materials/spec.md`;
   KB và scaffolding do giảng viên cung cấp.
2. Mã khung, thuật toán và output tham khảo ở nhánh `sample`, `docs/sample-src/`.
   Nhóm tham khảo cấu trúc và kiểm bằng hợp đồng; không sửa nhánh tham khảo.
3. Đóng góp grammar phase 1 của nhóm trong PR #1–#3; các module được tích hợp
   trong PR #4/#5/#7. Chi tiết quyết định chấp nhận tại `docs/progress/done/T03-grammar-phase1.md`.
4. Bộ challenge và các cách diễn đạt bổ sung trong input do nhóm biên soạn.

**Khai báo AI cho đợt 2026-11-16:** Codex hỗ trợ đọc task/spec, sửa nullable và
kiểm mơ hồ của parser, mở rộng grammar/semantic FEAT, bổ sung ca kiểm thử, công cụ
kiểm grammar/đóng gói, sửa layout launcher, soạn README/báo cáo/kịch bản demo.
Codex chạy test hợp đồng và hồi quy, sinh lại golden từ baseline, kiểm câu sinh,
truy vấn có nguồn và chạy gói giải nén. Runtime hỏi đáp không dùng LLM.

Nhóm cần review từng thay đổi, hiểu và giải thích lại thuật toán trước thuyết
trình, xác nhận nội dung báo cáo và bổ sung khai báo AI cho các phần làm trước
đợt này. Tài liệu này không khẳng định nhóm đã hoàn tất các bước xác nhận đó.

**Bổ sung từ đợt rà thiết kế sau mốc `9096375`:** Codex hỗ trợ đối chiếu 19 ticket
với implementation, viết tài liệu thiết kế và bổ sung test phản ví dụ cho guard
query, context sau LO, grammar loader/generator, xuất grammar, chọn CFG kiểm tra
và cách chấm đánh giá. Các lỗi đã sửa và kết quả kiểm chứng lưu tại
`docs/validation/design-audit.md`; không thêm dữ kiện KB để sửa ca trả lời sai.
