# T19 · 🔧 Script kiểm tra grammar dùng chung

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **File:** `tools/check_grammar.py`

Hai lỗi nặng nhất phase 1 (#3 crash, #2 lệch tokenizer) script này bắt được ngay. Mỗi người chạy
trước khi mở PR.

## Việc cần làm
- [x] Load grammar bằng code chuẩn của nhóm; báo non-terminal chưa định nghĩa / không dùng tới /
      định nghĩa 2 lần / terminal viết hoa; đếm đủ 26 nhánh.
- [x] Chạy câu mẫu, câu thách thức và hội thoại; in câu rớt theo nhánh.
- [x] Sinh câu → parse lại; tìm tối đa 2 cây để phát hiện mơ hồ, không đếm mọi dẫn xuất.
- [x] Chạy cả pipeline trên câu sinh ra: intent ≠ UNKNOWN; entity có ID (trừ frame ngữ cảnh); query tìm thấy hoặc fallback có nguyên nhân rõ.

## Ghi chú
- Các bước gộp phase 1 được lưu ở `T03-grammar-phase1.md`, mục "Cách kiểm tra". Công cụ
  hiện tại chạy implementation của nhóm; baseline sample dùng riêng ở T06.
- `tools/make_golden.py` đã có sẵn phần lấy code `sample` qua `git archive` và chạy trên
  `src/data/` — dùng lại cách đó. Sau khi đổi grammar, chạy lại nó rồi chạy test hợp đồng.

## Kết quả nghiệm thu 2026-11-16

Đã thêm tools/check_grammar.py: kiểm cấu trúc, token, suite, hội thoại, 26 nhánh sinh, ambiguity và pipeline. Ca thiếu KB/ngữ cảnh có chủ đích được báo riêng; --strict-kb yêu cầu toàn bộ query tìm thấy. Không coi các fallback đúng là lỗi grammar. Bằng chứng: docs/validation/grammar-check.json.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Mục tiêu và đầu vào
[`tools/check_grammar.py`](../../../tools/check_grammar.py) là CLI kiểm hồi quy từ gốc repo hoặc cwd khác. --root mặc định src/, --grammar chọn CFG khác, --samples từ 26 đến 10.000 để yêu cầu phủ nhánh, --json lưu báo cáo, --strict-kb yêu cầu mọi query sinh phải tìm thấy.

### Kiểm cấu trúc trước khi chạy
Grammar loader kiểm cú pháp/start/tham chiếu; structural_errors kiểm một định nghĩa lhs mỗi dòng, rule lặp, nonterminal không tới được, terminal chữ hoa hoặc lệch tokenizer và đúng tập 26 nhánh trong BRANCH_INTENTS. Loader có thể gom nhiều production cùng lhs nhưng linter chọn quy ước một dòng/nhãn để tránh trùng định nghĩa khi gộp nhóm.

### Kiểm hành vi
Khởi tạo CourseAssistant với CFG đã nạp bằng from_paths(..., grammar=grammar), không nạp default CFG trước rồi thay parser. Đây là sửa lỗi --grammar: bản CFG sửa đúng vẫn phải được kiểm khi root/data/grammar.cfg đang hỏng. KB/scaffolding lấy từ root được chọn.

Official/challenge chạy theo thứ tự và reset trước mỗi bộ; dialogue reset mỗi phiên. Official thất bại làm exit 1. Challenge chỉ chấp nhận hai giới hạn đã ghi C007/C008; ca khác rớt là regression và phải exit 1. Trước đợt audit, script chỉ in challenge fail rồi vẫn PASS; test thay alias dịch máy chứng minh C013 mất hỗ trợ phải bị chặn.

Với câu sinh, reset state mỗi câu, kiểm parse, intent, entity (cho phép None với CONTEXT_DEPENDENT), found/fallback không mâu thuẫn và đủ nhánh. Các query thiếu KB/context được ghi kind/reason riêng; không ép chúng thành fact. --strict-kb cố ý có thể fail trên grammar hiện tại vì grammar chứa câu tuần/chương không có trong KB và đại từ cần context.

### Ambiguity, output và exit code
Set checked tránh kiểm lại cùng chuỗi câu; parse_trees(limit=2) tìm bằng chứng có ít nhất hai cây. Báo cáo JSON có rule/branch count, suite failures, dialogue score, GeneratorStats, coverage từng nhánh, query_statuses, missing_facts_or_context, ambiguous và errors. PASS/exit 0 nghĩa các điều kiện nghiệm thu đã nêu đạt; không nghĩa challenge 22/22 hay mọi query found.

Lỗi nạp/cấu trúc dừng sớm; không hứa lúc nào cũng ghi được JSON nếu chưa khởi tạo pipeline. Không dùng script như chứng minh CFG không mơ hồ hoặc exhaustive semantic test. T06 và các test counterexample vẫn cần để phát hiện sai logic không xuất hiện trong samples.

### Lệnh nghiệm thu và hồi quy
`python tools/check_grammar.py --samples 1000 --json docs/validation/design-audit-grammar.json`: 42/42, 20/22, 6/6, 1.000/1.000, 26/26 nhánh, 0 mơ hồ trên 1.047 chuỗi. Hai test audit chạy subprocess kiểm C013 regression và --grammar với default bị hỏng; chúng kiểm exit code thật, không chỉ nhìn chữ PASS in ra.
