# T08 · ⚙️ Tokenizer

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/tokenizer.py`
- **Nghiệm thu:** `tests.test_contract_tokenizer` pass (hợp đồng: `docs/contracts.md` §1)

Tầng đầu tiên: parser (T09), entity lexicon (T11) và query (T13) đều gọi tokenizer.

## Việc cần làm
- [x] Hàm cần viết: `normalize_text`, `tokenize`, `normalized_phrase`, `detokenize`.
- [x] `normalize_text` + `tokenize` khớp với terminal trong `src/data/grammar.cfg`: lowercase,
      Unicode NFC, giữ dấu tiếng Việt, giữ `context-free`, `llm/rag`, `lo2.5` là **1 token**,
      tách dấu câu `? ! . , : ;`, bỏ ngoặc kép, chuẩn hoá `L.O.2.5` → `lo2.5`.
- [x] `normalized_phrase`: chuẩn hoá cụm entity để tra lexicon (bỏ dấu câu).
- [x] `detokenize`: ghép token thành câu đọc được (dùng cho `samples.txt`).

## Ghi chú
- Grammar phase 1 được kiểm bằng tokenizer của nhánh `sample`. Đổi quy tắc tách token thì phải
  kiểm lại grammar (bài học PR #2: `"context" "-" "free"` → 232 câu không parse lại được).

## Kết quả nghiệm thu 2026-11-16

Code đã có từ b104437; nghiệm thu lại tokenizer golden trong toàn bộ suite, không còn test tầng bị skip.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
