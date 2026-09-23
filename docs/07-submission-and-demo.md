# Mốc 7 — Bản nộp, báo cáo và demo

Mốc này không thay đổi thuật toán NLP. Mục tiêu là chứng minh người khác có thể
nhận đúng bản nhóm nộp, chạy lại chương trình và đối chiếu kết quả với báo cáo.

## 1. Những phần đã chuẩn bị

- `src/README.md` đã có cài đặt, lệnh chạy, kiến trúc, grammar/parser, semantic,
  intent/entity, KB/query, lựa chọn Classical NLP, đánh giá, nguồn và hạn chế.
- `src/package_submission.py` kiểm tra file bắt buộc, số dòng output, JSON Lines,
  grammar, số câu sinh, dung lượng và thông tin thành viên.
- Script đóng gói nội dung `src/` thành một thư mục `project/` trong ZIP, loại
  cache Python và đặt tên ZIP theo danh sách MSSV.
- `docs/report-draft.md` là nội dung báo cáo kỹ thuật có thể chuyển sang Word/PDF.
- Kịch bản bên dưới bao phủ yêu cầu video của đề: input, xử lý, semantic, đáp án
  và một ca không thể trả lời từ KB.

## 2. Vì sao không tạo thêm `project/src/`

Đề đưa một cây thư mục tối thiểu mang tính minh họa. Scaffold Python do giảng
viên phát hành đặt `hcmut/`, `Dockerfile`, `setup.py` ngay dưới thư mục `python/`,
không có thêm một lớp `src/`. Nhóm đã chọn thư mục repo `src/` làm gốc runtime và
mọi đường dẫn đã được kiểm thử theo lựa chọn này.

Khi đóng gói, script chỉ đổi tên lớp ngoài thành `project/`:

```text
repo/src/hcmut/  →  ZIP/project/hcmut/
repo/src/data/   →  ZIP/project/data/
repo/src/output/ →  ZIP/project/output/
```

Không di chuyển code vào một lớp mới vì việc đó làm đổi `WORKDIR`, import path và
đường dẫn dữ liệu mà không đem lại chức năng nào.

## 3. Quy trình khóa bản nộp

Thực hiện đúng thứ tự từ thư mục `src/`:

```powershell
python -X utf8 run.py batch
python -X utf8 -m unittest discover -s tests -v
python -X utf8 package_submission.py check
```

Trên máy có Docker:

```powershell
docker build -t course-assistant .
$courseOutput = (Resolve-Path ./output).Path
docker run --rm --mount "type=bind,source=$courseOutput,target=/app/output" course-assistant
```

Chạy `package_submission.py check` lần nữa sau Docker. Khi không còn cảnh báo
thông tin thành viên, tạo ZIP:

```powershell
python -X utf8 package_submission.py build --student-ids MSSV1 MSSV2 MSSV3 MSSV4
```

Script tạo `submission/MSSV1-MSSV2-MSSV3-MSSV4.zip`. Mở ZIP và kiểm tra lớp đầu
tiên duy nhất là `project/`; sau đó giải nén sang một thư mục tạm và lặp lại lệnh
Docker ở chính bản giải nén. Không đóng gói `materials/`, `.git/`, cache Python,
dữ liệu gốc trùng lặp hoặc tài liệu nội bộ ngoài bản nộp.

## 4. Kịch bản video 4–6 phút

### 0:00–0:30 — Giới thiệu

“Nhóm xây dựng Course Assistant theo hướng Classical NLP. Pipeline gồm tokenizer,
CFG/Earley parser, semantic, intent/entity, query sáu file KB và answer template.”

Mở sơ đồ pipeline trong README. Nói rõ KB là dữ liệu mẫu và hệ thống không dùng
LLM để thay phần NLP bắt buộc.

### 0:30–2:15 — Một ca trả lời thành công

Chạy:

```powershell
python -X utf8 run.py ask --trace "Tuần 3 học gì?"
```

Chỉ lần lượt vào:

1. token `['tuần', '3', 'học', 'gì', '?']`;
2. cây có nhánh `Q_SCHEDULE_WEEK`;
3. semantic `GET_SCHEDULE(week=WEEK_03)`;
4. intent `GET_SCHEDULE`, entity `WEEK_03`;
5. query `KB.weeks[WEEK_03]`, status `FOUND`;
6. nguồn `schedule.txt:WEEK 03` và câu trả lời.

Giải thích một câu: parser quyết định cấu trúc, semantic quyết định yêu cầu và ID,
KB mới cung cấp nội dung trả lời.

### 2:15–3:15 — Ca không có dữ kiện

Chạy:

```powershell
python -X utf8 run.py ask --trace "Deadline của bài tập lớn là khi nào?"
```

Câu vẫn parse được và nhận đúng intent/entity, nhưng query cho `NOT_FOUND` vì
`assignments.txt` không có ngày cụ thể. Nhấn mạnh đây là hành vi đúng: hệ thống
không tự bịa deadline. Nếu còn thời gian, chạy một câu ngoài miền để chỉ ra
`Parse: ()` và `OUT_OF_SCOPE` khác với `NOT_FOUND`.

### 3:15–4:15 — Batch và đánh giá

Chạy:

```powershell
python -X utf8 run.py batch
```

Mở `output/evaluation.txt`: 28/28 trên bộ có nhãn và 11/13 trên challenge. Nêu
hai lỗi thật là câu thiếu dấu và một trật tự hỏi tín chỉ chưa có trong grammar.
Không giới thiệu 39/41 như độ chính xác trên mọi câu hỏi ngoài thực tế.

### 4:15–5:00 — Kết thúc

Mở cấu trúc `data/`, `output/` và `Dockerfile`. Tóm tắt ưu điểm: giải thích được,
có nguồn, tách `NOT_FOUND`/`OUT_OF_SCOPE`. Tóm tắt hạn chế: độ phủ phụ thuộc luật,
KB mẫu còn thiếu dữ kiện, chưa đánh giá hội thoại.

## 5. Dàn ý thuyết trình 5–10 phút

1. Bài toán và bảy nhóm câu hỏi bắt buộc — 45 giây.
2. Kiến trúc pipeline và ranh giới grammar/KB — 1 phút.
3. CFG và ba thao tác của Earley — 1,5 phút.
4. Ví dụ cây → semantic → intent/entity → query → answer — 2 phút.
5. Thiết kế KB, nguồn và xử lý thiếu fact — 1 phút.
6. Phương pháp đánh giá, kết quả và hai ca sai — 1,5 phút.
7. Hạn chế, hướng mở rộng và kết luận — 1 phút.

Mỗi thành viên cần giải thích được phần mình phụ trách và luồng của ví dụ tuần 3.

## 6. Các việc nhóm còn phải cung cấp hoặc thực hiện

1. Gửi họ tên, MSSV và phân công thật để thay bảng đầu README và báo cáo.
2. Build/run Docker trên máy có Docker rồi lưu ảnh hoặc log cho báo cáo.
3. Chuyển bản nháp báo cáo sang định dạng giảng viên yêu cầu và rà cách trình bày.
4. Quay video theo kịch bản, nghe lại âm thanh và kiểm tra chữ trong terminal.
5. Tạo ZIP bằng MSSV thật, giải nén và chạy thử bản ZIP trước khi nộp.

Mốc 7 chỉ có thể đóng hoàn toàn sau năm việc này vì chúng phụ thuộc thông tin nhóm,
môi trường Docker và thao tác ghi hình thực tế.
