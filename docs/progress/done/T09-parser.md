# T09 · ⚙️ Grammar loader + Parser (Phần I)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/grammar.py` (`Grammar.from_file`), `parser.py`
  (`EarleyParser.parse`); `tree.py` đã có sẵn
- **Output:** `src/output/parse-results.txt` (ghi file ở T16)
- **Test:** `src/tests/test_parser_generator.py`
- **Nghiệm thu:** `tests.test_contract_parser` pass — cả `test_grammar_has_the_26_question_branches`
  lẫn `test_trees_match_golden` (hợp đồng: `docs/contracts.md` §2)

Cần trước: T08 (tokenizer).

## Việc cần làm
- [x] Hàm cần viết: `Grammar.from_file`, `Grammar.from_text`, `EarleyParser.parse`.
- [x] Test mẫu `src/tests/test_parser_generator.py`: thay 2 `skipTest` TODO (parse phải ăn hết token; ca round-trip cần thêm T10 generator).
- [x] Grammar loader: đọc `%start`, `->`, `|`, alternative rỗng = ε, terminal trong ngoặc kép;
      báo lỗi non-terminal chưa định nghĩa.
- [x] Đi ngược câu → cây (Earley hoặc backtracking), dựng cây có nhãn để semantic đọc nhánh `Q_*`;
      ký hiệu sinh rỗng vẫn là một node không con.
- [x] Câu ngoài grammar → không có cây (in `()`).

## Ghi chú
- Grammar hiện tại không có câu mơ hồ (đã kiểm phase 1). Nếu sau này có, parser phải chọn cây
  một cách xác định (deterministic).
- Lý thuyết: `docs/knowledge/04-parser.md`.

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu cây golden; bổ sung nullable completion khi trạng thái chờ xuất hiện muộn, parse_trees(limit=2), kiểm thử epsilon/left recursion/ambiguity và trailing token.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
