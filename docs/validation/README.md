# Nghiệm thu đợt hoàn thiện 2026-11-16

Nhánh `feat/complete-remaining-tasks`, nền `b104437`; kết quả nghiệm thu nằm trong commit chứa file này.
Môi trường thực thi: Windows, Python 3.11.9. Dockerfile dùng Python 3.12.

| Kiểm tra | Kết quả |
| --- | --- |
| `cd src; python -m unittest discover -s tests -t .` | 33 test pass, không skip. |
| `python tools/check_grammar.py --samples 1000 --json docs/validation/grammar-check.json` | PASS; 42/42 câu đề, 20/22 challenge, 6/6 hội thoại. |
| Generator | 1.000 câu duy nhất; 26 nhánh, mỗi nhánh 38–39 câu; parse lại được; đã đọc 20 câu lấy mẫu seed 261. |
| Giới hạn sinh câu | Yêu cầu 10.001 câu: sinh 9.398 câu duy nhất, CLI parse lại toàn bộ thành công, giữ đúng trần 10.000. Generator có thể dừng sớm theo quota/budget. |
| Ambiguity | Không phát hiện trong 1.047 câu khác nhau đã kiểm; parser tìm tối đa 2 cây, không phải chứng minh toàn bộ CFG. |
| `python tools/package_submission.py` | Giải nén vào thư mục mới, chạy từ cwd khác; 9 output khớp bản source theo byte, UTF-8/LF. |
| `python tools/render_demo.py` | ffprobe xác nhận H.264, 1280×720, 128 giây; đã xem frame parser, context, FEAT, fallback và đánh giá; phụ đề tiếng Việt, không có tiếng. |
| Docker | Chưa chạy: máy không có lệnh Docker. Dùng `--verify-docker` trên công cụ đóng gói để kiểm build/run và so output. |

`grammar-check.json` ghi kết quả theo suite, độ phủ nhánh, query status, ca thiếu
dữ kiện/ngữ cảnh và lỗi. Hai ca challenge sai C007/C008 còn thiếu mẫu grammar;
không có hồi quy trên câu mẫu. C018 là lỗi found/fallback đã sửa so với sample.

Gói kiểm tra ở `dist/course-assistant-review.zip`; checksum/dung lượng thật ở
`dist/course-assistant-review.validation.json`. Video ở `dist/course-assistant-demo.mp4`
và `project/demo.mp4` trong zip. `dist/` không được Git theo dõi, có thể tái tạo bằng
hai công cụ trên. Gói không chứa golden, tools hoặc cache của repo.

Trước nộp: nhóm điền tên/MSSV, duyệt báo cáo/khai báo AI, phân vai trình bày,
chốt video/định dạng báo cáo và chạy kiểm chứng Docker. Sau đó dùng
`--student-ids` để tạo tên zip chính thức theo đề.
