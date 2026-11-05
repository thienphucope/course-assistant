# T17 · 🔧 Evaluation (Phần IV)

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Code:** `src/hcmut/iaslab/nlp/app/evaluate.py`
- **Output:** `src/output/evaluation.txt`
- **Nghiệm thu:** `tests.test_contract_pipeline` pass — mọi câu sample làm đúng vẫn đúng; số câu
  cải tiến (C007, C008) được in ra (hợp đồng: `docs/contracts.md` §8)
- **Ngày xong / Commit:** 05/11/2026 · nhánh `dev`, commit chứa file này

## Đã làm

- [x] `load_evaluation_cases`, `evaluate_cases`, `load_dialogue_cases`, `evaluate_dialogues`,
      `render_evaluation` (code từ nhánh `sample`).
- [x] Chạy `sample_queries.txt`: so intent, entity, trạng thái query, fact trong câu trả lời.
- [x] Chạy riêng `challenge_queries.txt` cho error analysis; ca sai có cột nguyên nhân theo tầng
      (grammar thiếu mẫu / semantic sai intent / entity sai / query sai).
- [ ] Mở rộng thêm bộ test (nhiều cách diễn đạt, câu ngoài phạm vi...) — chưa làm; làm khi cần
      thêm số liệu cho báo cáo (nhớ chạy lại `python tools/make_golden.py`).

## Kết quả (nhánh `dev`)

| Bộ | Kết quả |
| --- | --- |
| Bộ thầy cho (`sample_queries.txt`) | **42/42** (100%) intent, entity, query, answer |
| Bộ thách thức (`challenge_queries.txt`) | **6/8** (75%), trùng mốc tham chiếu của sample |
| Câu cải tiến mục tiêu (C007, C008) | 0/2 sửa được — in đúng như hợp đồng yêu cầu |

`evaluation.txt` của `dev` khớp từng dòng với bản của sample khi chạy cùng dữ liệu.

## Điểm yếu đã biết (đưa vào báo cáo T22: hạn chế và hướng mở rộng)

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
