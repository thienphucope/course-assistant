# T08 · ⚙️ Tokenizer

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/tokenizer.py`
- **Nghiệm thu:** `tests.test_contract_tokenizer` pass (hợp đồng: `docs/contracts.md` §1)

Parser (T09) gọi tokenizer, generator (T10) dùng detokenize, evaluator (T17) dùng normalize_text.
Entity lexicon (T11) và query (T13) hiện có helper chuẩn hóa riêng.

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
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### API và file chịu trách nhiệm
[`tokenizer.py`](../../../src/hcmut/iaslab/nlp/app/tokenizer.py) cung cấp bốn hàm thuần, không đọc file, không giữ state. Parser gọi `tokenize`; generator gọi `detokenize`; evaluator dùng `normalize_text`. Entity lexicon hiện có helper chuẩn hóa riêng và query có `_normalize_search_text`; đây là các helper riêng của từng tầng trong implementation hiện tại.

### Luồng chuẩn hóa
1. `normalize_text(text)` yêu cầu str, đưa về Unicode NFC và chữ thường, thay dạng `l.o.2.5` bằng `lo2.5`, gộp khoảng trắng.
2. `tokenize(text)` lấy các match của regex: mã LO, từ ghép nối bằng `- / .`, từ/số và sáu dấu câu `? ! . , : ;`. `context-free`, `llm/rag`, `lo2.5`, `tp.hcm` giữ thành một token.
3. `normalized_phrase` bỏ các token dấu câu để tạo khóa so alias.
4. `detokenize` ghép từ bằng khoảng trắng, ghép dấu câu sát từ trước. Hàm này không tự viết hoa hay tự thêm `?`; hình thức câu hỏi là việc T10.

### Hợp đồng và ví dụ
`“NLP” có mấy tín chỉ?` tạo `['nlp', 'có', 'mấy', 'tín', 'chỉ', '?']`; dấu ngoặc kép không thành token. `L.O.2.5 là gì?` có token đầu `lo2.5`. Parser phải tiêu thụ hết **chuỗi token đã chuẩn hóa**, không phải kiểm từng ký tự của câu gốc.

### Đối chiếu và nghiệm thu
`tests.test_contract_tokenizer` so 2.077 câu với golden. `tests.test_parser_generator` kiểm round-trip và đuôi token lạ; T19 kiểm terminal grammar khớp tokenizer. Thay regex có thể làm thay đổi cả parser, alias và evaluation nên phải xem lại hợp đồng/golden cùng grammar.

**Giới hạn:** regex lấy token nhận được và bỏ ký tự không thuộc mẫu; không dùng nó như bộ kiểm tra mọi ký tự lạ. Giữ `chữ.chữ` giúp nhận viết tắt nhưng cũng giữ lỗi gõ dính dấu chấm. Alias mới có quy tắc dấu câu khác cần test riêng, không mặc định rằng mọi Unicode dash hay cách viết tắt đều tương đương.
