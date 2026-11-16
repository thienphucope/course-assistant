# Đối chiếu thiết kế T01–T19 và rà bug

Mốc nền: `9096375`, sau khi fast-forward nhánh hoàn thiện vào `dev`.
Nhánh làm đợt rà soát: `chore/document-design-and-audit`.

## Tài liệu đã bổ sung

19/19 ticket trong `docs/progress/done/` có mục **Thiết kế triển khai hiện tại**.
Mỗi mục chỉ rõ file/API, dữ liệu qua tầng, thuật toán/luồng xử lý, quyết định,
lỗi và giới hạn, test/lệnh đối chiếu. Đã kiểm các link local trong ticket, không
có link hỏng. Các phần review phase 1 và số liệu cũ giữ làm lịch sử, không dùng
chúng để mô tả tình trạng hiện tại.

Các thông tin sửa lại gồm: KB nạp lúc khởi tạo; helper chuẩn hóa riêng ở entity
và query; marker khám phá project là run.py + data/grammar.cfg; tên renderer
dialogue; test pipeline đã triển khai; T12/T13 đã tích hợp ở `95df6db`; vị trí
archive gốc ở `docs/materials/`; phạm vi thực tế của kiểm không mơ hồ và score
dialogue. T07 ghi rõ quyết định giữ golden KB so khớp tuyệt đối.

## Bug và ca biên đã sửa

| Ticket | Trước khi sửa | Sau khi sửa / kiểm chứng |
| --- | --- | --- |
| T09 | Bare symbol `missing_symbol` bị coi là terminal dù thiếu ngoặc kép. | GrammarError có số dòng; yêu cầu bare non-terminal chữ hoa. |
| T10 | Đếm terminal không chặn form tăng mãi với `S -> S S`, kể cả nullable. | Tính min_yield, loại nonproductive, giới hạn chiều dài form; hai ca tăng trưởng kết thúc dưới 100 form. |
| T13 | GET_RESOURCE thiếu topic khớp chuỗi rỗng với mọi title. | found=False và đúng NOT_FOUND. |
| T13 | CH99 vẫn nhận danh sách tài liệu nền. | Kiểm chương có trong KB trước khi gợi ý. |
| T13 | Assignment/deadline có ID OTHER vẫn trả dữ kiện BTL01. | Guard đối tượng theo slot assignment; không trả fact của BTL khác. |
| T15 | Sau CH04 → LO2.5 → chương của LO, câu quan hệ tiếp theo vẫn dùng CH04. | LO_CHAPTER cập nhật last_chapter=CH06; giữ cache LO và source_branch. |
| T15 | history_limit=0 lại giữ danh sách tăng dần vì slice `[:-0]`. | Giới hạn không dương không lưu history, cache có kiểu vẫn hoạt động. |
| T16 | Xuất grammar dùng rstrip, mất dòng trống cuối source. | Ghi nguyên source_text, UTF-8/LF. |
| T16/T19 | --grammar hợp lệ vẫn lỗi nếu grammar mặc định trong root đang hỏng. | Assembler nhận CFG đã nạp, checker dùng đúng bản được chọn. |
| T17 | Parse nhận câu ngoài miền nhưng semantic UNKNOWN vẫn có thể được chấm đúng. | End-to-end kiểm cả trạng thái parse; diagnosis chỉ ra false acceptance. |
| T17 | Có required terms thì bỏ qua kiểm category fallback. | Kiểm fallback đúng loại trước, sau đó mới kiểm các fact. |
| T17 | Case hỏng/trùng ID/status lạ và dialogue thiếu reference có thể biến mất khỏi mẫu số. | Loader báo ValueError; không âm thầm giảm số lượng để chấm. |
| T19 | Challenge bị hồi quy vẫn in PASS/exit 0. | Chỉ C007/C008 là giới hạn đã biết; các ca khác fail làm exit 1. |

14 test mới trong `src/tests/test_audit_regressions.py` kiểm các phản ví dụ này.
Nhóm 10 test đầu đã chạy trên code trước sửa và thất bại; các ca xuất grammar,
CFG được chọn và tăng trưởng generator có test độc lập bổ sung. Ca generator
không productive được kiểm sau khi có guard để tránh chạy bản có thể tăng bộ nhớ.

## Nghiệm thu

- `python -m unittest discover -s src/tests -t src`: **47 test đạt, không skip**.
- Sinh lại golden bằng `python tools/make_golden.py`: nội dung fixture không đổi;
  vẫn 2.077 tokenizer/parser, 2.034 semantic, 205 query/answer, 64 cases, 6 dialogue.
- `python tools/check_grammar.py --samples 1000 --json docs/validation/design-audit-grammar.json`:
  42/42 official, 20/22 challenge, 6/6 dialogue, 1.000 sample, 26 nhánh.
  Không phát hiện hai cây trong 1.047 chuỗi đã kiểm; không phải chứng minh CFG không mơ hồ.
- Đối chiếu sáu file KB với archive gốc, bỏ khác biệt newline/dòng trống cuối:
  giữ nguyên nội dung fact.
- `python tools/package_submission.py --output dist/design-audit-review.zip`:
  gói 528.882 byte; giải nén sang thư mục mới, chạy từ cwd khác, cả 9 output
  khớp source theo byte. Checksum/kết quả lưu ở `design-audit-artifacts.json`.

Kết quả query missing-fact/context trong JSON vẫn có fallback có chủ đích.
C018 là lỗi found/fallback đã sửa so với baseline; output improvement targets
`1/3 fixed` gồm C018 đã đạt, C007/C008 còn ngoài grammar. Challenge tổng là 20/22.

## Phạm vi còn lại

Đây là rà soát implementation và ticket hiện tại, không phải chứng minh không còn
bug. Grammar đóng, tìm tài liệu dựa từ khóa, cache tham chiếu theo loại và phép
chấm dialogue ở lượt cuối vẫn là giới hạn thiết kế đã ghi trong ticket.
Chưa mở rộng C007/C008 hay thêm fact KB. Docker tạm hoãn theo yêu cầu người dùng;
không cài Docker hoặc đổi trạng thái T21 trong đợt này.

Các record nghiệm thu cũ trong `docs/validation/README.md` và `artifacts.json`
thuộc snapshot trước đợt rà soát. Không diễn giải checksum cũ là checksum gói mới.
