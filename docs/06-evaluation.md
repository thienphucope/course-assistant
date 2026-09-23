# Mốc 6 — Đánh giá hệ thống

Đề yêu cầu cho biết hệ thống đúng bao nhiêu, sai ở đâu và vì sao. `evaluate.py` chạy từng câu qua toàn bộ pipeline rồi so kết quả với nhãn đã chuẩn bị trước; nó không dùng đáp án vừa được máy tạo ra làm nhãn chuẩn.

## Chạy

Từ `src/`:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py evaluate
```

Lệnh ghi `output/evaluation.txt`. `run.py batch` cũng tái tạo file này cùng các đầu ra Phần I–II. `evaluate --strict` trả exit code 1 nếu có ca sai để dùng làm cổng kiểm thử; lệnh `evaluate` thông thường trả 0 khi việc đánh giá chạy thành công, dù điểm không đạt 100%.

## Hai bộ câu và nhãn

`data/scaffolding/sample_queries.txt` là 34 câu tham chiếu có bốn cột; Q029–Q034 là ví dụ hội thoại tùy chọn. Không trộn chúng vào điểm câu đơn. `gold_queries.txt` giữ 28 câu đơn Q001–Q028 và thêm hai cột: trạng thái KB kỳ vọng (`FOUND`, `NOT_FOUND`, `OUT_OF_SCOPE`) và các mảnh câu trả lời cần có, ngăn bằng `;;`. `challenge_queries.txt` là 13 ca nhóm tự viết: cách diễn đạt khác, câu gần đúng nhưng sai, dữ kiện thiếu, câu ngoài miền, tên chủ đề mới. Hai bộ được báo riêng.

Trên **mỗi tầng**, mẫu số là số ca có nhãn tương ứng:

| Tầng | Điều kiện đúng |
| --- | --- |
| Parse | Câu trong miền có cây phủ hết token; câu `UNKNOWN` nhận `()`. |
| Intent | Intent trùng nhãn. |
| Entity | ID chuẩn trùng nhãn; `OUT_OF_SCOPE` tương ứng không có entity. |
| Query | `QueryResult.status` trùng nhãn; khi `FOUND` phải có ít nhất một nguồn. |
| Answer evidence | Đáp án chứa tất cả mảnh bắt buộc, không phải lời xin lỗi nếu `FOUND`. |

Một ca đạt khi mọi nhãn **đã khai báo** đều đúng. File bốn cột không có nhãn query/answer thì hai tầng đó không được tính; tránh biến “không kiểm tra” thành “đúng”. Kiểm mảnh đáp án không thay thế việc người đọc đánh giá toàn bộ câu và tính chính xác của nguồn.

## Kết quả hiện tại

- Bộ Q001–Q028: **28/28** ca đạt trên nhãn đã ghi. Đây là các câu nhóm đã dùng trong quá trình xây dựng grammar và hệ thống; không phải phép đo trên người dùng mới.
- Bộ challenge: **11/13** ca đạt. `C003` (“Chương 4 học vào những tuần nào?”) và `C011` (“Môn NLP gồm mấy phần?”) ban đầu cho thấy grammar thiếu biến thể; đã thêm hai luật tương ứng và chạy lại kiểm thử.
- Hai ca còn sai thật: `C012` (“Tuan 3 hoc gi?”) thiếu dấu tiếng Việt; `C013` (“Số tín chỉ của môn NLP là bao nhiêu?”) dùng trật tự câu khác. Cả hai bị từ chối ở parser, nên intent/entity/query/answer phía sau không thể đúng. Đó là giới hạn độ phủ grammar/tokenizer hiện tại, không phải dữ kiện KB bị thiếu.
- Gộp theo nhãn đã khai báo: **39/41** ca đạt. Con số này không phải dự đoán độ chính xác trên câu hỏi bất kỳ ngoài thực tế.

`output/evaluation.txt` ghi số đúng/mẫu số cho từng tầng, hai câu sai với kỳ vọng/thực tế và tầng lỗi đầu tiên. Bộ KB là dữ liệu mẫu; ngày deadline cụ thể vẫn không có, nên `C001` đúng khi trả `NOT_FOUND`.

## Mã nguồn và vòng sửa lỗi

`evaluate.py:load_evaluation_cases` đọc định dạng bốn đến sáu cột; `evaluate_cases` chạy từng câu độc lập với `use_context=False`; `render_evaluation_report` tạo báo cáo. `cli.py` gọi các hàm đó; `output.py` ghi UTF-8 vào `evaluation.txt`.

Khi một ca sai, xem **tầng đầu tiên sai**: parse → sửa tokenizer/grammar; intent/entity → sửa nhánh `Q_*` hoặc alias; query → sửa loader/chỉ mục/handler; answer → sửa mẫu câu hoặc nhãn kỳ vọng sau khi kiểm tra fact. Sau mỗi thay đổi, chạy lại `python -X utf8 -m unittest discover -s tests -v`, `run.py batch` và `run.py evaluate`.

Hội thoại Q029–Q034 vẫn là phần mở rộng tùy chọn, được giữ ngoài các con số trên.
