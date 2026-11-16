# Architecture — Course Assistant (bản đồ kiến trúc)

> Đề: `docs/materials/spec.md` → **cái BẮT BUỘC** vs **cái nhóm ĐÃ CHỌN**.
> Cơ chế từng bước: các bài `00`→`09` + `kb-loader` trong thư mục này. Hợp đồng giữa các
> tầng: `docs/contracts.md`. Việc cần làm: `docs/progress/`.
> Quy ước: 🔥 tốn công/ăn điểm · ⚙️ chuẩn làm-1-lần · 🔀 chỗ rẽ · 🔧 plumbing · ✨ optional.

## 0. Hai quyết định lớn nhất (đã chốt)
| Quyết định | BẮT BUỘC (spec) | ĐÃ CHỌN | Vì sao |
|---|---|---|---|
| Ngôn ngữ | Java **hoặc** Python | **Python** | KB loader/parser ngắn hơn nhiều |
| Phần II — **Lựa chọn 1 (Classical/Statistical)** | trong đó: **classical hoặc statistical** | **classical (luật/keyword)** | cây đã nhả intent → keyword đủ, khỏi ML/dữ liệu train |

**Đừng lẫn 2 tầng lựa chọn:**
- **Fork BẮT BUỘC** nằm TRONG Lựa chọn 1 = **classical ↔ statistical** (2 cách làm
  tầng intent/entity, chọn 1). Đã chọn **classical**.
- **LLM/RAG = Lựa chọn 2** (§4.2 "không bắt buộc"), **KHÔNG** thay core NLP (§7.3, §9).
  Nhóm đã chọn Lựa chọn 1 → **không làm**.

## 1. BẮT BUỘC vs ĐÃ CHỌN — bảng tổng
| Thành phần | BẮT BUỘC | ĐÃ CHỌN | Output | Doc |
|---|---|---|---|---|
| **Grammar** 🔥 | phủ 7 nhóm câu hỏi | 1 file `src/data/grammar.cfg`; **26 nhánh `Q_*`** rẽ theo intent để intent+entity rơi ra từ cây | `grammar.txt` | 02, 05 |
| **Generator** ⚙️ | ≤10.000 câu | sinh đều theo nhánh + cap cứng; câu sinh ra phải parse lại được | `samples.txt` | 07 |
| **Parser** ⚙️ | câu→cây, ngoài grammar→`()` | thuật toán tự chọn (skeleton đặt tên `EarleyParser`); dạng cây cố định theo hợp đồng | `parse-results.txt` | 04 |
| **Semantic** 🔀 | câu→predicate | intent = nhãn nhánh `Q_*`; entity = node có tên (`WEEK_ENTITY`…) → ID chuẩn | `semantic.txt` | 05 |
| **Intent/Entity** 🔀 | luật/keyword/ML (không cần DL) | **keyword/luật thuần** (rơi ra từ cây, khỏi ML) | `intent-entity.txt` | 05 |
| **KB + Query** 🔧 | predicate→tra KB | 6 loader nhỏ, index theo ID chuẩn (`WEEK_03`, `CH04`…) | `query.txt` | 03, kb-loader |
| **Answer** 🔧 | đáp + not-found (không bịa) | template theo `kind` + 3 câu fallback | `answer.txt` | 06 |
| **Evaluation** 🔧 | accuracy + phân tích lỗi | `sample_queries` + `challenge_queries` + hội thoại; chẩn đoán ca sai theo tầng | `evaluation.txt` | 08 |
| **Dialogue** ✨ | *(Phần III, không bắt buộc)* | grammar đã có 5 nhánh `Q_CONTEXT_*`; resolver nhớ chương / phần BTL / LO gần nhất | `dialogue.txt` | 09 |
| **LLM/RAG** ✨ | *(Lựa chọn 2, không bắt buộc)* | **bỏ** | `retrieval.txt` | 09 |
| **README+Docker** 🔧 | bắt buộc | mô tả đủ các mục §7.5 | — | — |

**Intent**: 7 cái spec nêu (`GET_COURSE_INFO, GET_TOPIC, GET_SCHEDULE, GET_ASSIGNMENT,
GET_DEADLINE, GET_RESOURCE, GET_RULE`) **+ `GET_LO`** (KB có LO) **+ `GET_INSTRUCTOR`** +
`CONTEXT_DEPENDENT` (câu ngữ cảnh, chờ giải tham chiếu). `GET_INSTRUCTOR` được giữ dù KB
**không có** giảng viên: hỏi luôn ra not-found — chính là ca "KB không có thông tin" mà Phần IV
bắt phải có, và bộ test có câu này (C006).

## 2. Luồng + module (`src/hcmut/iaslab/nlp/app/`)
```
input/sentences.txt
      │
run.py → cli.py ─────────────────────────────────────────► output.py ──► output/*.txt
           │  CourseAssistant.process(câu), giữ ngữ cảnh giữa các câu
           ▼
      pipeline.py ─┬─► parser.py ──► tokenizer.py · grammar.py ◄── data/grammar.cfg · tree.py
                   ├─► semantic.py ─► entities.py ◄── data/scaffolding/entities.txt
                   ├─► dialogue.py      ("nó", "chương này" → entity gần nhất)
                   ├─► query.py ──► kb.py ◄── data/kb/*.txt
                   └─► answer.py

  generator.py ──► samples.txt      evaluate.py ──► evaluation.txt      paths.py (tìm root)
```
- `grammar.cfg` = **1 nguồn**, parser & generator cùng đọc (viết văn phạm 1 lần, dùng 2
  chiều). Copy ra `output/grammar.txt` để nộp.
- `semantic.py` gộp luôn intent/entity (cùng 1 lần duyệt cây) — đừng tách 2 module.
- Mỗi mũi tên giữa hai tầng có hợp đồng dữ liệu cố định: `docs/contracts.md`.
- Xem câu hỏi chạy qua các module (animation): `tools/visualizer/index.html`.

## 3. Layout thư mục
Repo:
```
src/        code (hcmut/…) + data/ input/ output/ models/ tests/ + README.md Dockerfile run.py
docs/       knowledge/ (bài giảng + kiến trúc) · progress/ (tiến độ) · contracts.md · materials/ (đề, data gốc)
tools/      make_golden.py (sinh golden test) · visualizer/
```
Dữ liệu đang dùng nằm ở `src/data/`; bản gốc để khôi phục nằm trong
`docs/materials/NLP_Course_Assistant_Sample_Data.zip`.
Nộp (§7.4) bắt buộc y khuôn `project/{src, data, models, input, output, README.md,
Dockerfile}` → khi đóng gói phải sắp lại; `docs/`, `tools/`, `tests/golden/` gỡ khỏi zip cho gọn
<10MB. Chi tiết: `docs/progress/undone/T24-submission.md`.

## 4. Điểm thiết kế "ngon" (mỗi cái 1 lý do)
1. **Semantic grammar — nhét intent vào tên nhánh `Q_*`** → intent+entity **rơi ra từ cây**,
   khỏi viết bộ phân loại riêng (doc 05). Đây là đòn bẩy lớn nhất.
2. **1 grammar, 2 chiều** (parser đọc + generator đọc) → không đồng bộ 2 bản.
3. **KB loader index theo ID chuẩn** → query chỉ là tra dict O(1), không quét file lúc
   chạy (doc kb-loader).
4. **Fallback tách 3 loại**: câu ngoài văn phạm (`()` ở parser), KB không có (rỗng ở query),
   thiếu ngữ cảnh (không giải được "nó"). Mỗi loại một câu cố định — vẫn thẳng với §4.1(5)
   "không bịa", lại cho evaluation biết lỗi nằm ở tầng nào.
5. **Keyword/luật thuần cho intent**, không ML: spec cho phép, mà cây đã nhả intent
   sẵn → thêm ML là tự làm khổ (doc 05).
6. **Cứng ở chỗ nối, lỏng bên trong**: dữ liệu giữa các tầng cố định + golden test
   (`docs/contracts.md`), còn mỗi người tự chọn cách cài đặt tầng của mình.

`ponytail:` recursive-descent + backtracking đủ cho miền nhỏ nhưng có thể **bùng nổ mũ** khi
nhiều nhánh cùng tiền tố và nhiều ký hiệu rỗng (grammar có `PREFIX`/`SUFFIX` rỗng) — chậm thì
dùng **chart parser / Earley** (Chương 3).

## 5. KHÔNG làm (YAGNI — tiết kiệm để dồn vào grammar + semantic)
- LLM/RAG (Lựa chọn 2) — nhóm đã chọn Classical.
- Dialogue Manager phức tạp, agent, tool-calling, fine-tune (§4.2 nói rõ không cần).
- ML/DL cho intent (keyword đủ).

## 6. Thứ tự build
Chi tiết và phân công: `docs/progress/`.
```
đợt 1 (song song): tokenizer + grammar loader + parser ⚙️ · KB loader 🔧 · generator ⚙️
đợt 2:             semantic + entity 🔀  →  query 🔧
đợt 3:             answer 🔧 · ghép pipeline + CLI + output 🔧
đợt 4:             evaluation 🔧 · (✨ dialogue)
cuối:              README + Dockerfile · báo cáo · video · đóng gói
```
Đổ **~70% công vào grammar + semantic** (doc 00 §7): accuracy Phần IV sống/chết theo
độ phủ grammar, không theo số module. Grammar phase 1 đã xong → trọng tâm chuyển sang
semantic và evaluation.
