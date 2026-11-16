# Hợp đồng giữa các tầng (contracts)

> **Cứng** những gì tầng khác hoặc đề bài phụ thuộc vào: dữ liệu đi qua chỗ nối giữa hai tầng.
> **Lỏng** cách mỗi tầng làm ra dữ liệu đó: thuật toán, cấu trúc nội bộ, câu chữ.
> **Cải tiến** được nhận nếu vẫn giữ hợp đồng; cải tiến làm đổi hợp đồng thì sửa file này + golden
> trong cùng PR (xem §10).

Hợp đồng được kiểm bằng máy: `src/tests/test_contract_*.py` chạy tầng của nhóm trên dữ liệu
**golden** trong `src/tests/golden/`. Golden sinh bằng `tools/make_golden.py`: chạy code của nhánh
`sample` (đóng băng) với grammar + data hiện tại trong `src/data/`.

| | Cứng (test kiểm) | Lỏng (tự quyết) |
| --- | --- | --- |
| Tokenizer | danh sách token của mọi câu | cách cài (regex, máy trạng thái…) |
| Parser | cây parse (nhãn, thứ tự con, node ε) hoặc không có cây | thuật toán (Earley, CYK, backtracking…), tốc độ |
| Generator | câu phải parse lại được, ≤ 10 000 câu | chiến lược sinh, thứ tự, độ đa dạng |
| Semantic | `intent`, `entity`, `slots`, `source_branch` | cách duyệt cây, cách tổ chức handler |
| Entity lexicon | ID chuẩn trả về | cách load / tra `entities.txt` |
| KB loader | cấu trúc `KnowledgeBase` (§4) | cách đọc từng file |
| Query | `found`, `kind`, `sources`, `data` (khi found) | chuỗi `query`, `reason`, cách tra |
| Answer | loại câu trả lời, dữ kiện bắt buộc, 3 câu fallback | câu chữ, template |
| Dialogue | frame sau khi giải tham chiếu | chuỗi giải thích `context_used`, cấu trúc lưu |
| Output files | tên + định dạng 9 file (§9, theo sample) | cách ghi file |

## 0. Chạy kiểm tra

```bash
cd src
python -m unittest discover -s tests -t .              # toàn bộ
python -m unittest tests.test_contract_semantic        # một tầng
```

- Tầng còn `NotImplementedError` → test **skip** (chưa làm), không tính là sai.
- Fail → in tối đa 10 bản ghi sai, mỗi bản ghi có expected / got.
- Mỗi test đưa vào đúng **đầu vào golden của tầng đó** (cây golden cho semantic, frame + KB golden
  cho query…) → mỗi tầng nghiệm thu độc lập, không chờ tầng trước.

Sinh lại golden (sau khi đổi `src/data/` hoặc đổi hợp đồng), từ gốc repo:

```bash
python tools/make_golden.py
```

## 1. Tokenizer — `tokenizer.tokenize(text) -> list[str]`

Golden: `tokenizer.jsonl` (2077 câu: câu test, câu hội thoại, câu sinh từ grammar, ca biên).

- Chữ thường, Unicode NFC, giữ dấu tiếng Việt; bỏ khoảng trắng thừa.
- `context-free`, `llm/rag`, `lo2.5` là **một** token (nối bằng `-` `/` `.`).
- `L.O.2.5`, `l.o.4.2` → `lo2.5`, `lo4.2`.
- Dấu câu `? ! . , : ;` là token riêng; ngoặc kép bị bỏ.

## 2. Grammar + Parser — `EarleyParser(grammar).parse(sentence) -> ParseResult`

Golden: `parser.jsonl` (2077 câu). File grammar: `src/data/grammar.cfg`, đúng **26 nhánh** `Q_*`.

- Câu thuộc văn phạm → `ParseResult.tree` là `Tree` gốc `S`; nhãn node = tên non-terminal; lá =
  token; non-terminal sinh ε là node **không có con** (`(PREFIX ε)` khi in).
- Câu ngoài văn phạm → `tree = None` (in `()`).
- Grammar hiện không có câu mơ hồ; nếu sau này có, parser phải chọn cây một cách xác định.

## 3. Semantic — `SemanticInterpreter(lexicon).interpret(tree) -> SemanticFrame`

Golden: `semantic.jsonl` (cây → frame). Nhánh `Q_*` con của `QUESTION` quyết định intent.

| Nhánh | intent | entity | slots |
| --- | --- | --- | --- |
| `Q_COURSE_CREDITS` | GET_COURSE_INFO | `CO3085` | `course`=CO3085, `field`=CREDITS |
| `Q_COURSE_PARTS` | GET_COURSE_INFO | `CO3085` | `course`=CO3085, `field`=MAIN_PARTS |
| `Q_COURSE_DESCRIPTION` | GET_COURSE_INFO | `CO3085` | `course`=CO3085, `field`=DESCRIPTION |
| `Q_COURSE_EXAM_DURATION` | GET_COURSE_INFO | `MIDTERM`/`FINAL` | `course`=CO3085, `field`=EXAM_DURATION, `exam`=MIDTERM/FINAL |
| `Q_COURSE_EXAM_TIME` | GET_COURSE_INFO | `MIDTERM`/`FINAL` | `course`=CO3085, `field`=EXAM_TIME, `exam`=MIDTERM/FINAL |
| `Q_COURSE_ASSESSMENT` | GET_COURSE_INFO | `CO3085` | `course`=CO3085, `field`=ASSESSMENT |
| `Q_INSTRUCTOR` | GET_INSTRUCTOR | `CO3085` | `course`=CO3085 |
| `Q_SCHEDULE_WEEK` | GET_SCHEDULE | `WEEK_NN` | `week`=WEEK_NN |
| `Q_SCHEDULE_CHAPTER` | GET_SCHEDULE | `CHNN` | `chapter`=CHNN |
| `Q_SCHEDULE_TOPICS` | GET_SCHEDULE | topic ID đầu tiên | `topics`=[topic ID, …] |
| `Q_TOPIC_BY_NAME` | GET_TOPIC | topic ID | `topic`=topic ID |
| `Q_TOPIC_BY_CHAPTER` | GET_TOPIC | `CHNN` | `chapter`=CHNN |
| `Q_TOPIC_RELATION` | GET_TOPIC | `CHNN` | `chapter`=CHNN, `relation`=topic ID |
| `Q_LO` | GET_LO | `LOx.y` | `lo`=LOx.y |
| `Q_ASSIGNMENT_OVERVIEW` | GET_ASSIGNMENT | `BTL01` | `assignment`=BTL01, `section`=OVERVIEW |
| `Q_ASSIGNMENT_PART` | GET_ASSIGNMENT | `PART_I..IV` | `assignment`=BTL01, `section`=PART_I..IV |
| `Q_ASSIGNMENT_FEATURE` | GET_ASSIGNMENT | `PART_I..IV` | `assignment`=BTL01, `section`=PART_I..IV, `feature`=cụm từ gốc |
| `Q_ASSIGNMENT_OUTPUT` | GET_ASSIGNMENT | `PART_I..IV` | `assignment`=BTL01, `section`=PART_I..IV, `field`=OUTPUTS |
| `Q_DEADLINE` | GET_DEADLINE | `BTL01` | `assignment`=BTL01 |
| `Q_RESOURCE` | GET_RESOURCE | resource topic ID | `topic`=resource topic ID |
| `Q_RULE` | GET_RULE | rule ID | `rule`=rule ID |
| `Q_CONTEXT_TOPIC_RELATION` | CONTEXT_DEPENDENT | `null` | `action`=TOPIC_RELATION, `relation`=topic ID |
| `Q_CONTEXT_NEXT_CHAPTER` | CONTEXT_DEPENDENT | `null` | `action`=NEXT_CHAPTER |
| `Q_CONTEXT_ASSIGNMENT_OUTPUT` | CONTEXT_DEPENDENT | `null` | `action`=ASSIGNMENT_OUTPUT |
| `Q_CONTEXT_RESOURCE` | CONTEXT_DEPENDENT | `null` | `action`=CONTEXT_RESOURCE |
| `Q_CONTEXT_LO_CHAPTER` | CONTEXT_DEPENDENT | `null` | `action`=LO_CHAPTER |
| không có cây | UNKNOWN | `null` | — (`source_branch` = `null`) |

- `source_branch` = tên nhánh `Q_*`.
- ID chuẩn: `WEEK_03`, `CH03`, `LO2.5`, `PART_II`; topic ID như `CFG`, `PCFG`, `QUESTION_ANSWERING`;
  resource topic ID như `STATISTICAL_NLP`, `PYTHON_NLP`; rule ID như `AI_USAGE`, `LLM_RAG`. Giá trị
  không có trong lexicon → `null` (không đoán).
- Bước semantic **không đọc KB**.

### Mở rộng T18 (2026-11-16)

`ASSIGNMENT_FEATURE` chứa một node nhóm: `FEAT_PARSING` → `PART_I`,
`FEAT_SEMANTIC` → `PART_II`, `FEAT_CONTEXT` → `PART_III`, `FEAT_EVAL` → `PART_IV`.
Handler đọc nhãn nhóm; slot `feature` giữ cụm từ gốc. Các cách gọi mới gồm
`grammar`, `parse tree`, `intent`, `entity`, `kb`, `hội thoại`, `test set`, `metric`.
Alias resource `dịch máy` → `MACHINE_TRANSLATION`; rule `thư viện có sẵn` →
`EXTERNAL_LIBRARIES`. Intent và schema query không đổi.

`tools/make_golden.py` áp dụng riêng các mở rộng này lên oracle nhánh `sample`
trước khi sinh golden; không sửa nhánh `sample` và không dùng code nhóm làm oracle.
Các câu mở rộng nằm trong `EDGE_SENTENCES` để bảo đảm kiểm tra dù generator đổi thứ tự.

## 4. KB loader — `KnowledgeBase.load(kb_dir) -> KnowledgeBase`

Golden: `kb.json` (so khớp tuyệt đối từng collection). `validate()` trả `[]` với KB được cấp.

| Trường | Kiểu | Khoá | Bản ghi |
| --- | --- | --- | --- |
| `course` | dict (23 khoá) | tên thuộc tính (`credits`, `assessment`, …) | giá trị / dict con |
| `weeks` | dict (15) | `WEEK_NN` | `week_id`, `chapter_id`, `chapter`, `part`, `topics` (+ `activity`, `milestone` nếu có) |
| `chapter_weeks` | dict (12) | `CHNN` | danh sách `WEEK_NN` |
| `topics` | dict (12) | `CHNN` | `chapter_id`, `chapter_number` (int), `title`, `part`, `summary`, `keywords`, `keyword_list`, `subtopics` |
| `assignment` | dict (14) | `assignment_id`, `title`, `goal`, `sections`, … | |
| `resources` | tuple (8) | — | `resource_id`, `title`, `kind`, `year`, `usage` (+ `authors`, `publisher` nếu có) |
| `regulations` | dict (8) | rule key | văn bản quy định |

Chi tiết từng giá trị: xem `src/tests/golden/kb.json`.

## 5. Query — `QueryEngine(kb).execute(frame) -> QueryResult`

Golden: `query.jsonl` (frame → result, chạy trên KB golden).

| kind | found | `data` khi found | sources |
| --- | --- | --- | --- |
| `COURSE_CREDITS` | ✓ | `{credits}` | `kb/course_info.txt` |
| `COURSE_PARTS` | ✓ | `{parts: list}` | `kb/course_info.txt` |
| `COURSE_DESCRIPTION` | ✓ | `{description}` | `kb/course_info.txt` |
| `EXAM_DURATION` | ✓ | `{exam, format}` | `kb/course_info.txt` |
| `EXAM_TIME` | ✗ (KB không có) | — | — |
| `ASSESSMENT` | ✓ | `{class_attention_and_assignments, major_assignment, midterm_exam, final_exam}` | `kb/course_info.txt` |
| `INSTRUCTOR` | ✗ (KB không có) | — | — |
| `SCHEDULE_WEEK` | ✓/✗ | bản ghi `weeks[WEEK_NN]` | `kb/schedule.txt` |
| `SCHEDULE_CHAPTER` | ✓/✗ | `{chapter_id, weeks}` | `kb/schedule.txt` |
| `SCHEDULE_TOPICS` | ✓/✗ | `{topics, weeks: [bản ghi tuần]}` | `kb/schedule.txt` |
| `TOPIC_CHAPTER` | ✓/✗ | bản ghi `topics[CHNN]` | `kb/topics.txt` |
| `TOPIC_SEARCH` | ✓ | `{topic, chapters: [bản ghi chương]}` | `kb/topics.txt` |
| `TOPIC_RELATION` | ✓ | `{chapter, relation, related: bool}` | `kb/topics.txt` |
| `LEARNING_OUTCOME` | ✓/✗ | `{lo, description}` | `kb/course_info.txt` |
| `LO_CHAPTER` | ✓ | `{lo, chapter}` | `kb/course_info.txt`, `kb/topics.txt` |
| `ASSIGNMENT_OVERVIEW` | ✓ | `{assignment_id, title, goal, sections}` | `kb/assignments.txt` |
| `ASSIGNMENT_SECTION` | ✓/✗ | `{section, field, feature}` | `kb/assignments.txt` |
| `DEADLINE` | ✓ | `[{week_id, milestone}]` | `kb/schedule.txt` |
| `RESOURCE` | ✓ | `[bản ghi resources]` | `kb/resources.txt` |
| `RULE` | ✓ | `{rule_id, text}` | `kb/regulations.txt` |
| `UNKNOWN` | ✗ | — | — (câu không parse được) |
| `UNRESOLVED_CONTEXT` | ✗ | — | — (frame `CONTEXT_DEPENDENT` chưa giải được) |

- **`found = False` khi và chỉ khi câu trả lời sẽ là một câu fallback.** Có dữ kiện mà rỗng (ví dụ
  output của Phần II/III/IV không có trong KB) → `found = False`. Đây là bug của sample, golden đã
  sửa: sample trả `found = True` rồi answer lại báo không tìm thấy.
- Query **không đọc lại câu hỏi gốc**, không bịa dữ kiện.
- `query` (chuỗi mô tả truy vấn, in ra `query.txt`) và `reason` là văn bản tự do.

## 6. Answer — `AnswerGenerator().generate(frame, result) -> str`

Golden: `answer.jsonl`.

- Ba câu fallback là hằng trong `answer.py`, phân biệt nhau:
  - `NOT_FOUND` = **"Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học."** (nguyên
    văn đề bài) — `found = False`, kind khác hai kind dưới.
  - `NOT_UNDERSTOOD` — kind `UNKNOWN`.
  - `MISSING_CONTEXT` — kind `UNRESOLVED_CONTEXT`.
- `found = True` → không được trả câu fallback, và phải chứa đủ **dữ kiện bắt buộc** (`must_contain`,
  lấy từ `expected_answer_terms` trong `sample_queries.txt`; so không phân biệt hoa thường).
- Câu chữ tự do (`reference_answer` trong golden chỉ để tham khảo, test không so).
- Answer không tra KB thêm.

## 7. Dialogue — `DialogueContext.resolve(frame)` / `update(frame, result)`

Golden: `dialogue.jsonl` (6 hội thoại, từng lượt: frame thô → frame đã giải).

| `action` | Cần | Frame sau khi giải |
| --- | --- | --- |
| `TOPIC_RELATION` | chương gần nhất | `GET_TOPIC(entity=CHNN, chapter=CHNN, relation=…)` |
| `NEXT_CHAPTER` | chương gần nhất, chương sau ≤ 12 | `GET_TOPIC(entity=CH(n+1), chapter=CH(n+1))` |
| `ASSIGNMENT_OUTPUT` | phần BTL gần nhất | `GET_ASSIGNMENT(entity=PART_x, assignment=BTL01, section=PART_x, field=OUTPUTS)` |
| `CONTEXT_RESOURCE` | chương gần nhất | `GET_RESOURCE(entity=CHNN, topic=CHNN, chapter=CHNN)` |
| `LO_CHAPTER` | LO gần nhất | `GET_TOPIC(entity=LOx.y, lo=LOx.y)` |
| thiếu ngữ cảnh / frame thường | — | giữ nguyên frame |

- `source_branch` giữ nguyên khi giải.
- `update` chỉ ghi nhớ khi `result.found`: entity `CH*` → chương, `PART_*` → phần BTL, `LO*` → LO;
  `SCHEDULE_WEEK` → `chapter_id` của tuần; `TOPIC_SEARCH` → chương đầu tiên tìm được.

## 8. End-to-end — `CourseAssistant.from_root(src).process(...)`

Golden: `cases.jsonl` (42 câu mẫu + 22 câu thách thức, có cờ `reference_pass`).

- Mỗi bộ (official, challenge) reset ngữ cảnh **một lần** rồi chạy theo thứ tự file — giống cách
  chấm, vì có câu tham chiếu câu ngay trước.
- Trạng thái: `found` → FOUND; kind `UNKNOWN`/`UNRESOLVED_CONTEXT` → SKIPPED; còn lại → NOT_FOUND.
  Entity rỗng → `OUT_OF_SCOPE` (intent UNKNOWN) hoặc `NONE`.
- Câu sample làm đúng (`reference_pass`) **phải** đúng. Câu sample làm sai (C007, C008) là mục tiêu
  cải tiến: test chỉ in số câu đã làm được.

## 9. Output files

**Chốt theo định dạng của sample** (xem bản thật: `git show sample:docs/sample-src/output/<file>`).
Đề chỉ bắt buộc: câu ngoài văn phạm in `()`; `samples.txt` mỗi dòng một câu, tối đa 10 000 câu —
phần còn lại nhóm chốt như dưới. UTF-8, xuống dòng `\n`.

Đầu vào: `input/sentences.txt`, bỏ dòng trống và dòng bắt đầu bằng `#`, chạy theo thứ tự với ngữ
cảnh giữ giữa các câu. `ID` = số thứ tự câu trong input, 3 chữ số (`001`, `002`…). Các file theo
từng câu có đúng một bản ghi cho mỗi câu, cùng thứ tự.

| File | Định dạng mỗi dòng / khối | Ví dụ |
| --- | --- | --- |
| `grammar.txt` | bản sao nguyên văn `data/grammar.cfg` dùng cho lần chạy | — |
| `samples.txt` | một câu sinh từ grammar mỗi dòng (detokenize, viết hoa chữ đầu, có `?`) | `Cho mình hỏi môn học gồm những phần nào ạ?` |
| `parse-results.txt` | `Tree.bracketed()` của câu, hoặc `()` nếu bị từ chối; không có ID | `(S (PREFIX ε) (QUESTION (Q_SCHEDULE_WEEK (WEEK_ENTITY tuần (WEEK_NUMBER 3)) (WEEK_CONTENT_QUESTION học gì))) (SUFFIX (END_MARK ?)))` |
| `semantic.txt` | `ID<TAB>predicate`; câu ngữ cảnh: `raw => resolved [context_used]` | `002	GET_SCHEDULE(entity=WEEK_03, week=WEEK_03)` · `007	CONTEXT_DEPENDENT(action=TOPIC_RELATION, relation=PARSING) => GET_TOPIC(entity=CH04, chapter=CH04, relation=PARSING) [tham chiếu gần nhất → CH04]` · `009	UNKNOWN()` |
| `intent-entity.txt` | một object JSON mỗi dòng, khoá sắp theo chữ cái: `entity` (sau khi giải ngữ cảnh, `null` nếu không có), `id` (số), `intent` (trước giải), `question`, `resolved_intent` | `{"entity": "CH04", "id": 7, "intent": "CONTEXT_DEPENDENT", "question": "Nó có liên quan đến parsing không?", "resolved_intent": "GET_TOPIC"}` |
| `query.txt` | `ID<TAB>query<TAB>status=FOUND\|NOT_FOUND<TAB>source=<file, …>` hoặc `source=-` | `002	KB.weeks[WEEK_03]	status=FOUND	source=kb/schedule.txt` · `009	NO_QUERY	status=NOT_FOUND	source=-` |
| `answer.txt` | 2 dòng mỗi câu: `ID<TAB>Q: <câu hỏi>` rồi `<TAB>A: <câu trả lời>` | `008	Q: Tuần 99 học gì?` / `	A: Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học.` |
| `dialogue.txt` | tiêu đề `LOCAL DISCOURSE CONTEXT RESULTS`; mỗi hội thoại: `Dxx \| PASS\|FAIL \| expected=… \| resolved=…`, rồi mỗi lượt `Un:`, `PARSEn:`, `SEMANTICn:`, `CONTEXTn:` (nếu có), `An:`, dòng trống; cuối: `Tổng: x/y hội thoại đúng (p%).` | `D01 \| PASS \| expected=CH03 \| resolved=CH03` |
| `evaluation.txt` | tiêu đề `COURSE ASSISTANT - EVALUATION REPORT` + mô tả phương pháp; mục **A** bộ của đề, **B** bộ thử thách — mỗi mục: số câu, tỉ lệ intent / entity / query-status / answer-fact / end-to-end, rồi bảng `ID \| Kết quả \| Expected \| Actual \| Parse \| Query expected/actual \| Answer`; mục **C** phân tích lỗi từng ca sai; mục **D** ưu điểm và hạn chế | `Q026 \| PASS \| UNKNOWN/OUT_OF_SCOPE \| UNKNOWN/OUT_OF_SCOPE \| () \| SKIPPED/SKIPPED \| ok` |

Ghi chú: `query.txt` chỉ có 2 trạng thái (câu không parse được in `NO_QUERY status=NOT_FOUND`),
còn `evaluation.txt` tách thêm `SKIPPED` (§8) — giữ đúng như sample.

Không có golden test cho output: nghiệm thu bằng review, so định dạng với bản của sample.

## 10. Đổi hợp đồng

1. Mở PR sửa `docs/contracts.md` (nói rõ đổi gì, vì sao), code liên quan, và nếu cần
   `tools/make_golden.py` (ví dụ thêm một ca sửa lỗi của sample như §5).
2. Chạy `python tools/make_golden.py`, commit golden mới trong cùng PR.
3. Phúc review. Không sửa tay file trong `src/tests/golden/`.

Ví dụ cải tiến cần đổi hợp đồng: FEAT_* của Khoa (thêm giá trị `feature` mới → đổi §3),
alias `dịch máy` (thêm resource topic ID → đổi §3, §5).
