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
- Chưa phát hiện câu mơ hồ trong corpus đã kiểm. Nếu có nhiều cây, parser phải chọn cây
  một cách xác định (deterministic).
- Lý thuyết: `docs/knowledge/04-parser.md`.

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu cây golden; bổ sung nullable completion khi trạng thái chờ xuất hiện muộn, parse_trees(limit=2), kiểm thử epsilon/left recursion/ambiguity và trailing token.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Thành phần và kiểu dữ liệu
[`grammar.py`](../../../src/hcmut/iaslab/nlp/app/grammar.py) chứa `Rule(lhs, rhs)` bất biến và `Grammar` với tuple rules, index `by_lhs`, tập nonterminals và source_text. [`tree.py`](../../../src/hcmut/iaslab/nlp/app/tree.py) chứa Tree bất biến; [`parser.py`](../../../src/hcmut/iaslab/nlp/app/parser.py) trả `ParseResult(sentence, tokens, tree)`.

### Grammar loader
`from_file` đọc UTF-8 rồi chuyển cho `from_text`. Loader bỏ dòng trống/comment, nhận một `%start`, tách lhs/rhs ở `->`, tách alternative `|` chỉ khi ngoài ngoặc kép và xử lý escape terminal bằng JSON. Alternative rỗng tạo rhs rỗng. Lhs và symbol không có ngoặc kép phải là non-terminal chữ hoa; cuối cùng kiểm start tồn tại và mọi tham chiếu non-terminal đã định nghĩa.

Trong đợt rà soát, `S -> missing_symbol` từng bị nhận nhầm thành terminal dù chưa có ngoặc kép. Loader nay báo GrammarError kèm số dòng. Terminal của grammar ứng dụng phải chữ thường và khớp một token; T19 kiểm thêm các điều kiện này, định nghĩa lặp và node không tới được. Rule/Grammar hiện biểu diễn symbol bằng str; không xem đây là parser cho mọi biến thể DSL CFG.

### Earley và dựng cây
Mỗi câu có chart ở n+1 vị trí. State gồm production, dot, origin và tuple con đã dựng. Predictor thêm luật khi symbol kế tiếp là non-terminal; scanner khớp terminal và tiến một token; completer dựng Tree rồi nối vào state đang chờ tại origin. Luật gốc tổng hợp `@START -> S` chỉ nhận nếu hoàn tất ở vị trí n, origin 0 và leaves khớp toàn bộ token.

State rỗng hoàn tất ngay tại cùng vị trí tạo node không con. Chỉ mục nullable theo vị trí/nhãn cho phép một waiting state xuất hiện muộn vẫn lấy node ε đã hoàn tất trước đó. Agenda và thứ tự production quyết định cây đầu tiên, tránh chọn ngẫu nhiên.

`parse` dùng limit=1. `parse_trees(limit=2)` giữ tối đa hai dẫn xuất cho mỗi chart item `(rule, dot, origin)` để phát hiện nhiều cây và chặn chu trình nullable. Đây là tìm cây có giới hạn, không phải parse forest hay phép đếm tất cả dẫn xuất; không khẳng định tính không mơ hồ của toàn bộ CFG.

### Lỗi, nghiệm thu và đầu ra
Câu không nhận trả tree=None và in `()`. Tree ε in `(PREFIX ε)`; semantic đọc nhãn node, không parse lại chuỗi bracketed. Test parser golden có 2.077 câu; hồi quy riêng kiểm left recursion, `A A` nullable, hai cây cho cùng câu, chu trình rỗng, trailing token và symbol bare sai dạng. T16 ghi mỗi cây một dòng theo thứ tự input.

**Giới hạn:** state chứa Tree và thực hiện copy/hash cấu trúc; chưa tối ưu packed forest cho câu dài. Cây đầu tiên xác định được không có nghĩa đó là cách hiểu đúng khi grammar được mở rộng thành mơ hồ.
