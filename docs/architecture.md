# Architecture — Course Assistant (bản đồ build + đề xuất)

> Từ spec (`materials/spec.md`) → **cái BẮT BUỘC** vs **cái tôi ĐỀ XUẤT cho ngon**.
> Cơ chế từng bước: `docs/00`→`09` + `kb-loader`. Việc code: `todo.md`.
> Quy ước: 🔥 tốn công/ăn điểm · ⚙️ chuẩn làm-1-lần · 🔀 chỗ rẽ · 🔧 plumbing · ✨ optional.

## 0. Hai quyết định lớn nhất (chốt trước khi gõ code)
| Quyết định | BẮT BUỘC (spec) | ĐỀ XUẤT | Vì sao |
|---|---|---|---|
| Ngôn ngữ | Java **hoặc** Python | **Python** | bạn đang dùng, KB loader/parser ngắn hơn nhiều |
| Phần II — **Lựa chọn 1 (Classical/Statistical)** | trong đó: **classical hoặc statistical** | **classical (luật/keyword)** | cây đã nhả intent → keyword đủ, khỏi ML/dữ liệu train |

**Đừng lẫn 2 tầng lựa chọn:**
- **Fork BẮT BUỘC** nằm TRONG Lựa chọn 1 = **classical ↔ statistical** (2 cách làm
  tầng intent/entity, chọn 1). Đề xuất **classical**.
- **LLM/RAG = Lựa chọn 2 = optional "sau nữa"** (§4.2 "không bắt buộc"), **KHÔNG**
  thay core NLP (§7.3, §9). Chỉ đụng khi core + eval đã chắc (✨).

## 1. REQUIRED vs PROPOSED — bảng tổng
| Thành phần | BẮT BUỘC | ĐỀ XUẤT (cho ngon) | Output | Doc |
|---|---|---|---|---|
| **Grammar** 🔥 | phủ 7 nhóm câu hỏi | 1 file text nguồn duy nhất; **Q rẽ theo intent** để intent+entity rơi ra từ cây | `grammar.txt` | 02, 05 |
| **Generator** ⚙️ | ≤10.000 câu | random + cap cứng; dùng round-trip test parser | `samples.txt` | 07 |
| **Parser** ⚙️ | câu→cây, ngoài grammar→`()` | recursive-descent + backtracking | `parse-results.txt` | 04 |
| **Semantic** 🔀 | câu→predicate | intent = nhãn nút Q; entity = terminal ở slot | `semantic.txt` | 05 |
| **Intent/Entity** 🔀 | luật/keyword/ML (không cần DL) | **keyword/luật thuần** (rơi ra từ cây, khỏi ML) | `intent-entity.txt` | 05 |
| **KB + Query** 🔧 | predicate→tra KB | 6 loader nhỏ, index theo entity | `query.txt` | 03, kb-loader |
| **Answer** 🔧 | đáp + not-found (không bịa) | template/intent + 1 message not-found chung | `answer.txt` | 06 |
| **Evaluation** 🔧 | accuracy + phân tích lỗi | chạy `sample_queries.txt`, bảng + chẩn đoán ca sai | `evaluation.txt` | 08 |
| **Dialogue** ✨ | *(Phần III, không bắt buộc)* | **bỏ** trừ khi dư giờ; history-list đơn giản | `dialogue.txt` | 09 |
| **LLM/RAG** ✨ | *(Lựa chọn 2, không bắt buộc)* | **bỏ**; faq.txt là corpus nếu làm | `retrieval.txt` | 09 |
| **README+Docker** 🔧 | bắt buộc | mô tả đúng 11 mục §7.5 | — | — |

**Intent nên phủ**: 7 cái spec nêu (`GET_COURSE_INFO, GET_TOPIC, GET_SCHEDULE,
GET_ASSIGNMENT, GET_DEADLINE, GET_RESOURCE, GET_RULE`) **+ `GET_LO`** (KB có LO, dễ
ăn thêm điểm). **Bỏ `GET_INSTRUCTOR`** trong entities.txt — KB **không có** dữ liệu
giảng viên → hỏi cũng chỉ ra not-found, thêm nhánh vô ích.

## 2. Luồng + module (src/)
```
input/sentences.txt
      │
      ▼
   parser.py ──► parse-results.txt        grammar.py  ◄── data/grammar.txt (1 nguồn)
      │  cây / ()                             ▲
      ▼                                       │
  semantic.py ──► semantic.txt, intent-entity.txt   generator.py ──► samples.txt
      │  predicate = intent(entity)
      ▼
   query.py ──► query.txt ──► kb.py (6 loader, index) ──► data/kb/*.txt
      │
      ▼
  answer.py ──► answer.txt   (có data → template | rỗng → not-found)

  evaluate.py ──► evaluation.txt   (chạy scaffolding/sample_queries.txt)
  main.py       wire tất cả; CLI đọc input/ → ghi output/
```
- `grammar.py` = 1 nguồn `data/grammar.txt`, **parser & generator cùng đọc** (viết
  văn phạm 1 lần, dùng 2 chiều). Copy ra `output/grammar.txt` để nộp.
- `semantic.py` gộp luôn intent/entity (cùng 1 lần duyệt cây) — đừng tách 2 module.

## 3. Layout thư mục nộp (§7.4 — bắt buộc y khuôn)
```
project/
  src/        grammar.py parser.py generator.py semantic.py kb.py query.py
              answer.py evaluate.py main.py
  data/       grammar.txt + kb/ + scaffolding/   ← đã có kb/ & scaffolding/
  models/     (trống/ config nếu cần — classical hầu như không cần)
  input/      sentences.txt (mẫu)                ← CHƯA có, phải tạo
  output/     *.txt kết quả chạy                 ← CHƯA có, sinh khi chạy
  README.md   Dockerfile                          ← CHƯA có
```
Repo hiện có `data/`, `docs/`, `materials/`. **Còn thiếu: `src/`, `input/`,
`output/`, `models/`, README, Dockerfile.** (`docs/`, `materials/` là của bạn, gỡ
khỏi zip nộp cho gọn <10MB.)

## 4. Điểm thiết kế "ngon" (mỗi cái 1 lý do)
1. **Semantic grammar — nhét intent vào tên nút Q** → intent+entity **rơi ra từ cây**,
   khỏi viết bộ phân loại riêng (doc 05). Đây là đòn bẩy lớn nhất.
2. **1 grammar, 2 chiều** (parser đọc + generator đọc) → không đồng bộ 2 bản.
3. **KB loader index theo entity** → query chỉ là tra dict O(1), không quét file lúc
   chạy (doc kb-loader).
4. **Not-found gộp 1 chỗ**: cả `()` (parser) lẫn rỗng (query) đổ về **1 message** →
   thẳng với §4.1(5), khỏi rải if khắp nơi.
5. **Keyword/luật thuần cho intent**, không ML: spec cho phép, mà cây đã nhả intent
   sẵn → thêm ML là tự làm khổ (doc 05).

`ponytail:` parser recursive-descent + backtracking có thể **bùng nổ mũ** với văn
phạm nhập nhằng nặng; miền này nhỏ nên OK — nếu chậm/nhập nhằng thì nâng **chart
parser** (Chương 3) sau, đừng làm sớm.

## 5. KHÔNG làm (YAGNI — tiết kiệm để dồn vào grammar)
- Phần III dialogue, LLM/RAG (đều ✨ optional) — chỉ đụng khi core + eval xong chắc.
- Dialogue Manager phức tạp, agent, tool-calling, fine-tune (§4.2 nói rõ không cần).
- ML/DL cho intent (keyword đủ). Chart parser (recursive-descent đủ cho miền nhỏ).
- `GET_INSTRUCTOR` (không có data).

## 6. Thứ tự build (theo todo.md)
```
kb.py (loader) 🔧  →  data/grammar.txt 🔥  →  parser.py ⚙️  →  generator.py ⚙️
  →  semantic.py 🔀  →  query.py + answer.py 🔧  →  evaluate.py 🔧
  →  README + Dockerfile 🔧   →  (✨ dialogue / RAG nếu dư giờ)
```
Đổ **~70% công vào grammar + semantic** (doc 00 §7): accuracy Phần IV sống/chết theo
độ phủ grammar, không theo số module.
