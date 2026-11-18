# T21 · 🔧 Dockerfile

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **File:** `src/Dockerfile`
- **Ngày xong / Commit:** 2026-11-17 / commit "Verify Docker in WSL2 and complete AI usage declaration"

## Việc cần làm
- [x] Build và chạy được toàn bộ pipeline trong Docker (bài được chấm bằng Docker).
- [x] Sinh đủ 9 file trong `src/output/`.

## Cập nhật 2026-11-16

Dockerfile mặc định chạy all, có UTF-8 và .dockerignore. Source và gói giải nén sinh đủ 9 output. Máy hiện không có lệnh docker nên chưa nghiệm thu build/run. Chạy tools/package_submission.py --verify-docker trên máy có Docker.

## Kết quả 2026-11-17

Nghiệm thu bằng Docker Engine 29.6.1 trong WSL2 (Ubuntu 26.04), trên bản sạch `git archive HEAD`
(`2e177be`) cộng `dist/course-assistant-demo.mp4`:

```
python3 tools/package_submission.py --verify-docker
```

- `docker build` từ thư mục `project/` giải nén từ zip (base `python:3.12-slim`): thành công.
- `docker run` mặc định (`ENTRYPOINT run.py --root /app`, `CMD all`): "Completed: 73 input questions,
  1000 generated samples, 9 output files in /app/output".
- Cả 9 output của container khớp byte với lần chạy source; validation ghi `"docker": "passed"`.
- 9 output chạy trên Linux (Python 3.14) khớp sha256 với `src/output/` trong repo (chạy trên Windows).

Lưu ý khi chạy lại trong WSL: `/etc/wsl.conf` mount ổ Windows với `uid=0,dmask=077` nên user thường
không đọc được `/mnt/d`; chép repo vào home WSL (`git archive HEAD | wsl tar -x -C ~/...`) rồi chạy.
Service `docker` trong WSL đang `disabled`: bật trước khi chạy bằng `wsl -u root systemctl start docker`.
