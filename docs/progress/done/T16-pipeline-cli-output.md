# T16 · 🔧 Ghép pipeline + CLI + ghi output (`run.py all`)

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Code:** `src/hcmut/iaslab/nlp/app/pipeline.py` (`CourseAssistant.from_paths`), `cli.py`,
  `output.py`, `paths.py`, `src/run.py`
- **Output:** cả 9 file trong `src/output/`
- **Nghiệm thu:** `tests.test_contract_pipeline` pass; `python run.py all` (trong `src/`) sinh đủ
  9 file từ `input/sentences.txt`
- **Ngày xong / Commit:** 05/11/2026 · nhánh `dev`, commit chứa file này

## Đã làm

- [x] `ProjectPaths.discover()` — đi ngược từ vị trí module tìm `run.py` + `data/grammar.cfg`,
      không phụ thuộc cwd; `source` hỗ trợ cả layout phát triển và gói nộp.
- [x] `CourseAssistant.from_paths`: load grammar, lexicon (`entities.txt`), KB (+ `validate()`,
      lỗi thì `ValueError`), dựng `PipelineComponents`. Thêm property `grammar`, `parser` cho CLI.
- [x] `cli.py`: lệnh `all`, `parse`, `answer` (`--trace`), `generate`, `evaluate`, `interactive`.
- [x] Reader `input/sentences.txt` (bỏ dòng trống và `#`), chạy theo thứ tự, giữ ngữ cảnh.
- [x] `output.py`: `write_grammar`, `write_samples` (≤ 10 000), `write_pipeline_outputs`; cùng
      `dialogue.txt`, `evaluation.txt` — định dạng theo `docs/contracts.md` §9.
- [x] `src/tests/test_pipeline.py` kiểm official end-to-end, context/reset, FEAT/alias và
      fallback; test audit kiểm thêm các ca biên của assembler/output.

## Kết quả ở mốc 05/11/2026 (lịch sử)

- `python run.py all`: 73 câu input, 1000 câu mẫu, **9 file output**, khoảng 1,8 s.
  `--samples 10000` ra **9849 câu** (không trùng, hợp lệ, < 10 000).
- Bộ test (`dev`): 28 test, 0 fail, 4 skip (test khung cũ `test_kb`, `test_parser_generator`,
  `test_pipeline` chưa ai viết). Hai test của `test_contract_pipeline` pass.
- Hiệu năng: nạp grammar + KB + lexicon 0,06 s; ~0,7 ms/câu qua pipeline đầy đủ.
- Đối chiếu với `sample` (cùng grammar, KB, input): 8/9 file output khớp từng dòng. Chỉ
  `samples.txt` khác — hai generator duyệt khác nhau, không câu nào trùng; cả hai đều 1000/1000
  câu parse lại được và phủ đủ **26/26 nhánh `Q_*`**.

## Ghi chú

- Code T16 lấy từ nhánh `sample` (bản của Phúc) rồi chuyển sang layout `main` (root là `src/`),
  nối với code của các member (PR #4, #5, #7). Phần viết thêm: `discover()`, `from_paths`,
  property `grammar`/`parser`, đổi `CourseAssistant(paths)` → `from_paths(paths)` trong `cli.py`.
- Khi ghi nguồn trong báo cáo (T22): pipeline/CLI/output dựa trên bản `sample`.

## Thiết kế triển khai hiện tại

### Composition root và đường dẫn
[`CourseAssistant.from_paths`](../../../src/hcmut/iaslab/nlp/app/pipeline.py) nạp grammar, EntityLexicon, KnowledgeBase và validate trước khi dựng PipelineComponents. KB được nạp ở bước này, không mở lại ở mỗi query. Tham số keyword grammar cho phép truyền CFG đã nạp; T19 dùng nó để `--grammar` không bị lỗi vì file grammar mặc định khác đang hỏng.

[`ProjectPaths.discover`](../../../src/hcmut/iaslab/nlp/app/paths.py) đi từ vị trí module lên các thư mục cha, tìm run.py và data/grammar.cfg. Marker hiện tại không phải pyproject.toml. from_root nhận root ứng dụng: src/ trong repo hoặc project/ trong gói nộp. source là root/src nếu có package hcmut ở đó, còn lại là root. Không truyền gốc repo làm --root rồi mong tự chuyển sang src/.

### Luồng một câu và state
process gọi parse → interpret → resolve (nếu use_context) → execute → generate → update context (nếu use_context). PipelineResult giữ sentence, parse, raw_semantic, semantic sau resolve, query, answer và context_used. detected_intent là intent gốc; detected_entity ưu tiên entity sau resolve. use_context=False bỏ qua resolve/update nhưng không xóa bộ nhớ phiên đã có.

### CLI và batch
[`cli.py`](../../../src/hcmut/iaslab/nlp/app/cli.py) có all/parse/answer/generate/evaluate/interactive; --root nằm trước subcommand. Launcher run.py hỗ trợ cả package đặt trực tiếp trong src/ lẫn project/src/. CLI hiện dựng toàn bộ assistant trước dispatch nên parse/generate cũng cần KB hợp lệ.

`all` đọc input UTF-8, bỏ dòng trống và comment #, xuất grammar, sinh và parse lại samples, reset context rồi xử lý input theo thứ tự; cuối cùng evaluate official/challenge riêng và reset giữa các dialogue. Một lệnh answer nhận nhiều câu giữ chung phiên; hai lệnh khác nhau không chia state. interactive có /reset và /quit.

### Chín output và hợp đồng
[`output.py`](../../../src/hcmut/iaslab/nlp/app/output.py) ghi grammar nguyên source_text, mỗi sample/cây một dòng, semantic ID+predicate, intent/entity JSONL sort_keys, query ID+status+source và answer hai dòng mỗi câu. Evaluation/dialogue dùng renderer của T17. File UTF-8, newline LF. Đợt audit sửa write_grammar vì rstrip từng làm mất dòng trống cuối, trái yêu cầu sao nguyên văn grammar.

Samples không chứa dòng stats. Query output chỉ FOUND/NOT_FOUND; evaluation tách SKIPPED. ID bắt đầu 001 và cùng thứ tự ở các file theo câu. Semantic giữ cả raw và resolved nếu có context trace.

### Kiểm chứng và giới hạn
Suite pipeline gồm golden cases và test chạy câu thật; không còn bốn skip ở mốc cũ. Test audit kiểm --grammar với default CFG bị hỏng và bảo toàn source khi xuất grammar. `python src/run.py all` xử lý 73 câu, tạo 1.000 sample/9 output; đóng gói giải nén và chạy từ cwd khác kiểm đường dẫn và so byte.

Việc ghi all chưa có transaction: lỗi giữa chừng có thể để lại vài file mới và vài file cũ, nên chỉ dùng output của lần all kết thúc thành công. Docker chưa kiểm chứng theo yêu cầu tạm hoãn của người dùng; không lấy chạy native để đánh dấu T21 hoàn tất.
