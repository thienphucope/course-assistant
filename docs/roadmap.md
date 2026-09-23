# Lộ trình hoàn thành Course Assistant

Tài liệu này đối chiếu đề gốc `materials/NLPAssignment-Course Assistant.pdf`, hướng thiết kế trong `docs/architecture.md`, `docs/todo.md` và trạng thái mã nguồn ngày 22/09/2026. Thời lượng bên dưới là **ước lượng ngày làm việc**, không phải hạn nộp do đề quy định. Nhóm điều chỉnh theo lịch thực tế.

## 1. Đích cần đạt

Chọn hướng **Python + Classical NLP dựa trên luật** mà nhóm đã phác thảo:

`câu hỏi → chuẩn hóa/tokenize → CFG/parser → cây cú pháp → semantic frame + intent/entity → query KB → câu trả lời`.

Một file CFG là nguồn chung của parser và bộ sinh câu. Nhãn `Q_*` trên cây xác định loại truy vấn; các slot trong cây xác định thực thể. KB chỉ được tra ở bước query. Không có dữ kiện thì trả lời không tìm thấy, không tự suy đoán. Dialogue và LLM/RAG chỉ làm sau khi phần bắt buộc đã đạt.

Đầu ra bắt buộc: `output/grammar.txt`, `samples.txt`, `parse-results.txt`, `semantic.txt`, `intent-entity.txt`, `query.txt`, `answer.txt`, `evaluation.txt`; kèm mã nguồn, dữ liệu, input mẫu, README, báo cáo và video demo. `output/dialogue.txt` chỉ cần nếu làm Phần III; `output/retrieval.txt` chỉ cần nếu làm LLM/RAG.

## 2. Trạng thái hiện tại

| Thành phần | Trạng thái ngày 22/09/2026 |
| --- | --- |
| Grammar, tokenizer, parser, generator | Mốc 2 xong: 25/25 câu lõi parse được; `part1` xuất ba file Phần I. |
| Semantic và entity | Mốc 3 xong: 25/25 câu lõi đúng intent/entity; C001 thành `GET_DEADLINE(BTL01)`; `semantic` xuất hai file theo thứ tự input. |
| KB, query và answer | Mốc 4 xong: sáu file KB được đọc; 25/25 câu lõi có đáp án kèm nguồn; deadline thiếu ngày trả `NOT_FOUND`. |
| Batch toàn pipeline | Mốc 5 đã triển khai: một lệnh tạo bảy file Phần I–II theo cùng thứ tự câu hỏi; Mốc 6 bổ sung file đánh giá thứ tám. |
| Docker và evaluator | Mốc 6 đã có `evaluation.txt` cho hai bộ câu; Dockerfile mặc định chạy `batch`, nhưng máy hiện tại không có Docker CLI để smoke test container. |
| Dialogue | Chưa triển khai; các nhánh `Q_CONTEXT_*` là phần mở rộng tùy chọn. |

`docs/architecture.md` và `docs/todo.md` được viết trước khi có bộ khung `src/`; các nhận định “chưa có src/input/output/Dockerfile” và gợi ý parser đệ quy đã cũ. Khi triển khai, lấy mã hiện tại làm chuẩn và cập nhật tài liệu sau khi chốt thiết kế.

## 3. Kế hoạch theo thứ tự phụ thuộc

### Mốc 0 — Chốt dữ liệu, giao diện và tiêu chí đo (1–2 ngày)

**Trạng thái: hoàn thành về thiết kế/dữ liệu ngày 22/09/2026.** Xem `docs/data-contract.md` và bảng 25 câu trong `docs/query-coverage.md`. Việc viết loader, parser và evaluator vẫn thuộc các mốc sau.

- Chọn `src/` làm thư mục `project/` nộp bài; đưa **bản sao có kiểm soát** của dữ liệu thật từ `data/kb/` và `data/scaffolding/` vào `src/data/`, hoặc cấu hình lại đường dẫn để chỉ có một nguồn. Không để hai bản dữ liệu âm thầm khác nhau.
- Lập bảng `Q001–Q025`: câu hỏi, nhóm trong 7 nhóm yêu cầu, nhánh `Q_*`, intent, entity chuẩn, trường KB cần tra, dữ kiện kỳ vọng. Tách `Q026–Q028` (ngoài miền), `Q029–Q034` (ba cặp hội thoại) và thêm ít nhất một ca **grammar hợp lệ nhưng KB thiếu dữ kiện**.
- Chốt các ID dùng xuyên suốt, ví dụ `CO3085`, `WEEK_03`, `CH04`, `BTL01`, `PART_I`, `CFG`, `PCFG`. Viết bảng ánh xạ alias → ID; không dùng đồng thời `COURSE_01` và `CO3085` mà không có chuyển đổi.
- Chốt giao diện giữa người làm semantic và KB theo khung mã hiện có: `SemanticFrame(intent, entity, slots, source_branch)` và `QueryResult(query, found, kind, data, sources, reason)`. Quy định rõ cách suy ra kết quả đánh giá `FOUND`, `NOT_FOUND`, `OUT_OF_SCOPE` từ `QueryResult`.
- Ghi rõ trong README rằng một phần lịch 15 tuần, mốc BTL và quy định trong bộ KB là **dữ liệu mẫu**, không phải thông tin hành chính chính thức. `data/kb/assignments.txt` không có ngày deadline cụ thể; câu hỏi yêu cầu một ngày cụ thể phải trả `NOT_FOUND` nếu không bổ sung nguồn xác thực.

**Hoàn thành khi:** chỉ còn một bộ dữ liệu chạy chính; bảng truy vết 25 ca lõi có đủ các cột; ID và giao diện được cả nhóm thống nhất. Lưu kết quả vào tài liệu ngắn hoặc ngay trong README.

### Mốc 1 — Một lát cắt chạy trọn vẹn (1–2 ngày)

**Trạng thái: hoàn thành cho câu hỏi lịch tuần 3.** Xem `docs/01-first-vertical-slice.md`; parser, semantic, query và answer đều chạy từ dữ liệu thật. Các nhánh intent khác vẫn thuộc các mốc tiếp theo.

Làm một câu trước, ví dụ **“Tuần 3 học gì?”**, theo đúng luồng: token → cây → `GET_SCHEDULE(week=WEEK_03)` → record lịch → câu trả lời có căn cứ. Có thể tạm dùng 1–2 luật CFG và 1 record KB, nhưng phải đi qua đúng các module dự kiến, không hard-code đáp án ở CLI.

**Hoàn thành khi:** một lệnh có thể in cây, semantic, intent/entity, query và answer của câu trên; câu ngoài miền trả `()` và thông báo phù hợp.

### Mốc 2 — Grammar, tokenizer, parser, generator (3–5 ngày)

**Trạng thái: hoàn thành Phần I ngày 22/09/2026.** Xem `docs/02-implementation-part1.md`. Grammar nhận 25/25 câu lõi; lệnh `part1` tạo ba file đầu ra; 10.000 câu sinh ra đều parse lại được. Đây chưa phải độ chính xác trả lời của pipeline.

- Hoàn thiện `tokenizer.py` và `grammar.py`: Unicode tiếng Việt, chữ hoa/thường, dấu câu, khoảng trắng; giữ được `CO3085`, `L.O.2.5`, `LLM/RAG`; kiểm tra luật CFG, ký hiệu thiếu, epsilon, vòng lặp nguy hiểm.
- Mở rộng `src/data/grammar.cfg` theo **7 nhóm bắt buộc**: thông tin chung, chủ đề, lịch, bài tập, deadline, tài liệu, quy định. Dùng 25 câu lõi làm mốc phủ ban đầu, thêm paraphrase như “mấy tín chỉ”, “được học ở đâu”, “có được dùng … không”. Grammar không chứa dữ kiện KB.
- Hoàn thiện parser theo giao diện **Earley hiện có** trong `parser.py`; chỉ chấp nhận khi đã tiêu thụ **toàn bộ token**. Xuất cây ổn định; câu sai/ngoài grammar là `()`.
- Hoàn thiện generator từ **cùng CFG**, giới hạn cứng 10.000 câu, tránh trùng hoặc sinh vô hạn; serialize mỗi dòng một câu.
- Thêm test cho mỗi nhánh quan trọng: câu hợp lệ, biến thể, gần đúng nhưng sai, token dư, dấu câu. Chạy round-trip `parse(generate())`.

**Hoàn thành khi:** cả 7 nhóm có ít nhất một câu parse thành cây; `Q001–Q025` đều parse được (ca nào chưa đạt phải nằm trong danh sách lỗi đang sửa, chưa đóng mốc); mọi câu được sinh trong bộ kiểm tra parse lại được; `samples.txt` không quá 10.000 dòng; câu không hợp lệ cho `()`.

### Mốc 3 — Semantic, intent và entity (2–4 ngày; song song với Mốc 4 sau khi chốt giao diện)

**Trạng thái: hoàn thành phần bắt buộc ngày 22/09/2026.** Xem `docs/03-semantic-intent-entity.md`. Cả 25 câu lõi cho đúng intent/entity; sáu câu bổ sung kiểm tra những nhánh bắt buộc chưa xuất hiện trong bộ 25; ba câu ngoài miền là `UNKNOWN`. Các nhánh hội thoại còn chờ phần tùy chọn.

- Đọc nhãn `Q_*` và slot từ cây, ánh xạ thành predicate/frame thống nhất; ví dụ `GET_TOPIC(topic=PCFG)` hoặc `GET_SCHEDULE(week=WEEK_03)`.
- Hoàn thiện từ điển alias/entity. Kiểm tra các dạng `NLP/CO3085`, `Chương 4/CH04`, `L.O.2.5/LO2.5`, `Bài tập lớn/BTL01`, các tên chủ đề tiếng Anh và tiếng Việt.
- Quy định ưu tiên khi cây có nhiều cách phân tích. Không lấy intent từ dữ kiện KB và không đoán entity bằng chuỗi thô sau khi parser đã thất bại.
- Ghi `semantic.txt` và `intent-entity.txt` theo thứ tự input, có dấu hiệu rõ cho câu `UNKNOWN`.

**Hoàn thành khi:** mỗi nhánh `Q_*` thuộc phần bắt buộc có mapping được kiểm thử; `Q001–Q025` cho đúng intent/entity kỳ vọng hoặc được liệt kê là lỗi cần sửa; câu `()` không bị gán intent hợp lệ.

### Mốc 4 — KB, query và answer (2–4 ngày; song song với Mốc 3)

**Trạng thái: hoàn thành phần bắt buộc ngày 22/09/2026.** Xem `docs/04-kb-query-answer.md`. Bảy nhóm trong 25 câu lõi chạy trọn pipeline, có nguồn dữ kiện. C001 deadline, câu hỏi ngày thi và giảng viên cho kết quả thiếu fact trung thực. File `query.txt` và `answer.txt` theo lô vẫn thuộc Mốc 5.

- Viết loader cho sáu file `course_info`, `schedule`, `topics`, `assignments`, `resources`, `regulations`; chuẩn hóa ID, tạo index, kiểm tra tham chiếu và trường thiếu. Giữ `source` để truy vết câu trả lời.
- Query chỉ nhận semantic frame; handler cho đủ 7 nhóm. Nếu grammar nhận ra một câu nhưng KB không có fact, trả `NOT_FOUND` thay vì suy diễn. Nếu parser thất bại, trả `OUT_OF_SCOPE`.
- Viết template trả lời tiếng Việt cho mỗi loại fact; kiểm tra đáp án lấy từ record nào. Riêng deadline ngày cụ thể phải trả không tìm thấy với KB hiện tại.

**Hoàn thành khi:** mỗi nhóm truy vấn có ít nhất một ca end-to-end, trong đó deadline có thể là ca `NOT_FOUND` trung thực; KB sai định dạng được báo lỗi rõ; không xuất thông tin không có trong KB.

### Mốc 5 — Tích hợp, batch output và CLI (1–2 ngày)

**Trạng thái: mã nguồn và đầu ra đã hoàn thành ngày 22/09/2026; kiểm tra Docker còn chờ môi trường có Docker.** Xem `docs/05-batch-and-docker.md`. Lệnh `batch` tái tạo tám file sau Mốc 6, chạy được từ ngoài `src/`; Dockerfile mặc định gọi lệnh này. Máy phát triển hiện không có `docker` hoặc `podman`, nên chưa thể khẳng định đã chạy được trong container.

- Hoàn thiện `CourseAssistant.from_paths`, `ProjectPaths`, `output.py`; thêm lệnh batch đọc từng dòng `input/sentences.txt` và ghi toàn bộ file theo đề. Các file phải có cùng thứ tự câu hỏi để đối chiếu từng tầng.
- Đặt quy tắc cho dòng trống, lỗi I/O, UTF-8 và kết quả của câu ngoài miền. Lệnh `ask` phục vụ demo; lệnh batch phục vụ chấm.
- Chạy từ thư mục bất kỳ và trong Docker; kiểm tra đường dẫn không phụ thuộc `cwd`.

**Hoàn thành khi:** một lệnh tái tạo được các file `grammar`, `samples`, `parse-results`, `semantic`, `intent-entity`, `query`, `answer`; output không còn `TODO`.

### Mốc 6 — Đánh giá và vòng sửa lỗi (2–3 ngày)

**Trạng thái: hoàn thành đánh giá phần bắt buộc ngày 22/09/2026.** Xem `docs/06-evaluation.md` và `src/output/evaluation.txt`. Bộ có nhãn đầy đủ Q001–Q028 đạt 28/28 trên tiêu chí đã ghi; bộ nhóm tự viết đạt 11/13, với hai lỗi parse được chẩn đoán cụ thể. Hai biến thể câu trong bộ mới đã được thêm vào grammar và kiểm tra hồi quy. Hội thoại Q029–Q034 vẫn là phần tùy chọn.

- Dùng **Q001–Q025** làm bộ lõi; **Q026–Q028** để đo nhận biết ngoài miền. Nếu làm ngữ cảnh, chạy riêng ba cặp **Q029–Q034** theo đúng thứ tự hội thoại; không gộp câu phụ thuộc ngữ cảnh vào accuracy câu đơn.
- Bộ mẫu chỉ cho **intent/entity**, chưa cho đáp án chuẩn đầy đủ. Nhóm cần thêm nhãn cho `query status`, fact/nguồn mong đợi và các mảnh nội dung đáp án, rồi rà bằng tay các ca sai.
- Tạo ca mới cho từng nhóm: paraphrase chưa thấy, grammar gần đúng nhưng sai, thực thể có trong grammar nhưng KB không có, câu dài/dấu câu. Tách bộ dùng để sửa và bộ challenge cuối để tránh chỉ học thuộc 25 mẫu.
- Báo ít nhất: số câu, số đúng, accuracy; nên báo thêm theo tầng `parse`, `intent/entity`, `query`, `answer` để biết lỗi ở đâu. Ghi vài ca sai thực tế và nguyên nhân, không chỉ báo một con số.
- Lặp sửa đúng tầng lỗi: tokenizer/grammar → parser → semantic/ID → KB/query → template; chạy lại toàn bộ hồi quy sau mỗi thay đổi.

**Hoàn thành khi:** `output/evaluation.txt` ghi số liệu có thể tái tạo, cách tính, ca sai, nguyên nhân, ưu/nhược; các test quan trọng không còn `skipTest("TODO")`.

### Mốc 7 — Nộp bài và demo (1–2 ngày)

**Trạng thái: phần kỹ thuật đóng gói đã chuẩn bị ngày 23/09/2026; chưa thể đóng mốc hoàn toàn.** `src/README.md` đã bao phủ các mục 7.5, `src/package_submission.py` kiểm tra và tạo ZIP `project/`, `docs/report-draft.md` chứa bản nháp báo cáo, và `docs/07-submission-and-demo.md` chứa quy trình cùng kịch bản video. Nhóm còn phải điền thành viên/MSSV, chạy Docker trên máy có Docker, hoàn thiện báo cáo/video và kiểm thử ZIP bằng MSSV thật.

- Viết README theo mục 7.5 của đề: thành viên, cài/chạy, kiến trúc, grammar/parser, semantic, intent/entity, KB/query, lựa chọn Classical, đánh giá, giới hạn và nguồn dữ liệu.
- Kiểm tra Docker build/run từ bản nộp sạch; chạy batch, xác nhận tất cả output; bỏ placeholder, file tạm, dữ liệu không dùng. Đặt thư mục `project/` trong ZIP và tên ZIP theo MSSV; giữ kích thước nhỏ theo khuyến nghị của đề.
- Báo cáo có sơ đồ pipeline, lựa chọn thuật toán, ví dụ cây → semantic → truy vấn → đáp, bảng đánh giá và phân tích lỗi. Video ngắn trình diễn ít nhất một câu trả lời đúng và một câu không trả lời được; nếu được gọi thuyết trình, chuẩn bị 5–10 phút.

**Hoàn thành khi:** một người khác chỉ đọc README có thể chạy Docker và tái tạo output; video/báo cáo mô tả đúng chương trình thực tế.

## 4. Phân công và lịch tương đối

Với **4 người**, có thể chia theo ranh giới module sau khi Mốc 0 chốt giao diện:

| Người | Phụ trách chính | Bàn giao |
| --- | --- | --- |
| A | Tokenizer, CFG, parser, generator | Cây cú pháp và câu sinh kiểm tra được |
| B | Entity lexicon, semantic, intent/entity | `SemanticFrame` đúng ID và slot |
| C | KB loader, validator, query, answer | `QueryResult` có fact/nguồn và đáp án |
| D | Pipeline, CLI/batch, output, evaluation, Docker/README | Lệnh chạy trọn vẹn và báo cáo đo lường |

Với **3 người**, gộp D vào B/C theo tải, nhưng vẫn chỉ định một người chịu trách nhiệm tích hợp. Cả nhóm cùng duyệt bảng Q001–Q025, hợp đồng dữ liệu và các ca sai.

- **Tuần làm việc 1:** Mốc 0–2, kèm một lát cắt end-to-end sớm.
- **Tuần làm việc 2:** Mốc 3–5; B/C làm song song, A mở rộng grammar theo lỗi tích hợp.
- **Tuần làm việc 3:** Mốc 6–7; khóa tính năng bắt buộc trước khi ghi hình và đóng gói.

Các mốc này là thứ tự ưu tiên, không phải lịch cứng. Nếu thiếu thời gian, hoàn thành 7 nhóm tối thiểu, đánh giá trung thực và bản nộp chạy được trước khi làm phần mở rộng.

## 5. Chỉ làm sau khi lõi hoàn tất

- **Dialogue Phần III:** trạng thái cục bộ có kiểu (`chapter`, `topic`, `assignment_part`) cho “nó”, “phần này”, “còn chương sau”; kiểm thử Q029–Q034 và ghi `dialogue.txt`. Reset trạng thái giữa các hội thoại.
- **LLM/RAG:** chỉ mở rộng nếu còn thời gian và có thể giải thích retrieval/context/grounding; không thay parser hay semantic bắt buộc. Cần `retrieval.txt` và thêm ca đánh giá hallucination.

## 6. Checklist cuối

- [x] Một nguồn dữ liệu chính; không còn placeholder trong dữ liệu/output bắt buộc.
- [x] CFG phủ đủ 7 nhóm; parser trả cây hoặc `()`; generator dùng cùng CFG và ≤10.000 câu.
- [x] Mỗi câu mẫu được theo dõi qua cây, semantic, intent/entity, query và answer.
- [x] `NOT_FOUND` cho KB thiếu fact; `OUT_OF_SCOPE` cho câu ngoài miền; không bịa deadline.
- [x] `evaluation.txt` có số lượng, accuracy, ca sai và phân tích nguyên nhân.
- [ ] Docker, README, báo cáo, video và ZIP được kiểm tra từ bản nộp sạch; README và công cụ ZIP đã sẵn sàng, còn thông tin nhóm/Docker/video.
