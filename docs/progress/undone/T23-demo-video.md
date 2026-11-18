# T23 · 🔧 Video demo + thuyết trình

- **Trạng thái:** video tự động xong (có tên nhóm); Phúc làm video nộp
- **Phụ trách:** Phúc (video)
- **Yêu cầu:** đề mục 7.6 — video ngắn; có thể bị gọi thuyết trình tuần 13–14 (5–10 phút/nhóm)

## Việc cần làm
- [x] Video thể hiện đủ: nhận câu hỏi → xử lý chính → kết quả phân tích / semantic → câu trả lời
      → **1 ca không trả lời được**.
- [ ] Kịch bản thuyết trình 5–10 phút, chia phần cho từng người (ai trình bày phần mình làm).
- [ ] (tuỳ chọn) dùng `tools/visualizer/index.html` để minh hoạ luồng dữ liệu qua các module.

## Cập nhật 2026-11-16

docs/demo-script.md có cảnh quay 3–4 phút và nội dung thuyết trình 5–10 phút. tools/demo.py chạy 7 câu thật, trace lưu docs/demo-transcript.txt; có thiếu KB và ngoài miền. tools/render_demo.py tạo video 1280×720 dài 2 phút 8 giây từ runtime, phụ đề tiếng Việt, không có tiếng; file dist/course-assistant-demo.mp4 và project/demo.mp4 trong gói kiểm tra. Đây là bản phát lại tự động. Nhóm còn điền thành viên/phân vai và chốt bản nộp.

## Cập nhật 2026-11-18

Màn mở đầu video có tên/MSSV 4 thành viên; màn cuối ghi Docker đã kiểm chứng. Render lại bằng
`python tools/render_demo.py` (128 giây). Còn: phân vai thuyết trình, chọn nộp bản tự động hay quay có thuyết minh.

## Việc tiếp theo (chốt 18/11)

Phúc làm video nộp (thay hoặc bổ sung bản tự động `dist/course-assistant-demo.mp4`).
- [ ] Đủ 5 cảnh đề 7.6: nhận câu hỏi → xử lý chính → kết quả phân tích/semantic → câu trả lời →
      1 ca không trả lời được. Kịch bản: `docs/demo-script.md`; lệnh trace: `python src/run.py answer "..." --trace`.
- [ ] Đưa video vào gói: `python tools/package_submission.py --student-ids 2310251 2310198 2311601 2212612
      --video <đường dẫn video> --verify-docker` (zip phải < 10 MB; video lớn thì upload và để link trong README).
- [ ] Phân vai thuyết trình 5–10 phút nếu nhóm được gọi (tuần 13–14).
