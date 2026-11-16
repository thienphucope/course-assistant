# Kịch bản video demo và thuyết trình

## Video ngắn khoảng 3–4 phút

Chạy từ gốc repo: `python tools/demo.py`. Mỗi ví dụ dùng kết quả runtime thật;
`docs/demo-transcript.txt` là bản trace để đối chiếu, không thay thế video nộp.
Khi quay, tăng cỡ chữ terminal để đọc được câu hỏi/semantic/answer. Có thể chạy
từng câu bằng `python src/run.py answer "..." --trace`.

| Thời gian | Thao tác/cảnh | Lời giải thích |
| --- | --- | --- |
| 0:00–0:20 | Tên môn, đề tài, thành viên. | Nhóm chọn Classical NLP, dùng CFG và KB môn học; runtime offline. Điền tên/MSSV trước khi quay. |
| 0:20–0:55 | Nhập `Môn NLP có bao nhiêu tín chỉ?` với `--trace`. | Chỉ token/cây, `Q_COURSE_CREDITS`, semantic, query, nguồn course_info và đáp án 3 tín chỉ. |
| 0:55–1:35 | Trong một phiên, nhập `Tuần 3 học gì?`, tiếp `Nó có liên quan đến parsing không?`. | Câu đầu lưu CH03; câu sau có frame CONTEXT_DEPENDENT, resolver lấy CH03 rồi query quan hệ. Chỉ rõ frame trước/sau. |
| 1:35–2:00 | `BTL có phần parse tree không?`. | Cây có FEAT_PARSING; semantic dùng nhãn để xác định PART_I. |
| 2:00–2:25 | `Ai dạy NLP?`, sau đó câu hỏi thời tiết. | Câu đầu có cây nhưng KB thiếu, trả thông báo của đề. Câu sau có `()`, UNKNOWN và không tra dữ kiện. |
| 2:25–3:00 | `python src/run.py all`; mở danh sách output và evaluation. | Đủ 9 file, câu mẫu 42/42, challenge 20/22, hội thoại 6/6. Đây là các bộ đã dùng khi phát triển. |
| 3:00–3:30 | Mở hai dòng FAIL C007/C008 và README. | Grammar chưa nhận số buổi/tuần và tuần dạng chữ. Nêu kế hoạch bổ sung luật có hồi quy. |
| 3:30–3:50 | Nếu có Docker: build rồi run, xem output volume. | Container chạy cùng pipeline. Chỉ trình bày kiểm chứng này sau khi đã chạy thật. |

Lệnh giữ chung phiên trong cảnh ngữ cảnh:

```bash
python src/run.py answer "Tuần 3 học gì?" "Nó có liên quan đến parsing không?" --trace
```

Nếu quay phần tương tác, dùng `python src/run.py interactive`, kết thúc bằng `/quit`.
Không chạy hai lệnh `answer` riêng rồi nói rằng chúng dùng chung bộ nhớ.

## Thuyết trình 5–10 phút

Phân vai dưới đây là đề xuất theo nội dung; nhóm điền người phụ trách thực tế.

| Khoảng thời gian | Nội dung | Người trình bày |
| --- | --- | --- |
| 0:00–1:00 | Phạm vi đề, KB, lựa chọn Classical, luồng dữ liệu. | Chờ nhóm điền |
| 1:00–3:00 | CFG 26 nhánh, tokenizer, Earley và xử lý ε; chỉ một cây thật. | Chờ nhóm điền |
| 3:00–4:30 | Từ cây sang frame, FEAT, entity, query có nguồn, fallback. | Chờ nhóm điền |
| 4:30–5:30 | Resolver theo loại, reset và ca không có ngữ cảnh. | Chờ nhóm điền |
| 5:30–7:30 | Demo, chỉ số, ca sai, giới hạn; Docker/gói nộp nếu đã kiểm. | Chờ nhóm điền |
| 7:30–8:00 | Nguồn tham khảo, AI và hướng mở rộng. | Chờ nhóm điền |

## Câu hỏi cần tự giải thích được

- Predictor/scanner/completer khác nhau thế nào? Vì sao phải xử lý node nullable đã hoàn tất trước trạng thái chờ?
- Vì sao `Tuần 3 học gì? xyz` phải bị từ chối? Cây ε được lưu thế nào?
- Nhánh `Q_*` và node `WEEK_ENTITY` giúp semantic tránh đọc lại câu gốc ra sao?
- FEAT_PARSING xác định PART_I thế nào? Thêm alias ở đâu và kiểm lại bằng gì?
- Phân biệt UNKNOWN, thiếu context và NOT_FOUND. Vì sao `Ai dạy NLP?` không trả tên người?
- Vì sao không cập nhật context khi query thất bại? Một câu hỏi phần BTL có làm mất chương đang nhớ không?
- Tỷ lệ 96,88% tính trên bao nhiêu câu? Vì sao không xem đó là độ chính xác trên câu hỏi mới?
- Cách xác nhận đủ 9 output và chạy được sau giải nén? Bước Docker nào đã thực hiện thật?

## Trạng thái chuẩn bị

Đã có video tự động `dist/course-assistant-demo.mp4` (2 phút 8 giây, 1280×720,
có phụ đề, không có tiếng), gói kiểm tra chứa `project/demo.mp4`. Video phát lại
trace thực thi của 7 câu, có cây/semantic/query/answer, ngữ cảnh, ca thiếu KB và
ngoài miền. Bản này có thể dùng để duyệt nội dung trước khi quay/thuyết minh.

Tạo lại bằng `python tools/render_demo.py`; công cụ phát triển cần Pillow và
ffmpeg, font Segoe UI/Consolas trên Windows. Trên hệ khác dùng `--font` và
`--mono-font` trỏ tới font hỗ trợ tiếng Việt. Runtime Course Assistant vẫn chỉ
cần thư viện chuẩn. Còn thông tin thành viên, phân vai và quyết định bản video nộp.
