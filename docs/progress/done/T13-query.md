# T13 · 🔧 Query builder (Phần II)

- **Trạng thái:** xong (đã tích hợp ở `95df6db`)
- **Phụ trách:** Nguyễn Huy Bách
- **Code:** `src/hcmut/iaslab/nlp/app/query.py` (`QueryEngine.execute`)
- **Output:** `src/output/query.txt`

- **Nghiệm thu:** `tests.test_contract_query` pass (hợp đồng: `docs/contracts.md` §5 — bảng
  `kind` / `data` / `sources`). Test dùng frame + KB golden nên **không phải chờ** semantic hay KB
  loader; chạy end-to-end mới cần hai task đó.

## Việc cần làm
- [x] Hàm cần viết: `QueryEngine.execute` (một nhánh cho mỗi intent).
- [x] Predicate → truy vấn KB theo intent, **không đọc lại câu hỏi gốc**.
- [x] Trả `QueryResult` có `found`, dữ kiện và nguồn (`kb/<file>.txt`).
- [x] `found = False` khi dữ kiện rỗng — ví dụ output của Phần II/III/IV không có trong KB (bug
      của sample, golden đã sửa; xem §5).

## Ghi chú
- Lý thuyết: `docs/knowledge/06-query-kb-answer.md`.

## Kết quả triển khai

- Ngày hoàn thành: 01/11/2026.
- Commit triển khai: `95df6db` (T12/T13).
- Tham khảo code nhánh đóng băng `sample`; giữ hợp đồng và golden hiện hành.
- 192/192 frame khớp golden, kể cả khi dùng KB đọc từ file thật; query không thay đổi KB.
- Sửa trường hợp section tồn tại nhưng không có output: `found=False`, giữ nguồn assignments theo golden.
- Kiểm tra T12/T13: 14 test đạt, không skip. Toàn bộ suite: 28 test, 16 đạt, 12 skip ở các task khác, không lỗi.

## Thiết kế triển khai hiện tại

### API và nguyên tắc
[`QueryEngine(kb).execute(frame)`](../../../src/hcmut/iaslab/nlp/app/query.py) dispatch theo frame.intent, dùng **slots** để truy vấn; frame.entity là tiêu điểm đi kèm, không thay slot bắt buộc. Không nhận câu gốc, không parse predicate, không đọc lại file KB. Trả QueryResult(query, found, kind, data, sources, reason). Query/reason là trace tự do, schema dữ kiện theo hợp đồng.

### Chiến lược theo nhóm
- Course: field credits/parts/description/assessment/exam duration lookup trong course; course khác CO3085 không tìm thấy. Ngày thi và giảng viên không có trong KB.
- Schedule: tra week, chapter_weeks, hoặc tìm tuần chứa đồng thời các topic; so từ khóa theo nguyên cụm và chuẩn hóa dấu gạch.
- Topic: tra chapter; topic search ưu tiên keyword_list khớp hoàn toàn (10) hơn nội dung nguyên cụm (2), trả các chương đồng hạng theo số chương. Quan hệ false vẫn found=True vì biết được kết luận âm. LO_CHAPTER dùng bảng LO_CHAPTER và record chương.
- Assignment: overview/section/output. Section tồn tại nhưng thiếu suggested_outputs vẫn found=False; giữ nguồn assignments để giải thích. Deadline lấy các milestone trong schedule của BTL hiện tại.
- Resource: chấm điểm mỗi term theo title (3) hoặc usage (1), giữ các record có điểm cao nhất và thứ tự nguồn. Với chương hợp lệ, trả một nhóm tài liệu NLP nền tảng; KB chưa có liên kết tài liệu–chương chi tiết.
- Rule: ID chuẩn → key trong regulations. UNKNOWN và context chưa giải đều NO_QUERY nhưng kind/fallback khác nhau.

### Các guard được bổ sung khi rà bug
Thiếu topic resource từng tạo chuỗi rỗng, khớp mọi title và trả toàn bộ sách; nay trả found=False. CH99 không tồn tại không được dùng nhánh gợi ý tài liệu nền. Assignment/deadline có slot assignment khác BTL01 nay trả không tìm thấy, thay vì lấy dữ kiện BTL01 cho đối tượng khác. Nếu slot assignment bị bỏ, API vẫn giữ mặc định BTL01 của miền hiện tại; không suy ra ID khác từ câu gốc.

Ví dụ GET_RESOURCE() → RESOURCE/found=False → NOT_FOUND; GET_ASSIGNMENT(assignment=OTHER, section=OVERVIEW) không trả overview của BTL01. Những frame này không có trong golden thông thường nên cần counterexample riêng.

### Hợp đồng và nghiệm thu
Found không đồng nghĩa câu trả lời có sắc thái 'có': TOPIC_RELATION related=False vẫn là fact tìm thấy. Ngược lại, không có dữ kiện để render phải found=False. Sources là file dữ kiện, có thể giữ nguồn khi missing output; không giả định mọi result thất bại luôn sources rỗng.

`test_contract_query` so 205 frame với KB golden; `tests.test_query` chạy lại với KB đọc file thật và kiểm không mutation. Các test audit missing_resource_topic, unknown_chapter, other_assignment bảo vệ guard mới. Giới hạn còn lại là tìm topic/resource dựa từ khóa và bảng LO–chương tĩnh, không bảo đảm truy xuất đúng cho mọi nội dung KB mới.
