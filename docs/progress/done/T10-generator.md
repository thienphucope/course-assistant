# T10 · ⚙️ Generator (Phần I)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/generator.py`
- **Output:** danh sách câu cho `src/output/samples.txt` (ghi file ở T16)
- **Nghiệm thu:** mọi câu sinh ra parse lại được bằng parser của nhóm; ≤ 10 000 câu; đủ 26 nhánh
  (cách sinh là phần lỏng — `docs/contracts.md`)

## Việc cần làm
- [x] Hàm cần viết: `SentenceGenerator.generate`.
- [x] Sinh câu hợp lệ từ grammar, **≤ 10 000 câu**, chia đều giữa các nhánh `Q_*`.
- [x] Mọi câu sinh ra phải parse lại được và không lộ tên non-terminal.
- [x] Trả `GeneratorStats` (requested / produced / explored_forms / truncated) cho T16;
      `samples.txt` chỉ chứa câu, không ghi thêm thống kê.

## Ghi chú
- Lý thuyết: `docs/knowledge/07-generator.md`.

## Kết quả nghiệm thu 2026-11-16

Sinh 1.000 câu duy nhất, có chữ hoa đầu và dấu ?, phân bổ 38–39 câu/nhánh cho đủ 26 nhánh. CLI parse lại trước khi ghi. Tôn trọng giới hạn 10.000 câu.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### API và mục tiêu
[`SentenceGenerator.generate`](../../../src/hcmut/iaslab/nlp/app/generator.py) nhận limit và max_tokens, trả `(list[str], GeneratorStats)`. limit âm hoặc max_tokens dưới 1 báo ValueError; limit=0 trả rỗng; request lớn hơn 10.000 được chặn ở trần 10.000 nhưng stats.requested giữ số xin ban đầu. Không bảo đảm sinh đủ limit khi grammar/quota/budget không cho phép.

### Chiến lược sinh
Lấy các nhánh Q từ production của QUESTION, sắp theo tên để ổn định thứ tự. Với start rule chứa QUESTION, mỗi seed thay nó bằng nhánh cụ thể; CFG không có wrapper này dùng seed start. Mỗi seed có deque và tập form đã thăm. Một vòng lấy một form của từng seed, mở rộng non-terminal trái nhất theo thứ tự luật. Quota chia bằng divmod nên request 1.000 phân bổ 38–39 câu mỗi nhánh khi có đủ câu.

Câu terminal qua detokenize, viết hoa đầu; với wrapper SUFFIX hỗ trợ câu hỏi thường/lịch sự, chuẩn hóa đuôi `?` và một số acronym. Set unique loại câu trùng sau định dạng. Chỉ nhận câu có số token không vượt max_tokens. Generator không tra KB: câu hỏi về tuần 99 hay ngữ cảnh đứng riêng vẫn có thể đúng grammar.

### Chặn tăng trưởng và lỗi đã sửa
Ngưỡng thăm là 250.000 form. Việc chỉ đếm terminal trước đây không chặn `S -> S S`: form có thể dài dần dù chưa có terminal. Code hiện tính min_yield bằng fixed point, loại non-terminal không sinh được terminal, và giới hạn chiều dài form trung gian bằng max_tokens + số nonterminal + rhs dài nhất. Từ đó grammar không sinh được câu hoặc tăng trưởng nullable dừng thay vì tích lũy form không hữu ích.

Không chạy lại một BFS fallback thứ hai khi generic seed đã được duyệt. Các giới hạn là chính sách an toàn/sampling, có thể bỏ dẫn xuất của CFG lớn; không phải thuật toán liệt kê đầy đủ ngôn ngữ. Quota của nhánh ít câu không được chia lại sang nhánh khác.

### Thống kê và nghiệm thu
GeneratorStats có requested, produced, explored_forms, truncated. explored_forms đếm form đã lấy khỏi queue, không đếm số câu; truncated cho biết có cắt theo quota/giới hạn trong quá trình sinh. T16 ghi samples mỗi dòng một câu; không serialize stats vào samples.txt.

CLI parse lại toàn bộ câu sinh trước khi ghi. `test_valid_question_round_trips` kiểm 260 câu duy nhất, đủ 26 nhánh, quota chênh tối đa 1 và leaves bằng token. T19 kiểm 1.000 câu; `test_generation_terminates_for_nonproductive_and_nullable_growth` kiểm hai grammar tăng trưởng không terminal. Đủ 26 nhánh chỉ có ý nghĩa khi limit/budget đủ lớn, không yêu cầu limit=1 cũng phủ mọi nhánh.
