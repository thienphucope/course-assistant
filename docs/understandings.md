# Course Assistant (CO3085) — Phân tích spec & Kế hoạch làm chi tiết

> Tóm tắt: Xây một **Trợ lý hỗ trợ học tập** cho **một môn học**. Người dùng hỏi
> bằng ngôn ngữ tự nhiên, hệ thống phân tích câu → hiểu ý định → tra cứu
> knowledge base (KB) → trả lời. Nhóm 3–4 SV, viết bằng **Java hoặc Python**,
> chấm bằng **Docker**.

---

## 1. Bức tranh tổng thể

Sản phẩm cuối là **một pipeline NLP hoàn chỉnh** trong miền hẹp (thông tin 1 môn học):

```
Câu hỏi tự nhiên
  → Grammar / Parser        (Phần I  — bắt buộc)
  → Cây cú pháp
  → Diễn giải ngữ nghĩa      (Phần II — bắt buộc, chọn 1 trong 2 hướng)
  → Intent / Entity
  → Truy vấn Knowledge Base
  → Câu trả lời
```

Mở rộng (không thay thế phần cốt lõi):
```
Knowledge Base → Retrieval → LLM → Câu trả lời có căn cứ (grounded)
```

**Điểm mấu chốt của môn này:** phần NLP cổ điển (grammar, parser, semantic,
intent/entity) là **cốt lõi và bắt buộc**. LLM/RAG chỉ là *mở rộng*, **không được
dùng LLM thay thế toàn bộ quá trình NLP**.

Miền dữ liệu bị **giới hạn trong thông tin của môn học được cung cấp** — hệ thống
không cần trả lời câu hỏi tổng quát ngoài miền, và khi không có dữ liệu thì phải
báo "không tìm thấy" chứ **không được bịa** (chống hallucination).

---

## 2. Ba quyết định phải chốt trước khi code

| Quyết định | Gợi ý | Lý do |
|---|---|---|
| **Ngôn ngữ lập trình** | **Python** | Có NLTK (CFG + parser sẵn), dễ làm RAG nếu muốn mở rộng. Java cũng được nhưng tốn công hơn. |
| **Ngôn ngữ câu hỏi** | **Tiếng Việt** | Tất cả ví dụ trong đề đều tiếng Việt. Tiếng Việt tách từ theo khoảng trắng-âm tiết → coi các cụm cố định ("bài tập lớn", "tín chỉ") như token ghép. |
| **Hướng Phần II** | **Lựa chọn 1 (Classical/Statistical)**, LLM/RAG làm bonus nếu dư thời gian | Lựa chọn 1 đúng trọng tâm môn, chắc điểm, không phụ thuộc API. Đề cho phép chọn 1 trong 2; cả hai đều phải dùng lại kết quả Phần I. |

> Ghi chú: Đề nói Phần II "chọn **một** trong hai hướng". Làm tốt Lựa chọn 1 là đủ
> điểm. Nếu làm thêm Lựa chọn 2 thì tính là điểm cộng, không bỏ Lựa chọn 1.

---

## 3. Yêu cầu từng phần & file output bắt buộc

### Phần I — Văn phạm & Parser *(bắt buộc)*

| Mục | Việc phải làm | Output |
|---|---|---|
| 3.1 | Viết **văn phạm (CFG)** cho miền Course Assistant. Tối thiểu phủ các nhóm: hỏi thông tin chung, nội dung/chủ đề, lịch học, bài tập, thời hạn, tài liệu, quy định. | `output/grammar.txt` |
| 3.2 | Viết **giải thuật sinh câu** từ văn phạm. Mỗi dòng 1 câu, câu phải hợp lệ theo grammar, **tối đa 10.000 câu**. | `output/samples.txt` |
| 3.3 | Viết **parser** dùng chính văn phạm đó. Đọc `input/sentences.txt` (mỗi dòng 1 câu), xuất cây cú pháp cho câu hợp lệ; câu không hợp lệ/ngoài văn phạm xuất `()`. | `output/parse-results.txt` |

### Phần II — Ngữ nghĩa & Course Assistant *(bắt buộc, chọn 1)*

**Lựa chọn 1 — Classical/Statistical NLP** (khuyến nghị). Chuỗi xử lý:
```
Input → Parsing → Semantic Representation → Intent/Entity → Query → KB → Answer
```
Các loại truy vấn tối thiểu: `GET_COURSE_INFO`, `GET_TOPIC`, `GET_SCHEDULE`,
`GET_ASSIGNMENT`, `GET_DEADLINE`, `GET_RESOURCE`, `GET_RULE`.

| Bước | Việc | Output |
|---|---|---|
| 1 | **Biểu diễn ngữ nghĩa**: cây cú pháp → predicate. VD `"Môn NLP có bao nhiêu tín chỉ?"` → `GET_CREDIT(course=NLP)`; `"Deadline bài tập lớn là khi nào?"` → `GET_DEADLINE(assignment=PROJECT)`. | `output/semantic.txt` |
| 2 | **Nhận diện intent + entity**: xác định loại yêu cầu và tham số. Được dùng: luật / keyword matching / thống kê / ML. **Không cần Deep Learning hay LLM.** | `output/intent-entity.txt` |
| 3 | **Xây truy vấn KB** từ semantic representation. | `output/query.txt` |
| 4 | **Truy xuất + sinh câu trả lời**. | `output/answer.txt` |
| 5 | **Xử lý không tìm thấy**: báo lịch sự, không bịa. VD `"Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học."` | (thể hiện trong `answer.txt`) |

**Lựa chọn 2 — LLM/RAG** (mở rộng, optional):
```
User Question → Retrieve → Retrieved Context → LLM → Answer
```
Bước: (1) cơ chế truy xuất, (2) xây prompt/context, (3) sinh câu trả lời,
(4) nếu được thì kèm nguồn, (5) xử lý không tìm thấy. Output: `output/retrieval.txt`,
`output/answer.txt` — phải thể hiện: câu hỏi, tài liệu truy xuất, câu trả lời.

### Phần III* — Ngữ cảnh hội thoại cục bộ *(optional, có sao)*

Xử lý tham chiếu qua các lượt, VD "Tài liệu của **phần này** ở đâu?" phải hiểu
"phần này" = nội dung vừa nói (CFG & Parsing tuần 5). **Không cần** Dialogue
Manager phức tạp — chỉ vài trường hợp tham chiếu định trước.
Output: `output/dialogue.txt` (hội thoại vào, ngữ cảnh dùng, kết quả diễn giải, câu trả lời).

### Phần IV — Đánh giá *(bắt buộc)*

Xây tập test phủ: câu hợp lệ, nhiều cách diễn đạt cùng 1 ý, câu ngoài phạm vi,
câu KB không có, (câu dùng ngữ cảnh nếu làm Phần III). Báo cáo tối thiểu: số câu
test, số câu đúng, độ chính xác, vài ca sai + phân tích nguyên nhân, ưu/nhược
điểm. Nếu làm LLM/RAG: thêm ví dụ trả lời có căn cứ, câu KB không có, và ca
nguy cơ **hallucination**. Output: `output/evaluation.txt`.

---

## 4. Kiến trúc đề xuất (Python + Lựa chọn 1)

```
project/
├── src/
│   ├── grammar.py        # load/định nghĩa CFG
│   ├── generate.py       # sinh câu (3.2)
│   ├── parser.py         # parser (3.3)
│   ├── semantic.py       # cây → predicate
│   ├── intent.py         # intent + entity
│   ├── kb.py             # load KB + query
│   ├── answer.py         # sinh câu trả lời (template)
│   ├── dialogue.py       # ngữ cảnh (Phần III, optional)
│   ├── evaluate.py       # chấy tập test (Phần IV)
│   └── main.py           # nối pipeline, ghi các file output/
├── data/                 # grammar nguồn + KB
├── models/               # config/model nếu có
├── input/                # sentences.txt mẫu
├── output/               # tất cả file kết quả
├── README.md
└── Dockerfile
```

**Công cụ gợi ý (Python):**
- Grammar + Parser: `nltk` — `nltk.CFG.fromstring(...)` + `nltk.ChartParser`.
  Sinh câu: `nltk.parse.generate.generate(grammar, n=...)`.
- KB: file `.txt`/`.json` đơn giản, đọc bằng stdlib. Không cần DB.
- Intent/Entity Lựa chọn 1: **rule + keyword matching là đủ** — mỗi intent một
  bộ từ khoá + regex bắt entity (số tuần, tên môn, "bài tập lớn"...).
- (Bonus RAG): `sentence-transformers` + FAISS/`numpy` cosine để retrieve, rồi
  gọi LLM. Chỉ làm sau khi Lựa chọn 1 xong.

Ánh xạ cây → semantic: gán **nhãn ngữ nghĩa** cho các luật CFG (mỗi luật gắn 1
mảnh predicate), hoặc duyệt cây sau khi parse để rút intent + entity. Cách đơn
giản nhất cho miền hẹp: parse xác định cấu trúc + intent, rồi regex/luật rút
entity từ chính câu.

---

## 5. Các bước làm — theo thứ tự

1. **Lấy KB** do giảng viên cung cấp. Đọc kỹ, liệt kê các trường thông tin có
   thật (số tín chỉ, lịch tuần, danh sách bài tập, deadline, tài liệu, quy định).
   → Đây là "nguồn chân lý", grammar và intent phải bám theo nó.
2. **Chốt danh sách intent** (bám 7 loại `GET_*` + vài loại riêng của môn).
3. **Viết CFG** (3.1) phủ đủ intent, gồm nhiều cách hỏi cho mỗi intent → `grammar.txt`.
4. **Sinh câu** (3.2) để tự kiểm tra độ phủ của grammar → `samples.txt` (≤10k).
5. **Viết parser** (3.3): đọc `input/sentences.txt`, xuất cây hoặc `()` → `parse-results.txt`.
   Test bằng chính vài dòng lấy từ `samples.txt` + vài câu sai để chắc ra `()`.
6. **Semantic** (II.1): cây → predicate `GET_*(...)` → `semantic.txt`.
7. **Intent/Entity** (II.2): rule + keyword → `intent-entity.txt`.
8. **Query + KB** (II.3): predicate → truy vấn KB → `query.txt`.
9. **Answer** (II.4–5): tra KB, sinh câu trả lời bằng template; xử lý không tìm
   thấy → `answer.txt`.
10. **(Optional) Phần III**: xử lý 2–3 mẫu tham chiếu ngữ cảnh → `dialogue.txt`.
11. **Phần IV**: xây tập test đủ loại, chạy, tính accuracy, phân tích lỗi → `evaluation.txt`.
12. **Đóng gói**: README, Dockerfile, `input/`, `output/` mẫu, quay video demo.

**Gợi ý phân công 3–4 người:**
- A: Grammar + Generate + Parser (Phần I).
- B: Semantic + Intent/Entity (II.1–2).
- C: KB + Query + Answer (II.3–5) + Phần III.
- D: Đánh giá (Phần IV) + README + Dockerfile + video demo (+ RAG nếu làm).

---

## 6. Nộp bài & tiêu chí kiểm

**Tên file nộp:** `MSSV1-MSSV2-MSSV3-MSSV4.zip`, gồm:
`src/ data/ models/ input/ output/ README.md Dockerfile`. Nén **< 10MB**;
file/model lớn thì upload chỗ khác và để link trong README.

**README** phải mô tả: thành viên; cài đặt; cách chạy; kiến trúc; grammar;
parser; semantic representation; intent/entity; KB & cách truy vấn; hướng đã
chọn (Classical hay LLM/RAG); cách đánh giá; hạn chế.

**Báo cáo + Demo:** nộp source, README, output, báo cáo, **video demo ngắn**.
Video phải thể hiện: (1) nhận câu hỏi, (2) quá trình xử lý chính, (3) kết quả
phân tích/semantic, (4) câu trả lời, (5) **một ca không trả lời được**. Nhóm
RAG: demo thêm phần truy xuất + context. Trình bày dự kiến tuần 13–14, 5–10 phút.

**Checklist file `output/`:**
- [ ] `grammar.txt`  - [ ] `samples.txt`  - [ ] `parse-results.txt`
- [ ] `semantic.txt`  - [ ] `intent-entity.txt`  - [ ] `query.txt`  - [ ] `answer.txt`
- [ ] `dialogue.txt` *(nếu làm Phần III)*  - [ ] `evaluation.txt`
- [ ] *(nếu chọn LLM/RAG)* `retrieval.txt`

---

## 7. Lằn ranh cần nhớ (tránh mất điểm / vi phạm liêm chính)

- **Không** dùng LLM/API thay thế toàn bộ NLP cốt lõi ở Lựa chọn 1.
- **Không** bịa thông tin ngoài KB — hết dữ liệu thì báo "không tìm thấy".
- Bổ sung dữ liệu test được, nhưng **ghi rõ nguồn**, không đổi bản chất bài toán.
- Mọi tham khảo (kể cả AI hỗ trợ) phải **hiểu và giải thích lại được**; ghi nguồn
  cho code/tài liệu bên ngoài. Không sao chép/chia sẻ bài giữa các nhóm.

---

## 8. Nguyên lý hoạt động: heuristic + đệ quy + brute force

Hệ này **không học gì cả** — không tham số, không xác suất (trừ khi tự thêm ML cho
intent). Toàn bộ "trí thông minh" nằm trong **luật con người viết**. Máy chỉ làm 3 việc:

- **heuristic (khớp mẫu)**: cắt cụm từ cố định khi tokenize, khớp từ khoá/luật để đoán intent.
- **đệ quy**: hàm parse gọi lại chính nó để dựng cây con — và luật CFG có thể tự
  tham chiếu (`LIST → COURSE "và" LIST`) cho câu dài tuỳ ý từ luật hữu hạn.
- **brute force**: parser **thử lần lượt mọi luật**, gặp nhánh tắc thì **backtrack**
  (quay lui, nhả token, thử luật khác). Xấu nhất là hàm mũ; chart parser/CYK là
  bản "brute force có nhớ" (quy hoạch động) đưa về ~O(n³).

Bản đồ "từ gì ra gì":

| Chặng | Vào → Ra | Nguyên lý |
|---|---|---|
| 1. Token hoá | chuỗi → list token | heuristic cắt từ + từ điển cụm |
| 2. Parse | token → cây cú pháp | **đệ quy** dò luật + **brute force** thử/backtrack |
| 3. Semantic | cây → `GET_CREDIT(course=NLP)` | luật ánh xạ theo cấu trúc cây (compositional) |
| 4. Intent/Entity | predicate → intent + tham số | heuristic keyword/regex |
| 5. Query→Answer | intent → tra KB → câu | tra bảng + điền template; hết dữ liệu thì báo lỗi |

Khác LLM: LLM đoán câu tiếp theo bằng xác suất từ hàng tỉ tham số → mạnh hơn nhưng
**giải thích không được và bịa được**. Bản cổ điển *không có khả năng* tạo thông tin
ngoài KB nên **không hallucinate**, và giải thích được từng bước ra câu trả lời.

## 9. Ví dụ nhỏ về thuật toán (chạy được: `src/example_parser.py`)

CFG thu nhỏ (cố ý xếp `SCHEDULE_Q` **trước** `CREDIT_Q` để lộ một lần backtrack):

```
S          → SCHEDULE_Q | CREDIT_Q
CREDIT_Q   → "môn" COURSE "có" "bao_nhiêu" "tín_chỉ"
SCHEDULE_Q → "tuần" NUM "học" "gì"
COURSE     → "nlp" | "ai" | "hđh"
NUM        → "5" | "6" | "7"
```

Cốt lõi parser (đệ quy + thử-từng-luật + backtrack):

```python
def parse_symbol(sym, tokens, pos, depth, trace):
    if sym not in GRAMMAR:                        # terminal: khớp trực tiếp 1 token
        if pos < len(tokens) and tokens[pos] == sym:
            return (sym, pos + 1)
        return None                               # không khớp -> nhánh tắc
    for i, rule in enumerate(GRAMMAR[sym]):       # BRUTE FORCE: thử từng luật của sym
        children, p = [], pos
        for s in rule:
            r = parse_symbol(s, tokens, p, depth+1, trace)   # ĐỆ QUY xuống thành phần
            if r is None:
                children = None; break            # tắc -> bỏ luật này
            children.append(r[0]); p = r[1]
        if children is not None:
            return ((sym, children), p)           # khớp cả luật -> trả cây con
        # rơi xuống đây = BACKTRACK, thử luật kế tiếp
    return None
```

Chạy với `"Môn NLP có bao nhiêu tín chỉ?"`, trace thực tế in ra:

```
thu S luat #0: ['SCHEDULE_Q']
  thu SCHEDULE_Q luat #0: ['tuần', 'NUM', 'học', 'gì']
    x can 'tuần' @0, thay ['môn']            <- nhánh tắc ngay từ đầu
  <= backtrack khoi SCHEDULE_Q luat #0
<= backtrack khoi S luat #0                   <- QUAY LUI, đổi luật
thu S luat #1: ['CREDIT_Q']
  thu CREDIT_Q luat #0: ['môn', 'COURSE', 'có', 'bao_nhiêu', 'tín_chỉ']
    . khop terminal 'môn' @0
    thu COURSE luat #0: ['nlp']
      . khop terminal 'nlp' @1
    => COURSE khop bang luat #0                <- đệ quy dựng cây con COURSE
    . khop terminal 'có' @2 ... 'bao_nhiêu' @3 ... 'tín_chỉ' @4
  => CREDIT_Q khop bang luat #0
=> S khop bang luat #1                         <- khớp hết token -> hợp lệ
```

Cây cú pháp → ngữ nghĩa → tra KB → câu trả lời:

```
        S                     to_semantic(cây)      tra data/course_info.txt
        └ CREDIT_Q     ─────► GET_CREDIT(course=NLP) ─────► credits: 3
            môn                                                   │
            COURSE(nlp)                                           ▼
            có bao_nhiêu tín_chỉ                        "Môn NLP có 3 tín chỉ."
```

Câu ngoài văn phạm, ví dụ `"Hôm nay trời đẹp"`: mọi luật của `S` đều tắc → `parse`
trả `None` → xuất `()` (đúng yêu cầu 3.3). Đây cũng là chỗ chống bịa: không dựng
được thì không trả lời liều.

> File `src/example_parser.py` có sẵn `__main__` tự kiểm bằng `assert`
> (câu hợp lệ ra đúng predicate, câu ngoài văn phạm ra `()`). Đây là *đồ chơi* để
> hiểu cơ chế — grammar/parser thật của nhóm sẽ phủ nhiều intent và cách diễn đạt hơn.
