# Nấc 8 — Evaluation (Phần IV): chấm chính mình, không tự khen

> Có cả pipeline rồi. Phần IV bắt **đo** nó đúng bao nhiêu, sai ở đâu. Bắt buộc.

## Dữ liệu có sẵn (thầy cho)
`data/scaffolding/sample_queries.txt`: mỗi dòng
`QUERY | EXPECTED_INTENT | EXPECTED_ENTITY` = đáp án chuẩn để so.

## Chạy gì
Mỗi query → chạy full pipeline → lấy intent/entity **máy đoán** → so EXPECTED:
- **Accuracy intent** = intent đúng / tổng.
- **Accuracy entity** = entity đúng / tổng.
- **Out-of-scope** (Q026–028): phải ra `UNKNOWN`. Đoán ra intent thật = **sai kiểu
  nguy hiểm** (máy tưởng hiểu câu ngoài phạm vi).

## Phần ăn điểm: PHÂN TÍCH ca sai (đừng chỉ in con số)
Với mỗi ca sai, chỉ đúng **thủ phạm**:
| Triệu chứng | Gốc | Vá ở đâu |
|---|---|---|
| ra UNKNOWN mà đáng ra có intent | **grammar thiếu mẫu** câu đó | phủ thêm nhánh Q (doc 05) |
| intent đúng, entity sai | slot bắt sai / thiếu đồng nghĩa | entities.txt ② |
| intent sai hẳn | 2 nhánh Q **chồng mẫu** → nhập nhằng | tách mẫu trong grammar |

→ Vòng lặp: **đo → thấy lỗ → vá grammar → đo lại.** Đây là lý do grammar ăn 70%
công (doc 00 §7): accuracy sống/chết theo **độ phủ** của grammar, không phải số intent.

## Nối bài tập
`output/evaluation.txt`: bảng số + danh sách ca sai kèm chẩn đoán.
