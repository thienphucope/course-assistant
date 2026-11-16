# T11 · 🔥 Cây → semantic + Intent/Entity (Phần II)

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/hcmut/iaslab/nlp/app/semantic.py`, `entities.py`
- **Output:** `src/output/semantic.txt`, `src/output/intent-entity.txt`
- **Nghiệm thu:** `tests.test_contract_semantic` pass (hợp đồng: `docs/contracts.md` §3 — bảng
  26 nhánh → intent / entity / slots). Test dùng cây golden nên không phải chờ parser.

## Việc cần làm
- [x] Hàm cần viết: `SemanticInterpreter.interpret`; `EntityLexicon.from_file`, `resolve`, `resolve_week`, `resolve_chapter`, `resolve_topic`, `resolve_lo`, `resolve_assignment_part`, `resolve_resource_topic`, `resolve_rule`.
- [x] `SemanticInterpreter.interpret`: lấy nhánh `Q_*` con của `QUESTION` → intent; mỗi nhánh một
      handler rút slot, ví dụ `GET_SCHEDULE(week=WEEK_03)`.
- [x] Đọc entity qua node có tên (`WEEK_ENTITY`, `CHAPTER_ENTITY`, `TOPIC_ENTITY`, `LO_ENTITY`,
      `ASSIGNMENT_PART`, `ASSIGNMENT_FEATURE`, `RESOURCE_TOPIC`, `RULE_TOPIC`, `EXAM_ENTITY`).
      Grammar phase 1 giữ nguyên các node này cho mọi cách hỏi mới.
- [x] `EntityLexicon`: load `src/data/scaffolding/entities.txt`, resolve về ID chuẩn
      (`WEEK_NN`, `CHNN`, `LOx.y`, `PART_I..IV`, topic / resource / rule ID).
- [x] **FEAT_\* (ý của Khoa)** — cải tiến, làm *sau* khi pass hợp đồng: handler
      `Q_ASSIGNMENT_FEATURE` đọc **nhãn** node con (`FEAT_PARSING` → `PART_I`, `FEAT_SEMANTIC` →
      `PART_II`, `FEAT_CONTEXT` → `PART_III`, `FEAT_EVAL` → `PART_IV`) thay vì tra cứng 5 từ như
      sample. Đổi hợp đồng §3 → làm theo `docs/contracts.md` §10, rồi tiếp mục FEAT_* trong
      `T18-grammar-extensions.md`.
- [x] **Alias mới cho lexicon** — cải tiến, cũng theo §10: `dịch máy` → `MACHINE_TRANSLATION`
      (resource); `thư viện có sẵn` → `EXTERNAL_LIBRARIES` (rule).

## Ghi chú
- `ASSIGNMENT_PART` chỉ có `phần` / `part` + số La Mã i–iv; câu deadline luôn hỏi deadline chung
  của BTL (không theo phần).
- Lý thuyết: `docs/knowledge/05-semantic-intent-entity.md`.

## Kết quả nghiệm thu 2026-11-16

Nghiệm thu golden semantic; handler FEAT đọc nhãn nhóm, giữ cụm feature gốc. Alias dịch máy và thư viện có sẵn đã nhận qua grammar. Cập nhật contracts §3 và sinh lại golden bằng adapter tường minh trên sample.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Dữ liệu trao đổi
[`SemanticFrame`](../../../src/hcmut/iaslab/nlp/app/semantic.py) có intent, entity, slots và source_branch. predicate là chuỗi để trình bày, không được query parse ngược để lấy ý nghĩa. Slots giữ kiểu dữ liệu, chẳng hạn `topics` là list ID; entity là tiêu điểm cho evaluation/context.

### Duyệt cây và dispatch
`interpret(None)` trả UNKNOWN. Với cây, tìm QUESTION rồi lấy con trực tiếp có nhãn Q thuộc BRANCH_INTENTS; chọn `_handle_q_*`, trích các constituent có tên và gắn source_branch. Không có QUESTION/nhánh/handler phù hợp cũng trả UNKNOWN. Tổng cộng 26 nhánh: thông tin môn/giảng viên, lịch, chủ đề/chương, LO, BTL, deadline, resource/rule và năm yêu cầu context.

Ví dụ WEEK_ENTITY → resolve_week → WEEK_03 → GET_SCHEDULE với slot week. Hai TOPIC_ENTITY của Q_SCHEDULE_TOPICS tạo list topic; Q_CONTEXT_* tạo CONTEXT_DEPENDENT với action và entity=None. T15 mới giải frame context, không giấu việc phân giải trong handler semantic.

### Entity lexicon là thiết kế kết hợp
[`entities.py`](../../../src/hcmut/iaslab/nlp/app/entities.py) đọc các section COURSE/PART/CHAPTERS/TOPICS/ASSIGNMENT/INTENTS từ entities.txt; các hàm family dùng bảng ID topic/resource/rule và regex tuần/chương/LO/phần BTL. Không phải thêm bất kỳ dòng nào vào file cũng tự tạo được intent hoặc ID mới. COURSE/ASSIGNMENT trong file có metadata tên đầy đủ; handler hiện cố định CO3085/BTL01 cho miền một môn, một BTL.

Chuẩn hóa alias dùng NFC/lowercase, dấu câu và khoảng trắng; week/chapter lấy chữ số, LO nhận mã lo, phần BTL nhận i–iv và có hỗ trợ digit ở resolver dù grammar hiện dùng La Mã. ID số vượt KB vẫn được giữ, ví dụ WEEK_99: semantic có nghĩa cú pháp nhưng query mới quyết định fact có tồn tại.

### FEAT và alias
Q_ASSIGNMENT_FEATURE đọc node con FEAT_PARSING/SEMANTIC/CONTEXT/EVAL → PART_I/II/III/IV. Slot feature giữ nguyên cụm lá như `parse tree`, không tra cứng năm từ cũ. `dịch máy` và `thư viện có sẵn` được nhận ở cả grammar và bảng resource/rule ID; xem T18. Thêm từ mới phải kiểm cả grammar, lexicon, semantic và query để tránh nhận cú pháp nhưng mất slot.

### Hợp đồng và kiểm chứng
Semantic không load hay dùng KnowledgeBase. `test_contract_semantic` tái dựng 2.034 cây golden độc lập với parser, so frame đủ bốn trường. `test_feature_labels_and_new_aliases` chạy câu thật qua pipeline. Nhánh không có fact vẫn phải tạo frame đúng; không gán UNKNOWN chỉ vì KB thiếu thông tin giảng viên.

**Giới hạn:** các bảng ánh xạ và quy tắc phần lớn viết tay; không hỗ trợ entity tùy ý hay nhiều intent trong một câu. Việc resolve được ID không chứng minh đáp án hay quan hệ của ID đó có trong KB.
