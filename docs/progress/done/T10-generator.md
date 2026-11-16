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
- [x] Trả `GeneratorStats` (requested / produced / explored / truncated) cho T16 ghi file.

## Ghi chú
- Lý thuyết: `docs/knowledge/07-generator.md`.

## Kết quả nghiệm thu 2026-11-16

Sinh 1.000 câu duy nhất, có chữ hoa đầu và dấu ?, phân bổ 38–39 câu/nhánh cho đủ 26 nhánh. CLI parse lại trước khi ghi. Tôn trọng giới hạn 10.000 câu.

- **Ngày xong:** 2026-11-16
- **Commit:** commit chứa file này trên nhánh `feat/complete-remaining-tasks` (nền `b104437`).
