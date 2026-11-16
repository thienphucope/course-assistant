# T18 · 🔥 Grammar mở rộng sau phase 1

- **Trạng thái:** xong
- **Phụ trách:** chưa giao
- **Code:** `src/data/grammar.cfg`
- **Nghiệm thu:** 26 nhánh, 42/42 câu mẫu, 0 câu mơ hồ trong corpus nghiệm thu; chạy lại `python tools/make_golden.py`

Phase 1 đã xong (`done/T03-grammar-phase1.md`). Bản sao `output/grammar.txt` do T16 ghi. Còn lại:

## Việc cần làm
- [x] Khi `T11-semantic.md` xong phần FEAT_*: thêm cách gọi tính năng BTL của Khoa
      (`grammar`, `parse tree`, `intent`, `entity`, `kb`, `hội thoại`, `test set`, `metric`, …)
      vào `ASSIGNMENT_FEATURE`, gom theo `FEAT_PARSING` / `FEAT_SEMANTIC` / `FEAT_CONTEXT` / `FEAT_EVAL`.
- [x] Khi lexicon có alias mới: thêm `dịch máy` vào `RESOURCE_TOPIC`, `thư viện có sẵn` vào `RULE_TOPIC`.
- [ ] (tuỳ chọn) C007 `Môn NLP học mấy buổi mỗi tuần?`, C008 `Tuần thứ ba tụi mình học bài gì vậy?`
      — sample cố ý để ngoài grammar; chỉ thêm nếu KB trả lời được.

## Ghi chú
- Mọi thay đổi phải giữ: 26 nhánh, 42/42 câu mẫu, 0 câu mơ hồ trong corpus nghiệm thu (xem quy ước ở `docs/progress/README.md`).

## Kết quả nghiệm thu 2026-11-16

Giữ 26 nhánh; bổ sung FEAT và 2 alias. Bộ đề 42/42, hội thoại 6/6; 1.000 câu sinh round-trip. Không phát hiện mơ hồ trong 1.047 câu khác nhau đã kiểm. C007/C008 là phần tùy chọn chưa triển khai, ghi phân tích trong báo cáo.

- **Ngày xong:** 2026-11-16
- **Commit nghiệm thu:** `ebe53eb` (nền `b104437`); thiết kế và bugfix mới xem mục bên dưới.

## Thiết kế triển khai hiện tại

### Thiết kế mở rộng mà giữ nhánh semantic
[`grammar.cfg`](../../../src/data/grammar.cfg) giữ 26 alternative QUESTION. Mở rộng đi vào constituent của nhánh đã có, không thêm Q mới chỉ để nhận một cách gọi. T03 là grammar phase 1; T18 hoàn thiện những alias/nhóm feature từng hoãn vì semantic chưa sẵn sàng.

### FEAT và đường đi tới query
`ASSIGNMENT_FEATURE -> FEAT_PARSING | FEAT_SEMANTIC | FEAT_CONTEXT | FEAT_EVAL`. FEAT_PARSING gồm parser/grammar/parse tree/văn phạm/phân tích cú pháp; SEMANTIC gồm hỏi đáp/semantic/intent/entity/KB/ngữ nghĩa; CONTEXT gồm ngữ cảnh/hội thoại/tham chiếu; EVAL gồm đánh giá/test set/metric/kiểm thử.

T11 map **nhãn** FEAT sang PART_I–IV, giữ text lá trong slot feature; T13 dùng section để tra assignment. Ví dụ BTL có phần parse tree không? → Q_ASSIGNMENT_FEATURE → FEAT_PARSING → GET_ASSIGNMENT(section=PART_I). Thêm từ vào đúng nhóm không cần mở rộng danh sách từ khóa riêng trong handler.

### Hai alias đi qua đầy đủ các tầng
`dịch máy` trong RESOURCE_TOPIC có bảng RESOURCE_IDS → MACHINE_TRANSLATION và query tìm tài liệu dịch máy. `thư viện có sẵn` trong RULE_TOPIC có RULE_IDS → EXTERNAL_LIBRARIES → key external_libraries của KB. Chỉ thêm terminal mà thiếu alias có thể nhận câu nhưng mất nghĩa; không xem parse thành công là hoàn tất T18.

### Hợp đồng và nghiệm thu
Hợp đồng §3 mô tả FEAT, giữ schema frame/query. tools/make_golden.py có adapter tương ứng trên baseline và EDGE_SENTENCES phủ 18 feature cùng hai alias, không sửa sample. Test parser kiểm cả cây có thêm node FEAT; test semantic kiểm frame; test pipeline dùng câu thật.

T19 hiện kiểm 42/42 official, 20/22 challenge, 6/6 dialogue và 1.000 câu sinh đủ 26 nhánh; không phát hiện mơ hồ trong 1.047 chuỗi đã kiểm. Kiểm không mơ hồ là theo corpus có giới hạn. Các thử nghiệm không chứng minh mọi tổ hợp grammar đều tự nhiên hay truy xuất đúng.

### Phần chưa triển khai
C007/C008 là optional vẫn để unchecked và giữ trong error analysis. Không bổ sung fact số buổi mỗi tuần nếu KB chưa có. Mở rộng ordinal 'thứ ba' cần sửa cả constituent tuần và resolver, không chỉ nhét thêm từ để parser nhận.
