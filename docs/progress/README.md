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

Các ticket T01–T19 có mục **Thiết kế triển khai hiện tại**: file/API, luồng xử lý,
schema, quyết định thiết kế, lỗi/giới hạn và cách nghiệm thu. Số liệu giai đoạn cũ
ghi dưới nhãn lịch sử. Kết quả đối chiếu và sửa bug sau mốc `9096375` nằm tại
[`design-audit.md`](../validation/design-audit.md).

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
| T07 | 🔧 Quyết định của nhóm | — | — | done |
| T08 | ⚙️ Tokenizer | `tokenizer.py` · §1 | `test_contract_tokenizer` | done |
| T09 | ⚙️ Grammar loader + Parser | `grammar.py`, `parser.py` · §2 | `test_contract_parser` | done |
| T10 | ⚙️ Generator | `generator.py` | parse lại 100% | done |
| T11 | 🔥 Semantic + entity lexicon | `semantic.py`, `entities.py` · §3 | `test_contract_semantic` | done |
| T12 | 🔧 KB loader | `kb.py` · §4 | `test_contract_kb` | done |
| T13 | 🔧 Query | `query.py` · §5 | `test_contract_query` | done |
| T14 | 🔧 Answer + not-found | `answer.py` · §6 | `test_contract_answer` | done |
| T15 | ✨ Dialogue (Phần III) | `dialogue.py` · §7 | `test_contract_dialogue` | done |
| T16 | 🔧 Pipeline + CLI + 9 file output | `pipeline.py`, `cli.py`, `output.py`, `paths.py`, `run.py` · §8–9 | `test_contract_pipeline` + `run.py all` | done |
| T17 | 🔧 Evaluation + mở rộng bộ test | `evaluate.py` · §8 | `evaluation.txt` đúng §9 | done |
| T18 | 🔥 Grammar mở rộng sau phase 1 | `src/data/grammar.cfg` | 42/42 · 0 mơ hồ | done |
| T19 | 🔧 Script kiểm tra grammar | `tools/` | — | done |
| T20 | 🔧 README nộp bài | `README.md` | đủ mục đề 7.5 | nội dung kỹ thuật xong; chờ tên/MSSV |
| T21 | 🔧 Dockerfile | `Dockerfile` | build + chạy được | đã chuẩn bị; chờ kiểm chứng Docker |
| T22 | 🔥 Báo cáo (+ ghi nguồn, khai báo AI) | — | đủ mục đề 6, 7.6 | nội dung xong; chờ nhóm duyệt/định dạng |
| T23 | 🔧 Video demo + thuyết trình | — | đủ cảnh đề 7.6 | nội dung/video tự động xong; chờ nhóm/phân vai |
| T24 | 🔧 Đóng gói zip nộp bài | `project/` | đúng đề 7.4, < 10MB | gói kiểm tra xong; chờ MSSV và Docker |

Đợt code (thứ tự gợi ý): **T08, T09, T12, T10** song song → **T11, T13** → **T14, T16** → **T17,
T15** → **T20–T24**. Test hợp đồng dùng đầu vào golden nên T11, T13, T14 nghiệm thu được trước
khi tầng trước xong.

## Cân nhắc sau — rà theo đề (17/11/2026)

Đối chiếu đề PDF với output, README, gói nộp tại `620b673`: Phần I, II (Classical), III, IV đạt;
8/8 câu ví dụ của đề đúng theo KB; chạy kiểu `ENTRYPOINT` (`run.py --root`, gói giải nén, cwd khác)
ra 9 output khớp repo. Còn lại:

**Chặn nộp bài**

- [ ] Tên/MSSV trong README, báo cáo, tên zip (T20, T22, T24).
- [ ] `docker build` + `run` thật trên máy có Docker: `python tools/package_submission.py
      --student-ids ... --verify-docker` (T21) — bài chấm bằng Docker.
- [ ] Khai báo AI (đề mục 8, `AI_usage`): báo cáo/README mới ghi Codex; lịch sử git còn commit đồng
      tác giả Claude (`git log --grep='Co-Authored-By: Claude'`) → bổ sung Claude Code (T22, T20).
- [ ] Phân vai thuyết trình; cân nhắc quay video có thuyết minh thay bản tự động không tiếng (T23).

**Chất lượng — nên chuẩn bị giải thích hoặc sửa**

- [ ] Tài liệu theo chương ("Tài liệu của phần này ở đâu?"): KB không có quan hệ tài liệu–chương nên
      trả tài liệu NLP nền, nhưng câu trả lời ghi "Tài liệu phù hợp:" như thể riêng cho chương →
      đổi câu chữ (T14) hoặc nói rõ khi bị hỏi.
- [ ] "Tài liệu nào nói về CFG?" → Speech and Language Processing đến từ bảng `RESOURCE_TERMS` nhóm tự
      viết trong `query.py`, không phải dữ kiện KB (T13).
- [ ] `evaluation.txt` mục C: C007/C008 chỉ có một câu lý do chung; nguyên nhân cụ thể (thiếu mẫu
      "buổi mỗi tuần", không nhận số thứ tự "thứ ba", KB cũng không có số buổi) mới nằm ở README (T17).
- [ ] 42/42 đo trên tập dùng khi phát triển; 32 câu phase 1 + ngữ cảnh trong `input/sentences.txt`
      chưa gắn nhãn chấm → gắn nhãn để tăng mẫu "các cách diễn đạt khác nhau" (T17).
- [ ] `samples.txt` có 38 câu viết `Lo1`, `Lo2.5` thay vì `LO1`, `LO2.5` — chỉ là hiển thị (T10).

## Ai đọc KB khi nào (đừng lẫn)

- **Design time (bạn):** đọc `entities.txt` (schema + vocab) để viết grammar/intent.
- **Khởi tạo:** loader nạp `src/data/kb/` một lần khi dựng `CourseAssistant`.
- **Xử lý từng câu:** semantic/intent **không đọc KB**; query tra đối tượng KB đã nạp,
  trả dữ kiện hoặc kết quả rỗng. Chi tiết ranh giới: `docs/knowledge/03-grammar-vs-kb.md`.

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

## Thiết kế triển khai
- File/API và kiểu dữ liệu vào/ra.
- Luồng xử lý, thuật toán và lý do chọn cách làm.
- Bất biến, ca lỗi và giới hạn còn lại.

## Kiểm chứng
- Test/lệnh chạy thật, kết quả và phạm vi kết luận.
- Đối chiếu code với thiết kế; phân biệt số liệu hiện tại và lịch sử.

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
