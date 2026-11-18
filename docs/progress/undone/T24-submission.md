# T24 · 🔧 Đóng gói nộp bài

- **Trạng thái:** zip cuối đã tạo, Docker pass; đóng gói lại nếu T22/T23 còn đổi
- **Phụ trách:** chưa giao
- **Yêu cầu:** đề mục 7.4

## Việc cần làm
- [x] Tên file: `MSSV1-MSSV2-MSSV3-MSSV4.zip`, dung lượng **< 10 MB** (file lớn → upload nơi khác,
      để link trong README).
- [x] Cấu trúc tối thiểu theo đề:
      ```
      project/
        src/  data/  models/  input/  output/
        README.md  Dockerfile
      ```
      Repo hiện để `data/`, `input/`, `output/`, `models/`, `Dockerfile`, `README.md` **bên trong
      `src/`** → khi đóng gói phải sắp lại cho đúng cấu trúc trên, và kiểm tra code vẫn tìm được
      data (`ProjectPaths`).
- [x] Không đưa vào zip: `tests/golden/` (2,2 MB, chỉ dùng nội bộ), `docs/` nội bộ, `tools/`,
      `__pycache__/`.
- [x] `output/` trong zip là kết quả chạy thật của code nhóm (`python run.py all`), không chép từ
      sample.
- [x] Giải nén zip ra thư mục mới, build Docker và chạy thử trước khi nộp (pass 17/11 trong WSL2,
      gói review; chạy lại với `--student-ids` cho zip cuối).

## Cập nhật 2026-11-16

tools/package_submission.py tạo dist/course-assistant-review.zip dưới 10 MB, đúng layout project/, loại golden/cache/tools; giải nén và chạy từ cwd khác, cả 9 output khớp byte. Chưa có MSSV để đặt tên cuối; kiểm chứng Docker còn thiếu. Dùng --student-ids và --verify-docker khi đủ điều kiện.

## Kết quả 2026-11-18

Trong WSL2 (Docker Engine 29.6.1, Python 3.14), trên snapshot working tree cộng video mới:

```
python3 tools/package_submission.py --student-ids 2310251 2310198 2311601 2212612 --verify-docker
```

- `dist/2310251-2310198-2311601-2212612.zip`: 535 232 byte, 54 file,
  sha256 `c0081cf61cee17c394f62ed07f10063697375b3fba978ddbe8230ff95e0b5e26`.
- Chạy gói giải nén từ cwd khác + `docker build`/`run`: cả 9 output khớp byte; validation ghi
  `"docker": "passed"`, `"final_student_filename": true`.
- 9 output trên Linux khớp sha256 với `src/output/` trong repo.

Nếu báo cáo (T22) hoặc video (T23) đổi, chạy lại lệnh trên để zip chứa bản mới.

Đóng gói lại cùng ngày sau khi có báo cáo PDF (`tools/package_submission.py` lấy `report/report.pdf`,
chỉ dùng `docs/report.md` khi chưa build PDF): zip 916 447 byte, 54 file, sha256
`a9e92458768f5f7a3701fe383b3ecea127088052ef550ab3b25c2a6bae46c2c9`; extracted run + Docker pass.
Trong WSL phải chép thêm `report/report.pdf` (chưa track) cạnh snapshot `git stash create`.
