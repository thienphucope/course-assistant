# T02 · 🔧 Đồng bộ `src/data/` với bộ dữ liệu của sample

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Ngày xong / Commit:** 22/10/2026 · `687b9a0`

## Đã làm

- [x] Thay `src/data/kb/` và `src/data/scaffolding/` (trước đây là placeholder rút gọn, ví dụ
      `schedule.txt` 21 dòng) bằng nguyên bộ dữ liệu của nhánh `sample`
      (`docs/sample-src/data/`, `schedule.txt` 166 dòng).
- [x] `grammar.cfg` không thay ở bước này (grammar làm riêng — xem
      [T03-grammar-phase1.md](T03-grammar-phase1.md)).
- [x] Cập nhật `src/README.md` và `src/data/README.md` cho khớp.

## Ghi chú

- Bản gốc lưu trong `docs/materials/NLP_Course_Assistant_Sample_Data.zip`; `src/data/` giữ KB
  gốc và các phần mở rộng kiểm thử/grammar. Thư mục `data/` ngoài đã bỏ ở `9096375`.
- Code đọc data qua `ProjectPaths.from_root(root)` → `root/data/...`, với root là `src/`.
- PR #2 (Bách) có sửa `entities.txt`, `sample_queries.txt`, `dialogues.txt`,
  `challenge_queries.txt` theo format code riêng — sẽ conflict nếu merge PR đó sau commit này
  (PR này không merge — xem `done/T05-codebase-decision.md`).

## Thiết kế triển khai hiện tại

### Quyết định đồng bộ
`687b9a0` thay bộ placeholder trong skeleton bằng dữ liệu đầy đủ từ nhánh `sample`. Đồng bộ theo thư mục KB/scaffolding; grammar là ranh giới của T03/T18 nên không chép đè trong bước này. Đây là thao tác chuẩn bị dữ liệu, không phải nâng cấp schema riêng của một module.

### Thiết kế đường dẫn và quyền sở hữu dữ liệu
- [`ProjectPaths.from_root`](../../../src/hcmut/iaslab/nlp/app/paths.py) nhận **root ứng dụng**, hiện là `src/`, rồi tạo `root/data/kb`, `root/data/scaffolding`, `root/data/grammar.cfg`.
- Khi đóng gói, root trở thành `project/`; cùng API đọc `project/data/`. Mã package có thể ở `project/src/hcmut/`, tách khỏi data mà không đổi loader.
- File KB là nguồn chung; alias/câu đánh giá trong scaffolding thuộc các nhiệm vụ riêng. Không thay định dạng dữ liệu cho một implementation rồi bắt cả nhóm đọc theo.

### Trạng thái sau khi dọn repo
Thư mục `data/` ngoài đã xóa; bản nguồn lưu tại `docs/materials/NLP_Course_Assistant_Sample_Data.zip`. Bản hiện tại trong `src/data/` gồm dữ kiện KB gốc, grammar và phần kiểm thử bổ sung. Không coi việc thêm status/fact vào bộ test là sửa nội dung KB.

### Kiểm chứng
`tests.test_kb` kiểm 15 tuần, 12 chương, 8 tài liệu, index CH04 → WEEK_04/WEEK_05 và tuần 15 không có chương. `tests.test_contract_kb` so cấu trúc, kiểu và giá trị collection. Chạy launcher từ cwd khác và gói giải nén kiểm rằng chương trình không dựa vào thư mục `data/` đã bỏ.

**Giới hạn:** ticket không định nghĩa cơ chế nâng phiên bản dữ liệu hay schema migration. Khi đổi KB/scaffolding, phải cập nhật hợp đồng liên quan và sinh lại golden theo T06.
