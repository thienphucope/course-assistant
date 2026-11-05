# Progress — theo dõi tiến độ BTL

> Cái nào **thầy cho sẵn**, cái nào **mình phải tự xây**. Đầu tư: **~70% vào
> Grammar + Cây→Intent**, 30% cho đường ống còn lại. Lý thuyết từng trạm: `docs/knowledge/`.

Mỗi việc là **một file `.md`** tên `Txx-<tên>.md`:

- `undone/` — việc chưa xong (chưa làm hoặc đang làm).
- `done/` — việc đã xong, kèm kết quả và commit.

**ID `Txx`** cố định suốt đời task: không đổi khi chuyển thư mục, không dùng lại. Việc mới lấy số
kế tiếp (hiện tới **T24**). Gọi task bằng ID trong PR, commit, chat: "xong T11".

**Tên = ranh giới**: task code mang tên tầng trong `docs/contracts.md` và trùng tên test
nghiệm thu (`T11-semantic` ↔ `tests.test_contract_semantic`); một file code chỉ thuộc một task.

Xong một việc: `git mv docs/progress/undone/Txx-<tên>.md docs/progress/done/`, rồi điền
**Ngày xong**, **Commit** và **Kết quả** trong file.

Legend dùng trong tiêu đề: ✅ có sẵn · 🔥 tốn công/ăn điểm · ⚙️ chuẩn, làm 1 lần ·
🔧 plumbing · ✨ optional (điểm cộng).

## Danh sách task

| ID | Việc | Ranh giới (code · hợp đồng) | Nghiệm thu | Trạng thái |
| --- | --- | --- | --- | --- |
| T01 | ✅ Dữ liệu thầy cho sẵn | `src/data/` | — | done |
| T02 | 🔧 Đồng bộ `src/data/` với data đầy đủ | `src/data/kb`, `scaffolding` | — | done |
| T03 | 🔥 Grammar phase 1 — mở rộng và gộp | `src/data/grammar.cfg` | 42/42 · 0 mơ hồ | done |
| T04 | 🔧 Kết thúc PR phase 1 (merge tay) | GitHub PR #1–#3 | — | done |
| T05 | 🔧 Codebase chuẩn: skeleton, không dùng pipeline PR #2 | — | — | done |
| T06 | 🔧 Hợp đồng giữa các tầng + golden test | `docs/contracts.md`, `tools/make_golden.py`, `src/tests/` | — | done |
| T07 | 🔧 Quyết định của nhóm | — | — | undone |
| T08 | ⚙️ Tokenizer | `tokenizer.py` · §1 | `test_contract_tokenizer` | undone |
| T09 | ⚙️ Grammar loader + Parser | `grammar.py`, `parser.py` · §2 | `test_contract_parser` | undone |
| T10 | ⚙️ Generator | `generator.py` | parse lại 100% | undone |
| T11 | 🔥 Semantic + entity lexicon | `semantic.py`, `entities.py` · §3 | `test_contract_semantic` | undone |
| T12 | 🔧 KB loader | `kb.py` · §4 | `test_contract_kb` | done (chờ review) |
| T13 | 🔧 Query | `query.py` · §5 | `test_contract_query` | done (chờ review) |
| T14 | 🔧 Answer + not-found | `answer.py` · §6 | `test_contract_answer` | undone |
| T15 | ✨ Dialogue (Phần III) | `dialogue.py` · §7 | `test_contract_dialogue` | undone |
| T16 | 🔧 Pipeline + CLI + 9 file output | `pipeline.py`, `cli.py`, `output.py`, `paths.py`, `run.py` · §8–9 | `test_contract_pipeline` + `run.py all` | done |
| T17 | 🔧 Evaluation + mở rộng bộ test | `evaluate.py` · §8 | `evaluation.txt` đúng §9 | done |
| T18 | 🔥 Grammar mở rộng sau phase 1 | `src/data/grammar.cfg` | 42/42 · 0 mơ hồ | undone |
| T19 | 🔧 Script kiểm tra grammar | `tools/` | — | undone |
| T20 | 🔧 README nộp bài | `README.md` | đủ mục đề 7.5 | undone |
| T21 | 🔧 Dockerfile | `Dockerfile` | build + chạy được | undone |
| T22 | 🔥 Báo cáo (+ ghi nguồn, khai báo AI) | — | đủ mục đề 6, 7.6 | undone |
| T23 | 🔧 Video demo + thuyết trình | — | đủ cảnh đề 7.6 | undone |
| T24 | 🔧 Đóng gói zip nộp bài | `project/` | đúng đề 7.4, < 10MB | undone |

Đợt code (thứ tự gợi ý): **T08, T09, T12, T10** song song → **T11, T13** → **T14, T16** → **T17,
T15** → **T20–T24**. Test hợp đồng dùng đầu vào golden nên T11, T13, T14 nghiệm thu được trước
khi tầng trước xong.

## Ai đọc KB khi nào (đừng lẫn)

- **Design time (bạn):** đọc `entities.txt` (schema + vocab) để viết grammar/intent.
- **Run time (máy):** bước intent **KHÔNG** đọc KB; chỉ bước **query** mới mở `src/data/kb/` —
  "có thì bóc, không thì rỗng". Chi tiết: `docs/knowledge/03-grammar-vs-kb.md`.

## Mẫu file

```markdown
# Txx · 🔧 Tên việc

- **Trạng thái:** chưa làm | đang làm | xong
- **Phụ trách:** <tên> (chưa giao)
- **Code:** <file thuộc ranh giới task này>
- **Nghiệm thu:** <test / tiêu chí>
- **Ngày xong / Commit:** <điền khi chuyển sang done/>

## Việc cần làm
- [ ] ...

## Ghi chú
```

## Quy ước làm việc (rút từ review phase 1)

- **Trước khi code một tầng: đọc `docs/contracts.md`.** Nghiệm thu = test hợp đồng của tầng đó
  pass (`cd src && python -m unittest tests.test_contract_<tầng>`); ghi trong mục **Nghiệm thu**
  của từng file `undone/`. Cách làm bên trong tầng là tự do.
- **PR nhỏ, đúng phạm vi, rebase lên `main` trước khi mở.**
- **Grammar:** giữ đúng 26 nhánh `Q_*` của `QUESTION`. Câu mới = thêm alternative vào nhánh có
  sẵn, không thêm nhánh mới.
- **Dùng lại biến có sẵn, không định nghĩa lại biến đã có.** Biến dùng chung (`YES_NO`,
  `TOPIC_ENTITY`, `ASSIGNMENT_PART`, `ASSIGNMENT_ENTITY`, `CONTEXT_REFERENCE`, `COURSE_SUBJECT`)
  muốn sửa phải báo cả nhóm.
- **Tiêu chí nghiệm thu một nhánh grammar:** pass toàn bộ câu mẫu thuộc nhánh; không làm rớt câu
  nào đang pass; không sinh câu mơ hồ; đọc 20 câu sinh ngẫu nhiên không có câu vô nghĩa.
- **Nhánh `sample` là bản tham khảo, đóng băng** — không commit vào đó. **Khuyến khích đọc** để
  xem một cách làm từng tầng: code ở `docs/sample-src/src/hcmut/iaslab/nlp/app/`, output mẫu ở
  `docs/sample-src/output/`. Xem không cần đổi nhánh: `git show sample:docs/sample-src/src/hcmut/iaslab/nlp/app/parser.py`,
  hoặc mở song song: `git worktree add ../Assignment-sample sample`. Điều kiện: tự hiểu và giải thích
  được code mình nộp (đề mục 8), pass test hợp đồng, ghi nguồn tham khảo trong báo cáo.
