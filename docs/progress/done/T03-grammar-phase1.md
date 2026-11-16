# T03 · 🔥 Phase 1 — Mở rộng và gộp `grammar.cfg`

- **Trạng thái:** xong
- **Phụ trách:** Bảo (#1), Bách (#2), Khoa (#3) · review + gộp: Phúc
- **Mốc:** review 26/09/2026 · hạn cũ 02/10 · gộp 22/10/2026
- **Output:** `src/data/grammar.cfg`
- **Ngày xong / Commit:** 22/10/2026 · commit chứa file này

PR #1, #2, #3 **không merge trực tiếp** (đôi một conflict ở `grammar.cfg`; #3 crash; #2 kèm 71
file ngoài phạm vi). Thay vào đó lấy **grammar của nhánh `sample` (đóng băng) làm nền**, rồi chọn
lọc từng cách hỏi của 3 người mà sample chưa có: nhận nếu không làm hỏng gì, loại nếu không sửa
được. 3 PR kết thúc bằng merge tay: `T04-phase1-prs.md`.

---

## 1. Kết quả

Đo bằng code của nhánh `sample` (tokenizer, loader, Earley parser, semantic, KB, generator) trên
bộ test hiện tại trong `src/data/scaffolding/`: 42 câu mẫu (Q001–Q034, S001–S008), 8 câu thách
thức (C001–C008), 6 hội thoại.

| Bản | Load | Câu mẫu /42 | Thách thức /8 | Hội thoại /6 | Sinh câu → parse lại | Câu mơ hồ |
| --- | --- | --- | --- | --- | --- | --- |
| main trước gộp (seed) | OK | 20 | 0 | 3 | sạch | — |
| #1 Bảo | OK | 21 | 0 | 3 | sạch | — |
| #2 Bách | OK, **30 nhánh** | 34 | 0 | 4 | 232 câu lỗi | — |
| #3 Khoa | **crash** | — | — | — | — | — |
| sample (nền) | OK | 42 | 6 | 6 | sạch | 0 |
| **main sau gộp** | OK, 26 nhánh | **42** | **6** | **6** | sạch | **0** |

- Bộ test không đổi nên điểm main sau gộp bằng sample; cái tăng là **số cách hỏi được chấp nhận**.
  Mỗi cách hỏi được nhận đều phải: parse vào đúng nhánh, resolve được entity, KB trả lời được.
- Chạy cả pipeline trên 6000 câu sinh ra: không có câu UNKNOWN hay entity rỗng; chỉ còn các ca
  NOT_FOUND **cố ý** giống hệt sample (`tuần 99`, `lo9.9`, `chương 13`, giảng viên không có trong KB).
- 2 câu thách thức còn rớt (C007 `học mấy buổi mỗi tuần`, C008 `tuần thứ ba tụi mình học bài gì
  vậy`) là câu sample cố ý để ngoài grammar.

### Cách kiểm tra (để làm lại được)

1. Load grammar bằng `Grammar.from_file` của sample → bắt non-terminal chưa định nghĩa.
2. Đếm nhánh của `QUESTION` (phải là 26), non-terminal định nghĩa 2 lần, terminal viết hoa.
3. Chạy `evaluate_cases` trên `sample_queries.txt`, `challenge_queries.txt` và hội thoại trong
   `dialogues.txt`.
4. Sinh 3000–6000 câu → parse lại; đếm số cây parse của mỗi câu (> 1 = mơ hồ).
5. Chạy `CourseAssistant.process` trên câu sinh: intent ≠ UNKNOWN; entity có ID trừ frame
   context; query tìm thấy hoặc fallback có nguyên nhân do thiếu KB/ngữ cảnh.
6. Đo đóng góp: thay mọi danh sách entity bằng 1 giá trị cố định, sinh "khung câu" của từng nhánh
   từ grammar của người đóng góp, xem grammar nền có parse được vào đúng nhánh không.

Công cụ hiện đã có ở `tools/check_grammar.py`; điều kiện nghiệm thu hiện tại (bao gồm
fallback hợp lệ) ghi tại T19 và mục thiết kế bên dưới.

---

## 2. Phân công

| Người | Nhánh được giao |
| --- | --- |
| **Bảo** | `Q_COURSE_CREDITS` `Q_COURSE_PARTS` `Q_COURSE_DESCRIPTION` `Q_COURSE_EXAM_DURATION` `Q_COURSE_EXAM_TIME` `Q_COURSE_ASSESSMENT` `Q_INSTRUCTOR` `Q_SCHEDULE_WEEK` `Q_SCHEDULE_CHAPTER` |
| **Bách** | `Q_SCHEDULE_TOPICS` `Q_TOPIC_BY_NAME` `Q_TOPIC_BY_CHAPTER` `Q_TOPIC_RELATION` `Q_LO` `Q_ASSIGNMENT_OVERVIEW` `Q_ASSIGNMENT_PART` `Q_ASSIGNMENT_FEATURE` |
| **Khoa** | `Q_ASSIGNMENT_OUTPUT` `Q_DEADLINE` `Q_RESOURCE` `Q_RULE` `Q_CONTEXT_TOPIC_RELATION` `Q_CONTEXT_NEXT_CHAPTER` `Q_CONTEXT_ASSIGNMENT_OUTPUT` `Q_CONTEXT_RESOURCE` `Q_CONTEXT_LO_CHAPTER` |

Lưu ý đã giao: dùng lại các biến `*_ENTITY` đã khai báo; PR từng phần sớm để check; giữ nguyên
danh sách 26 nhánh của `QUESTION`.

---

## 3. Từng người: nhận xét → nhận gì, bỏ gì

Các bảng nhận xét là số liệu **review 26/09** (bộ test cũ Q001–Q034 + C001–C008). "Khung câu" =
số mẫu câu khác nhau của nhánh khi gộp danh sách thực thể thành 1 ô: main → PR (sample).
"Độ phủ" = số câu sinh từ grammar sample mà PR chấp nhận đúng nhánh.

### 3.1 Bảo — PR #1

**Nhận xét.** 3 commit (12–13/09), chỉ sửa `grammar.cfg` (+14/−13 dòng), mọi non-terminal bị sửa
đều thuộc 9 nhánh của Bảo. Mở rộng `COURSE_ENTITY` và `EXAM_ENTITY` thay vì tạo biến mới. PR sạch
nhất nhóm, không mơ hồ.

| Nhánh | Khung câu | Câu mẫu | Độ phủ |
| --- | --- | --- | --- |
| `Q_COURSE_CREDITS` | 1 → **8** (7) | Q001 ✗ · Q002 ✓ · C004 ✗ | 6/25 |
| `Q_COURSE_PARTS` | 1 → **4** (9) | Q003 ✗ | 3/27 |
| `Q_COURSE_DESCRIPTION` | 1 → **4** (6) | C003 ✗ | 3/24 |
| `Q_COURSE_EXAM_DURATION` | 1 → **4** (3) | Q016 ✓ · Q017 ✓ | 4/12 |
| `Q_COURSE_EXAM_TIME` | 1 → **5** (3) | C005 ✗ | 8/12 |
| `Q_COURSE_ASSESSMENT` | 1 → **4** (3) | — | 1/9 |
| `Q_INSTRUCTOR` | 1 → **6** (6) | C006 ✗ | 6/24 |
| `Q_SCHEDULE_WEEK` | 1 → **4** (12) | Q004 ✓ · C001 ✗ | 30/153 |
| `Q_SCHEDULE_CHAPTER` | 1 → **4** (3) | Q005 ✓ | 12/69 |

Số cách hỏi ngang hoặc hơn sample ở 6/9 nhánh. Điểm yếu: chữ "môn" chèn lẻ vào từng alternative
(`"môn" COURSE_ENTITY "mấy" "tín" "chỉ"`…) thay vì bọc chung → rớt Q001 `Môn NLP có bao nhiêu tín
chỉ?` và Q003 `Môn học gồm những phần nào?`.

**Nhận — toàn bộ 31/31 khung câu**, viết lại theo cấu trúc sample (đặt vào `*_QUESTION` có sẵn,
dùng `COURSE_SUBJECT` nên tự có dạng "môn X"):

- Tín chỉ: bỏ chữ "có" bắt buộc (`CREDIT_VERB` = rỗng | có | được) → `NLP mấy tín chỉ`,
  `NLP được mấy tín chỉ`; `NLP bao nhiêu tín`; `Số tín chỉ của NLP là bao nhiêu`.
- Các phần: `có mấy phần`, `chia thành mấy phần`, `Các phần học của NLP`.
- Mô tả: `giới thiệu nội dung gì`, `nghiên cứu vấn đề gì`, `Tổng quan về NLP`.
- Thời lượng thi: `thi trong bao lâu`, `Thời gian làm bài midterm`, `Thời lượng thi midterm là bao nhiêu`.
- Lịch thi: `thi vào tuần mấy`, `Lịch thi midterm là ngày nào`, `Ngày thi midterm là khi nào`.
- Cách tính điểm: `Thang điểm của NLP`, `Trọng số điểm NLP như thế nào`, `Cách đánh giá NLP`.
- Giảng viên: `Ai phụ trách NLP`, `Thầy cô nào phụ trách NLP`, `Giảng viên NLP` (không cần "là
  ai"); `cho biết …`, `cho mình xem …` đưa lên `PLEASE_PREFIX` → dùng được cho mọi nhánh.
- Lịch tuần: `Nội dung của tuần 3`, `Tuần 3 giảng chủ đề gì`.
- Lịch chương: `Tuần nào học chương 3`, `Chương 3 được dạy tuần nào`, `Chương 3 ở tuần mấy`.

**Bỏ:** cách chèn "môn" lẻ trong từng alternative (thay bằng `COURSE_SUBJECT`). Entity
"xử lý ngôn ngữ tự nhiên", "giữa kỳ", "cuối kỳ" sample đã có.

### 3.2 Bách — PR #2

**Nhận xét.** 2 commit (23/09), **71 file, +15 259/−391 dòng**: tự hiện thực toàn bộ pipeline
(loader, tokenizer, parser, semantic, KB, query, answer, evaluate, CLI), 12 file docs, 9 file test,
`src/output/samples.txt` 10 001 dòng, `package_submission.py`. Copy `data/kb/*` vào `src/data/kb/`
đúng lưu ý. 50 test của PR đều pass.

| Nhánh | Khung câu | Câu mẫu | Độ phủ |
| --- | --- | --- | --- |
| `Q_SCHEDULE_TOPICS` | 1 → **1** (6) | — | 0/153 |
| `Q_TOPIC_BY_NAME` | 1 → **2** (7) | Q006 ✓ Q008 ✓ Q021 ✓ Q022 ✓ Q023 ✓ · Q007 qua nhánh mới | 17/152 |
| `Q_TOPIC_BY_CHAPTER` | 1 → **1** (5) | Q020 ✓ Q029 ✓ · Q024 qua nhánh mới | 12/115 |
| `Q_TOPIC_RELATION` | 2 → **2** (5) | Q025 ✓ Q031 ✓ | 42/152 |
| `Q_LO` | 1 → **1** (4) | Q009 ✓ · Q010 qua nhánh mới | 16/68 |
| `Q_ASSIGNMENT_OVERVIEW` | 1 → **2** (6) | Q011 ✓ | 6/21 |
| `Q_ASSIGNMENT_PART` | 1 → **1** (3) | Q012 ✓ | 12/48 |
| `Q_ASSIGNMENT_FEATURE` | 1 → **1** (1) | Q013 ✓ Q033 ✓ | 15/20 |

- Đóng góp thật: mở rộng danh sách thực thể — `TOPIC_ENTITY` 4 → 23, `LO_ENTITY` 6 → 16.
- Cách hỏi mới chỉ 2 khung (`chương nào học về X`, `bài tập lớn yêu cầu xây dựng những gì`);
  6/8 nhánh không có cách hỏi mới.
- Thêm 4 nhánh ngoài danh sách chốt, mỗi nhánh đúng 1 câu: `Q_TOPIC_LOCATION`,
  `Q_TOPIC_METHODS`, `Q_LO_CONTENT`, `Q_RULE_PERMISSION` → `QUESTION` thành 30 nhánh.
- Lấn phần Bảo (`COURSE_ENTITY`, `CREDIT_QUESTION`, `Q_COURSE_PARTS`, `Q_SCHEDULE_CHAPTER`) và
  Khoa (`Q_RESOURCE`, `RULE_TOPIC`, `Q_RULE_PERMISSION`).
- `TOPIC_ENTITY` viết `"context" "-" "free"`: chạy được với tokenizer của Bách (tách `-`), nhưng
  tokenizer sample giữ `context-free` là 1 token → 232 câu sinh ra không parse lại được.

**Nhận** (phần sample chưa có):

- `môn học` làm chủ ngữ chung trong `COURSE_SUBJECT` → `Môn học có bao nhiêu tín chỉ`, … (thay
  alternative riêng `"môn" "học" PARTS_QUESTION` của sample).
- `Chương 3 học vào những tuần nào`.
- `CFG và parsing nằm ở tuần nào` — không bắt buộc chữ "phần" (`TOPIC_GROUP`).
- `Tài liệu tham khảo nói về / liên quan đến / về X [là gì]`, `Tài liệu nào về X`.

**Đã có trong sample (không cần thêm):** 23 topic, 16 LO, `btl01`, `natural language processing`,
`chương nào học về`, `X được học ở đâu`, `có những phương pháp gì`, `liên quan đến nội dung nào`,
`yêu cầu xây dựng những gì`, `có được dùng X không`. Các câu đi qua 4 nhánh thừa đều pass dưới
nhánh có sẵn → chứng tỏ không cần nhánh mới.

**Bỏ:**

- `"môn" "nlp"` trong `COURSE_ENTITY` — mơ hồ với `COURSE_SUBJECT -> "môn" COURSE_ENTITY`.
- 4 nhánh mới — giữ 26 nhánh.
- `"context" "-" "free"` — sample đã viết đúng `"context-free"`.
- `Tài liệu nào nói về X là gì` — đuôi "là gì" thừa sau "nào".
- Phần pipeline (71 file) — ngoài phạm vi grammar, xem `done/T05-codebase-decision.md` (quyết định: không dùng làm nền).

### 3.3 Khoa — PR #3

**Nhận xét.** 1 commit (25/09), chỉ sửa `grammar.cfg` (+113/−24). Nhiều cách hỏi nhất nhóm, có ý
hay (gom `FEAT_PARSING`/`FEAT_SEMANTIC`/… để semantic map sang phần BTL).

| Nhánh | Khung câu | Câu mẫu | Độ phủ |
| --- | --- | --- | --- |
| `Q_ASSIGNMENT_OUTPUT` | 1 → **592** (3) | — | 4/12 |
| `Q_DEADLINE` | 1 → **104** (12) | C002 ✗ | 18/48 |
| `Q_RESOURCE` | 1 → **95** (4) | Q018 ✗ · Q019 ✓ | 10/44 |
| `Q_RULE` | 1 → **75** (10) | Q014 ✗ · Q015 ✓ | 11/145 |
| `Q_CONTEXT_TOPIC_RELATION` | 8 → **60** (20) | Q030 ✓ | 8/152 |
| `Q_CONTEXT_NEXT_CHAPTER` | 1 → **ĐÃ XOÁ** (2) | Q032 ✗ (hồi quy) | 0/2 |
| `Q_CONTEXT_ASSIGNMENT_OUTPUT` | 1 → **2960** (3) | Q034 ✓ | 1/3 |
| `Q_CONTEXT_RESOURCE` | 4 → **200** (9) | D01 ✓ | 3/9 |
| `Q_CONTEXT_LO_CHAPTER` | 1 → **10** (1) | D05 lượt 2 ✓ | 1/1 |

5 lỗi chặn merge:

1. `Q_DEADLINE` gọi `TARGET_HAS_OUTPUT` — không được định nghĩa → loader crash.
2. Xoá `Q_CONTEXT_NEXT_CHAPTER` nhưng `QUESTION` vẫn gọi → `Còn chương sau?` (Q032) hỏng; bản thay
   thế `Q_CONTEXT_CONTINUATION` không được nối vào.
3. 4 nhánh mới không nối vào `QUESTION` (code chết): `Q_CONTEXT_CONTINUATION`,
   `Q_CONTEXT_ASSIGNMENT_DEADLINE`, `Q_CONTEXT_SCHEDULE`, `Q_CONTEXT_EXAM_ASSESSMENT`.
4. `PART_NUM_ROMAN_UPPER -> "I" | "II" …`: tokenizer đã lowercase → không bao giờ khớp; loader còn
   hiểu nhầm là non-terminal.
5. Định nghĩa lại `YES_NO` → trùng `"không"`, đổi luôn nhánh của Bách (`Chương 1 có cfg chưa?`).

Còn thiếu: Q014 `Có được dùng LLM/RAG không?` (xoá terminal `llm/rag`), Q018 `Tài liệu tham khảo
về statistical NLP là gì?`, C002 `Hạn nộp bài tập lớn vào tuần nào?`. Sinh thừa nhiều do các thành
phần rỗng đứng cạnh nhau (`MODAL`, `QUANTITY`, `ASSIGNMENT_OUTPUT_TARGET`, `OPT_*`) và
`CONTEXT_REFERENCE` dùng chung cho mọi nhánh ngữ cảnh: `Btl định dạng gì?`, `Bài này bắt buộc in ra
các gì?`, `Chương này nằm ở chương nào?`, `Phần 10 của project là gì?`. Lấn phần Bách: viết lại
3 nhánh BTL (160/148/30 khung), đổi `ASSIGNMENT_PART` sang `phần 1..10` và xoá `ROMAN_NUMBER`.

**Nhận** (sau khi sửa 5 lỗi trên):

- Deadline: `Hạn chót / Thời hạn của BTL …`; `… là bao giờ`; `Khi nào / Bao giờ (phải) nộp BTL`;
  `BTL khi nào nộp`, `BTL bao giờ hết hạn (nộp)`, `đến hạn nộp`.
- Tài liệu: `giáo trình`, `sách` (`RESOURCE_NOUN`); `Có giáo trình nào về CFG không`;
  `… nào viết về / hướng dẫn X`.
- Quy định: `Có được phép dùng AI không`; `Chính sách (về) LLM là gì / như thế nào / ra sao`.
- Tổng quan BTL: `BTL gồm những phần nào`, `bao gồm những gì`, `có những chức năng gì`,
  `cần / phải làm những gì`, `cần thực hiện những gì`; `Yêu cầu / Nội dung / Đề bài của BTL là gì`.
- Phần BTL: `Phần II cần làm (những) gì`, `yêu cầu (những) gì`, `BTL phần II cần làm gì`; `part i`.
- Tính năng BTL: `BTL có (chức năng / yêu cầu) parser không`; đảo `Phần parser có trong BTL không`.
- Output (dùng chung cho câu thường và câu ngữ cảnh): `cần / phải nộp những gì`, `cần nộp file
  gì`, `trả về kết quả gì`, `đầu ra là gì`, `định dạng đầu ra là gì`.
- `assignment`, `project` (`ASSIGNMENT_ENTITY`); `hay không` (`YES_NO`).
- Ngữ cảnh: `chương đó`, `phần đó`; `Còn chương sau thì sao / như thế nào`; `Nó nằm ở chương nào`;
  `Giáo trình / Sách của chương này …`, chữ "của" tùy chọn, `của nó`.

**Bỏ** (kèm lý do):

| Bỏ | Lý do |
| --- | --- |
| `phần 1..10`, `câu i` | `resolve_assignment_part` chỉ nhận i–iv; BTL có 4 phần |
| `PART_NUM_ROMAN_UPPER` | tokenizer đã lowercase |
| Deadline theo phần (`Bao giờ nộp phần I`) | semantic luôn trả deadline chung của BTL → trả lời sai đối tượng |
| Hỏi output không nói phần nào (`ASSIGNMENT_TARGET -> ASSIGNMENT_ENTITY`) | không biết trả lời phần nào |
| `RESOURCE_TOPIC`: `nlp`, `nlp cơ bản`, `nlp tiếng việt`, `ngữ pháp` | không có ID trong lexicon → NOT_FOUND |
| `dịch máy`, `thư viện có sẵn` | đúng nghĩa nhưng cần thêm alias trong code → `undone/T11-semantic.md` |
| `RESOURCE_NOUN`: `reference`, `textbook` | thừa, đã có tiếng Việt |
| `điểm danh`, `chuyên cần`, `nghỉ học`, `chép bài`, `share code` | quy định không có trong KB → NOT_FOUND |
| `chia sẻ bài` | sample đã có `chia sẻ bài làm` |
| `RULE_NOUN` `yêu cầu`, `về việc` | sinh `Yêu cầu AI là gì`, `Quy định về việc AI` |
| `FEAT_*` (`grammar`, `intent`, `kb`, `metric`, …) | semantic tra cứng 5 từ → cần sửa code trước, `undone/T11-semantic.md` |
| Tổ hợp rỗng `MODAL` / `QUANTITY` / `ASSIGNMENT_OUTPUT_TARGET` / `OPT_*` | sinh `BTL bắt nộp các gì`, `Btl định dạng gì` |
| `cái này`, `cái đó`, `bài này`, `mô đun này` | mơ hồ, không rõ trỏ chương hay phần BTL; sinh `Chương này nằm ở chương nào` |
| `Còn tuần sau / phần sau / câu tiếp theo` | handler chỉ xử lý "chương kế tiếp" → sai nghĩa |
| 3 nhánh ngữ cảnh mới (deadline, schedule, exam) | không nối vào `QUESTION`, không có handler |
| `YES_NO` `chưa` | `Chương 1 có CFG chưa` sai nghĩa |

---

## 4. Đánh giá chung (review 26/09)

| | Đúng phạm vi | Chất lượng grammar | Độ phủ câu mẫu | Tổng kết |
| --- | --- | --- | --- | --- |
| **Bảo** | ✅ hoàn toàn | ✅ sạch, không mơ hồ | ⚠️ rớt 2 câu vì "môn" | **Đạt** — PR sớm, đúng quy trình |
| **Bách** | ❌ lấn Bảo + Khoa, PR 71 file | ⚠️ sạch nhưng mỏng; 4 nhánh phá danh sách chốt | ✅ nhờ entity list + nhánh mới | **Chưa đạt** — grammar vừa đủ để câu mẫu pass; phần lớn công sức ngoài nhiệm vụ |
| **Khoa** | ⚠️ lấn 3 nhánh BTL của Bách | ❌ crash, hồi quy, sinh thừa | ⚠️ +2 câu, −1 câu | **Chưa đạt** — nhiều công sức nhất, cần sửa lỗi và tỉa |

### Đính chính so với review 26/09

- **D05 không pass:** review ghi D05 ✓, nhưng chỉ lượt 2 (`Nội dung này nằm ở chương nào?`, của
  Khoa) parse được; lượt 1 `L.O.2.5 học về gì?` (`Q_LO`, của Bách) rớt nên cả hội thoại rớt.
- **3 nhánh BTL làm trùng:** review đề xuất lấy bản Khoa làm nền; đo lại thì bản Bách được 33/42,
  bản Khoa 32/42 (mất Q011, sinh thừa). Vấn đề không còn vì đã lấy sample làm nền.
- **Thứ tự merge và lịch 27/09–02/10** của review không còn áp dụng: không PR nào được cập nhật
  sau review, nên chuyển sang cách gộp có chọn lọc ở trên.
- Quy trình rút ra (PR nhỏ, không định nghĩa lại biến, chủ sở hữu biến dùng chung, tiêu chí
  nghiệm thu) chuyển thành quy ước trong `docs/progress/README.md`.

## Thiết kế triển khai hiện tại

### Ranh giới thiết kế
File hiện hành là [`grammar.cfg`](../../../src/data/grammar.cfg), gốc `%start S`, production `S -> PREFIX QUESTION SUFFIX`. Prefix/lịch sự/dấu câu nằm ngoài nội dung yêu cầu; `QUESTION` có đúng 26 alternative, mỗi alternative là một nhánh `Q_*` có handler semantic tương ứng. Mục đích là thêm cách diễn đạt mà giữ nguyên schema semantic.

### Cấu trúc để semantic đọc được
Nhóm giữ các node `WEEK_ENTITY`, `CHAPTER_ENTITY`, `TOPIC_ENTITY`, `LO_ENTITY`, `ASSIGNMENT_PART`, `RESOURCE_TOPIC`, `RULE_TOPIC`, `EXAM_ENTITY`. Ví dụ `Tuần 3 học gì?` phải đi vào `Q_SCHEDULE_WEEK` và chứa `WEEK_ENTITY`, không nhận qua một nhánh keyword khác. Terminal dùng chữ thường khớp tokenizer; cụm kỹ thuật như `context-free` là một terminal.

Nhóm gộp grammar bằng cách chọn alternative có nghĩa và đặt vào constituent dùng chung. Không merge nguyên pipeline của PR #2, không thêm nhánh Q mới chỉ để nhận một câu mẫu, không nới đại từ nếu resolver chưa hỗ trợ. Các bảng nhận/bỏ phía trên là hồ sơ review phase 1, không phải danh sách các giới hạn hiện tại.

### Phần đã thay đổi sau phase 1
T18 đã thêm `ASSIGNMENT_FEATURE -> FEAT_PARSING | FEAT_SEMANTIC | FEAT_CONTEXT | FEAT_EVAL` cùng alias `dịch máy`, `thư viện có sẵn`. Vì vậy các dòng lịch sử từng hoãn FEAT/alias sang T11 đã được giải quyết ở `ebe53eb`; vẫn giữ 26 nhánh. C007/C008 còn ngoài grammar và có phân tích tại T17.

### Nghiệm thu và phạm vi kết luận
`python tools/check_grammar.py --samples 1000` dùng implementation hiện tại, kiểm 42/42 câu đề, 20/22 challenge, 6/6 hội thoại, 1.000 câu sinh phủ 26 nhánh. Không phát hiện mơ hồ trong 1.047 câu phân biệt đã thử; kết quả không chứng minh toàn bộ ngôn ngữ CFG không mơ hồ. Các con số 3.000/6.000 câu ở review cũ là số liệu lịch sử, chưa tái chạy nguyên thí nghiệm của từng PR trong đợt rà soát này.

Câu sinh có thể có query NOT_FOUND đúng vì tuần/chương/LO không tồn tại hoặc KB thiếu fact; câu ngữ cảnh đứng riêng có thể UNRESOLVED_CONTEXT. Điều kiện là parse/semantic đúng và fallback có nguyên nhân, không ép mọi query tìm thấy.
