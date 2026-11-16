# T21 · 🔧 Dockerfile

- **Trạng thái:** đã chuẩn bị; chờ kiểm chứng Docker
- **Phụ trách:** chưa giao
- **File:** `src/Dockerfile`

## Việc cần làm
- [ ] Build và chạy được toàn bộ pipeline trong Docker (bài được chấm bằng Docker).
- [ ] Sinh đủ 9 file trong `src/output/`.

## Cập nhật 2026-11-16

Dockerfile mặc định chạy all, có UTF-8 và .dockerignore. Source và gói giải nén sinh đủ 9 output. Máy hiện không có lệnh docker nên chưa nghiệm thu build/run. Chạy tools/package_submission.py --verify-docker trên máy có Docker.
