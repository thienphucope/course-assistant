# T15 · ✨ Phần III — Dialogue (optional)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/dialogue.py`
- **Output:** `src/output/dialogue.txt`
- **Nghiệm thu:** `tests.test_contract_dialogue` pass (hợp đồng: `docs/contracts.md` §7 — bảng
  `action` → frame sau khi giải)

## Việc cần làm
- [x] Hàm cần viết: `DialogueContext.resolve`, `DialogueContext.update`.
- [x] Test mẫu `src/tests/test_pipeline.py`: thay `skipTest` TODO về ngữ cảnh hội thoại.
- [x] Giữ ngữ cảnh cục bộ theo loại: chương / phần BTL / LO vừa nhắc.
- [x] Giải tham chiếu: `nó`, `chương này/đó`, `phần này/đó`, `nội dung này`.
- [x] Chạy 6 hội thoại trong `src/data/scaffolding/dialogues.txt`.

## Ghi chú
- Grammar phase 1 chỉ nhận đại từ hợp với loại thực thể resolver cần (đã bỏ `cái này`, `bài
  này`, `còn tuần sau`…). Muốn nhận thêm thì resolver phải hỗ trợ trước.

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu golden dialogue và 6/6 hội thoại; kiểm thử nhớ chương độc lập với phần BTL, không cập nhật khi query thất bại và reset phiên.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Mô hình state và call order
[`DialogueContext`](../../../src/hcmut/iaslab/nlp/app/dialogue.py) thuộc một CourseAssistant/phiên, giữ last_entity, last_chapter, last_assignment_part, last_lo và history. Resolver dùng các field theo loại, không tìm trong history để suy luận. `resolve(raw_frame)` chạy trước query, `update(resolved_frame, query_result)` chạy sau answer. reset xóa cả field lẫn history.

### Năm hành động được hỗ trợ
| action | State cần có | Frame trả về |
| --- | --- | --- |
| TOPIC_RELATION | chương gần nhất | GET_TOPIC(chapter, relation) |
| NEXT_CHAPTER | chương gần nhất và số kế ≤12 | GET_TOPIC(chapter kế) |
| ASSIGNMENT_OUTPUT | phần BTL gần nhất | GET_ASSIGNMENT(BTL01, section, field=OUTPUTS) |
| CONTEXT_RESOURCE | chương gần nhất | GET_RESOURCE(topic=chapter, chapter) |
| LO_CHAPTER | LO gần nhất | GET_TOPIC(lo) |

Frame mới giữ source_branch của câu context. Frame thường hoặc thiếu state trả lại nguyên frame và trace=None; query phân biệt UNRESOLVED_CONTEXT để answer báo thiếu ngữ cảnh. Không đoán chương 13 sau chương 12 hoặc lấy phần BTL thay cho chương.

### Quy tắc update và lỗi đã sửa
Chỉ result.found=True mới cập nhật. Entity CH*/PART_*/LO* cập nhật cache theo loại; SCHEDULE_WEEK suy ra chapter_id từ tuần, TOPIC_SEARCH lấy chương đầu tiên trong kết quả. Đợt rà soát bổ sung LO_CHAPTER: phải nhớ chapter_id của chương vừa trả lời.

Ca hồi quy: nhắc CH04 → hỏi LO2.5 → hỏi chương của LO (CH06) → hỏi 'Nó có liên quan đến parsing không?'. Code cũ vẫn dùng CH04; hiện dùng CH06. Việc nhắc LO đơn thuần chưa xóa chương cũ, nhưng khi answer đã xác định chương mới thì cache chương phải theo kết quả đó.

History mặc định chỉ giữ 20 entity gần nhất; history_limit<=0 nay không lưu history, vẫn cập nhật cache có kiểu. Trước đây slice `[:-0]` không xóa gì nên limit=0 lại làm danh sách tăng mãi. Không coi history_limit là thời hạn hết hiệu lực của tham chiếu.

### Nghiệm thu và giới hạn
`test_contract_dialogue` so frame từng lượt của 6 fixture. `test_dialogue_state_is_scoped_and_resettable` kiểm phân loại/reset/query thất bại. Hai test audit kiểm chuỗi LO→chương→quan hệ và history limit=0. Hợp đồng §7 đã ghi thêm update LO_CHAPTER; fixture cũ vẫn giữ kết quả vì chuỗi mới có test riêng.

Đây là resolver theo action định trước, không hiểu đồng tham chiếu tổng quát. Các từ 'nó/phần này' chỉ có nghĩa theo nhánh grammar đã chọn; topic có nhiều chương dùng kết quả đầu tiên. Không có clarification, tham chiếu xa hay state dùng chung giữa hai process CLI.
