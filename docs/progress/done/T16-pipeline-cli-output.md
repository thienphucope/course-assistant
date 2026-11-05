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

- [x] `ProjectPaths.discover()` — đi ngược từ vị trí file tìm thư mục có `pyproject.toml` + `data/`,
      không phụ thuộc cwd; thêm `PATHS`. `source` giữ theo skeleton (= root, vì `src/` là root).
- [x] `CourseAssistant.from_paths`: load grammar, lexicon (`entities.txt`), KB (+ `validate()`,
      lỗi thì `ValueError`), dựng `PipelineComponents`. Thêm property `grammar`, `parser` cho CLI.
- [x] `cli.py`: lệnh `all`, `parse`, `answer` (`--trace`), `generate`, `evaluate`, `interactive`.
- [x] Reader `input/sentences.txt` (bỏ dòng trống và `#`), chạy theo thứ tự, giữ ngữ cảnh.
- [x] `output.py`: `write_grammar`, `write_samples` (≤ 10 000), `write_pipeline_outputs`; cùng
      `dialogue.txt`, `evaluation.txt` — định dạng theo `docs/contracts.md` §9.
- [ ] `src/tests/test_pipeline.py` vẫn là test khung (`skipTest` TODO) — chưa viết end-to-end
      `sample_queries.txt`; việc này được `test_contract_pipeline` phủ phần nào.

## Kết quả

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
