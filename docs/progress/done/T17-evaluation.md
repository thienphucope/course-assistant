# T17 · 🔧 Evaluation (Phần IV)

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Code:** `src/hcmut/iaslab/nlp/app/evaluate.py`
- **Output:** `src/output/evaluation.txt`
- **Nghiệm thu:** `tests.test_contract_pipeline` pass — mọi câu sample làm đúng vẫn đúng; số câu
  cải tiến (C007, C008) được in ra (hợp đồng: `docs/contracts.md` §8)
- **Ngày xong / Commit:** 05/11/2026 · nhánh `dev`, commit chứa file này

## Đã làm

- [x] `load_evaluation_cases`, `evaluate_cases`, `load_dialogue_cases`, `render_dialogue_evaluation`,
      `render_evaluation` (code từ nhánh `sample`).
- [x] Chạy `sample_queries.txt`: so intent, entity, trạng thái query, fact trong câu trả lời.
- [x] Chạy riêng `challenge_queries.txt` cho error analysis; ca sai có cột nguyên nhân theo tầng
      (grammar thiếu mẫu / semantic sai intent / entity sai / query sai).
- [x] Bộ challenge đã mở rộng thành C001–C022, có alias mới, dữ kiện thiếu, ngoài miền và
      nhiều câu trong một lượt; golden đã sinh lại bằng `python tools/make_golden.py`.

## Kết quả ở mốc 05/11/2026 (lịch sử)

| Bộ | Kết quả |
| --- | --- |
| Bộ thầy cho (`sample_queries.txt`) | **42/42** (100%) intent, entity, query, answer |
| Bộ thách thức (`challenge_queries.txt`) | **6/8** (75%), trùng mốc tham chiếu của sample |
| Câu cải tiến mục tiêu (C007, C008) | 0/2 sửa được — in đúng như hợp đồng yêu cầu |

`evaluation.txt` của `dev` khớp từng dòng với bản của sample khi chạy cùng dữ liệu.

## Điểm yếu ghi nhận ở mốc 05/11/2026 (lịch sử)

- **Độ phủ cách nói hẹp (bản chất Classical).** Grammar viết tay chỉ nhận câu có luật khớp; câu
  ngoài mẫu bị từ chối thay vì đoán. Chat thử trên `dev` (7 câu): 1 câu trả lời đúng
  ("bài tập lớn là gì"); 2 câu từ chối **đúng** vì ngoài miền ("tôi đẹp trai không", "mai có học
  không"); 4 câu trong miền nhưng bị từ chối vì thiếu mẫu ("lịch học như nào", "yêu cầu của môn
  học", "chương nào học đầu tiên", "chương 5 là gì"). Đánh đổi: chính xác, giải thích được (mỗi
  đáp án lần ngược ra cây parse) nhưng recall thấp. Cách khắc phục là mở rộng grammar (T18).
- **Câu nhiều mệnh đề** ("Tuần 3 học gì? Tuần 4 học gì?") bị từ chối cả câu: mỗi câu một intent.
- **Tokenizer nối `chữ.chữ`** để giữ `TP.HCM`; hệ quả: gõ dính "xong.Hết" thành một token và câu bị
  từ chối. Chấp nhận (lỗi gõ của người dùng).
- **Parser Earley với luật rỗng** (`PREFIX ->`, `SUFFIX ->`): completer chưa xử lý trường hợp luật
  rỗng hoàn tất ngay tại cùng vị trí (điểm yếu kinh điển của Earley). Chưa gây lỗi với grammar hiện
  tại: 9849 câu sinh và 1500 biến thể ngẫu nhiên đều được nhận. Cần xem lại nếu thêm luật rỗng.
- **Generator** dừng ở 9849 câu khi xin 10 000 (`truncated`, giới hạn `max_tokens=32`). Hợp lệ vì
  đề chỉ yêu cầu ≤ 10 000 dòng.
- **Ngữ cảnh** chỉ nhớ tham chiếu gần nhất; "Còn tuần sau?" ngay sau câu hỏi tuần bị từ chối vì
  grammar chưa có mẫu đó (xem trong cuộc chat thử).

## Ghi chú

- Mốc tham chiếu (đo bằng code sample với grammar phase 1): 42/42 câu mẫu, 6/8 câu thách thức.
- Lý thuyết: `docs/knowledge/08-evaluation.md`.

## Cập nhật 2026-11-16

- Challenge mở rộng thành 22 câu: 20/22 đúng; C007/C008 còn thiếu grammar.
- Parser nullable completion đã được sửa và có test hồi quy; hạn chế nullable kể trên là ghi nhận lịch sử trước đợt này.
- Generator chuẩn hóa hình thức câu hỏi và chia quota đều; output mặc định 1.000 câu, đủ 26 nhánh.
- Báo cáo dùng số liệu mới trong docs/report.md; output đã chạy lại từ code hiện tại.

## Thiết kế triển khai hiện tại

### Dữ liệu và định nghĩa chỉ số
[`evaluate.py`](../../../src/hcmut/iaslab/nlp/app/evaluate.py) có EvaluationCase, EvaluationRecord, EvaluationSummary. Record lưu expected/actual, PipelineResult và bốn cờ intent/entity/query/answer. Summary đếm theo record; percentage xử lý tổng 0 để không chia 0. Chuỗi predicate/query chỉ để trace, không dùng so khớp ngữ nghĩa bằng nguyên văn.

load_evaluation_cases nhận dòng có ID dạng X001, 4 cột đầu bắt buộc và tối đa 6 cột. Cột 5 là FOUND/NOT_FOUND/SKIPPED; cột 6 là các fact ngăn bởi ;;. Dạng legacy bốn cột mặc định UNKNOWN→SKIPPED, GET_INSTRUCTOR→NOT_FOUND, còn lại FOUND. Header/comment không phải record được bỏ. Nay ID/dòng record sai, trùng ID, status không hợp lệ hoặc bộ rỗng phải báo ValueError thay vì làm giảm mẫu số mà không thông báo.

### Chấm một bộ
Reset context một lần trước bộ, chạy đúng thứ tự, lấy intent trước resolve và entity sau resolve. Entity rỗng biểu diễn OUT_OF_SCOPE nếu UNKNOWN, còn lại NONE. Found=True → FOUND; kind UNKNOWN/UNRESOLVED_CONTEXT → SKIPPED; các thất bại khác → NOT_FOUND.

Answer phải đúng category trước khi so fact chuẩn hóa NFC/lowercase/space: FOUND phải có đáp án và không phải fallback; NOT_FOUND phải đúng hằng của đề; SKIPPED phải đúng NOT_UNDERSTOOD hoặc MISSING_CONTEXT theo kind. Có must_contain không cho phép bỏ qua kiểm tra fallback. End-to-end còn yêu cầu parse hợp lệ cho intent trong miền và tree=None cho UNKNOWN.

Đợt audit sửa hai lỗ hổng: parse đã nhận câu ngoài miền nhưng semantic UNKNOWN vẫn từng được tính đúng; câu chứa fact fallback rồi chèn nội dung tự tạo vẫn từng được tính đúng. Test dùng PipelineResult giả lập để kiểm phép chấm độc lập với pipeline.

### Hội thoại và xuất báo cáo
load_dialogue_cases đọc heading DIALOGUE, các dòng U theo thứ tự và EXPECTED_REFERENCE; thiếu câu/reference, trùng ID hoặc không có phiên nay báo lỗi. `render_dialogue_evaluation` reset mỗi phiên, in trace các lượt và chấm entity của lượt cuối cùng cùng found=True. Alias PART_I_GRAMMAR_PARSER quy về PART_I cho chấm. API thực tế là render_dialogue_evaluation; không có hàm evaluate_dialogues trong code hiện tại.

Độ đúng dialogue hiện là **phân giải tham chiếu cuối phiên**, không phải so mọi fact ở mọi lượt. Evaluation renderer in A/B bảng chi tiết, C nguyên nhân theo tầng, D ưu/nhược; không khẳng định template bảo đảm không thể trả lời sai.

### Kết quả và bằng chứng
Hiện có 42/42 official, 20/22 challenge, 6/6 tham chiếu dialogue. C007 hỏi số buổi/tuần còn thiếu mẫu và KB; C008 dùng 'tuần thứ ba' chưa có luật/resolver tương ứng. Các ca thiếu KB đúng như tuần 99, chương 13, output Phần II không tính là sai khi kỳ vọng NOT_FOUND.

Những bảng 6/8, 28 test và lỗi nullable ở phần trên là lịch sử. Đợt này kiểm thêm label hỏng/duplicate, false acceptance, fallback và chuỗi ngữ cảnh LO. Các bộ đã dùng để xây grammar/luật; chưa có held-out set độc lập. Không dùng tỷ lệ hiện tại để suy ra độ chính xác trên mọi câu hỏi tự nhiên.
