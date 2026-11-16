# Nấc 8 — Evaluation (Phần IV): chấm chính mình, không tự khen

> Có cả pipeline rồi. Phần IV bắt **đo** nó đúng bao nhiêu, sai ở đâu. Bắt buộc.

## Dữ liệu có sẵn
`src/data/scaffolding/sample_queries.txt`, mỗi dòng
`ID | QUERY | EXPECTED_INTENT | EXPECTED_ENTITY | EXPECTED_QUERY_STATUS | REQUIRED_ANSWER_TERMS`:
- **Q001–Q034 = của thầy** (bản gốc trong `docs/materials/NLP_Course_Assistant_Sample_Data.zip` chỉ có 4 cột đầu).
- **S001–S008** = câu ví dụ nguyên văn trong đề.
- Cột status (`FOUND` / `NOT_FOUND` / `SKIPPED`) và dữ kiện bắt buộc (`;;` = tất cả phải có)
  được bổ sung để chấm được cả bước query và câu trả lời.

Thêm: `challenge_queries.txt` (C001–C022, nhóm tự viết để phân tích lỗi — **ghi rõ nguồn**, đề
7.2) và `dialogues.txt` (6 hội thoại, cho Phần III).

## Chạy gì
Mỗi bộ test **reset ngữ cảnh một lần rồi chạy theo thứ tự file** (có câu như "Nó có liên quan
đến parsing không?" trỏ về câu ngay trước). Mỗi query → full pipeline → so EXPECTED:
- **Accuracy intent** = intent đúng / tổng.
- **Accuracy entity** = entity đúng / tổng.
- **Query status + câu trả lời**: đúng FOUND / NOT_FOUND / SKIPPED, và chứa đủ dữ kiện bắt buộc.
- **Out-of-scope** (Q026–028): phải ra `UNKNOWN`. Đoán ra intent thật = **sai kiểu
  nguy hiểm** (máy tưởng hiểu câu ngoài phạm vi).

## Phần ăn điểm: PHÂN TÍCH ca sai (đừng chỉ in con số)
Với mỗi ca sai, chỉ đúng **thủ phạm**:
| Triệu chứng | Gốc | Vá ở đâu |
|---|---|---|
| ra UNKNOWN mà đáng ra có intent | **grammar thiếu mẫu** câu đó | phủ thêm nhánh Q (doc 05) |
| intent đúng, entity sai | slot bắt sai / thiếu đồng nghĩa | entities.txt ② |
| intent sai hẳn | 2 nhánh Q **chồng mẫu** → nhập nhằng | tách mẫu trong grammar |
| intent/entity đúng, status hoặc đáp sai | query tra sai / template thiếu dữ kiện | query, answer (doc 06) |

→ Vòng lặp: **đo → thấy lỗ → vá grammar → đo lại.** Đây là lý do grammar ăn 70%
công (doc 00 §7): accuracy sống/chết theo **độ phủ** của grammar, không phải số intent.

## Nối bài tập
`output/evaluation.txt`: bảng số + danh sách ca sai kèm chẩn đoán.
