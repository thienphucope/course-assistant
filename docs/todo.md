
# TODO — Course Assistant (CO3085)

> Cái nào **thầy cho sẵn**, cái nào **mình phải tự xây**. Đầu tư: **~70% vào
> Grammar + Cây→Intent**, 30% cho đường ống còn lại.

Legend: ✅ đã có · 🔨 phải xây · 🔥 tốn công/ăn điểm · ⚙️ chuẩn, làm 1 lần · 🔧 plumbing · ✨ optional (điểm cộng)

---

## Thầy đã cho sẵn ✅ (khỏi làm)

- [X]  **List intent** — `data/scaffolding/entities.txt` (GET_SCHEDULE, GET_TOPIC, GET_DEADLINE, …)
- [X]  **Entity vocab + đồng nghĩa** — `entities.txt` (NLP=CO3085=Natural Language Processing; CFG, PCFG, …)
- [X]  **Nội dung KB** — `data/kb/*.txt` (course_info, schedule, topics, assignments, resources, regulations, faq, dialogues)
- [X]  **Test có đáp án** — `data/scaffolding/sample_queries.txt` (cột EXPECTED_INTENT | EXPECTED_ENTITY)

→ `entities.txt` = "đã bóc intent + entity hộ". Với data khác thì phải tự làm khúc này.

---

## Phải tự xây 🔨

### Nền — đọc được KB (làm trước, plumbing)

- [ ]  🔧 **KB loader** — mỗi file `data/kb/*.txt` có format riêng → viết code đọc thành cấu trúc tra được (dict/index)

### Phần I — Grammar & Parser *(bắt buộc)*

- [ ]  🔥 **Grammar (CFG)** — luật phủ mọi cách hỏi cho từng intent → `output/grammar.txt`
- [ ]  ⚙️ **Parser** — đi ngược câu→cây, backtracking; câu ngoài grammar xuất `()` → `output/parse-results.txt`
- [ ]  ⚙️ **Generator** — sinh câu hợp lệ từ grammar, ≤10.000 câu → `output/samples.txt`

### Phần II — Semantic & QA *(bắt buộc, Lựa chọn 1 = Classical)*

- [ ]  🔀 **Cây → semantic** — rút predicate, vd `GET_SCHEDULE(week=3)` → `output/semantic.txt`
- [ ]  🔀 **Intent/Entity** — gắn nhãn intent + trích entity (luật/keyword; KHÔNG cần DL/LLM) → `output/intent-entity.txt`
- [ ]  🔧 **Query builder** — predicate → truy vấn KB → `output/query.txt`
- [ ]  🔧 **Answer + not-found** — tra KB, đổ template; không có thì báo lịch sự, KHÔNG bịa → `output/answer.txt`

### Phần IV — Đánh giá *(bắt buộc)*

- [ ]  🔧 **Evaluation** — chạy `sample_queries.txt`, so EXPECTED, tính accuracy, phân tích ca sai → `output/evaluation.txt`

### Optional ✨ (điểm cộng, làm khi lõi đã chắc)

- [ ]  ✨ **Phần III — Dialogue** — ngữ cảnh cục bộ ("phần này", "nó") → `output/dialogue.txt`
- [ ]  ✨ **Phần II Lựa chọn 2 — RAG/LLM** — retrieve → context → LLM; Phần IV thêm ca hallucination → `output/retrieval.txt`

### Đóng gói

- [ ]  🔧 **README.md** (thành viên, cài đặt, chạy, mô tả kiến trúc/grammar/parser/semantic/intent/KB)
- [ ]  🔧 **Dockerfile** (chấm bằng Docker)

---

## Ai đọc KB khi nào (đừng lẫn)

- **Design time (bạn):** đọc `entities.txt` (schema + vocab) để viết grammar/intent.
- **Run time (máy):** bước intent **KHÔNG** đọc KB; chỉ bước **query** mới mở `data/kb/` — "có thì bóc, không thì rỗng".
