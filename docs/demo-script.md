# Kịch bản video demo và thuyết trình

## Chuẩn bị giao diện demo

Chạy từ gốc repo bằng Python rồi giữ cửa sổ này mở trong lúc quay.

```powershell
python tools/demo_web.py --open
```

Nếu trình duyệt chưa mở, vào [http://127.0.0.1:8765](http://127.0.0.1:8765).
Nếu cổng `8765` đang bận, thêm `--port 8766` và dùng URL hiện trong terminal.
Dùng `Ctrl+C` trong terminal để dừng sau khi quay.

Nhập câu hỏi hoặc chọn **Câu mẫu**, rồi bấm **Phân tích**. Dùng **Bước tiếp**,
**Bước trước**, phím mũi tên trái/phải khi con trỏ nằm ngoài ô nhập, hoặc bấm trực
tiếp một bước. Mỗi bước giữ nguyên trên màn hình để bạn thuyết minh. **Xem toàn bộ**
hiển thị các kết quả cùng lúc. **Lượt hỏi trong phiên** mở lại trace đã chạy.

## Kịch bản video khoảng 2 phút 45 giây

Mục 7.6 của đề yêu cầu người xem thấy câu hỏi,
bước xử lý chính, kết quả phân tích hoặc ngữ nghĩa, câu trả lời và một ca hệ thống
không trả lời được. Đề để nhóm chọn cách trình bày. Đọc lời dẫn hoặc đặt phụ đề ngắn
để người xem biết nên nhìn dòng nào và vì sao kết quả khác nhau. Dành phần giải thích
thuật toán và cách chấm cho buổi thuyết trình.

Dùng giao diện demo để đi qua các cảnh bên dưới. Nếu quay bằng terminal, chạy các
lệnh kèm theo từ gốc repo và phóng cỡ chữ để đọc được `PARSE`. Mỗi lần gọi script
terminal bắt đầu một phiên mới, riêng lệnh `dialogue` xử lý cả hai câu trong cùng phiên.
Trong gói đã giải nén, các lệnh CLI dùng `python run.py` từ thư mục `project/`.

### 0:00–0:10 · Mở đầu

**Màn hình** — CO3085 · Course Assistant. Hiện tên và MSSV của Phan Gia Bảo (2310251),
Nguyễn Huy Bách (2310198), Mai Anh Khoa (2311601) và Hoàng Ngô Thiên Phúc (2212612).

**Lời dẫn** — “Nhóm em làm trợ lý hỏi đáp cho môn Xử lý Ngôn ngữ Tự nhiên. Sau đây là
cách hệ thống phân tích câu hỏi và tra dữ liệu môn học.”

### 0:10–0:45 · Trả lời câu hỏi trực tiếp

**Trên giao diện** — Nhập “Môn NLP có bao nhiêu tín chỉ?” rồi di chuyển từ **Câu hỏi
& token** đến **Câu trả lời**. Dừng ở cây, vị từ và dữ liệu truy xuất để chỉ kết quả.

```powershell
python src/run.py answer "Môn NLP có bao nhiêu tín chỉ?" --trace
```

**Màn hình** — Giữ câu hỏi trên màn hình. Lần lượt chỉ `Q_COURSE_CREDITS` trên cây,
`GET_COURSE_INFO` với `field=CREDITS`, truy vấn `KB.course[CREDITS]`, nguồn
`kb/course_info.txt` và câu trả lời **3 tín chỉ**. Có thể dùng `python tools/demo.py credits`
để hiện thêm token và trạng thái `FOUND`.

**Lời dẫn** — “Em hỏi môn NLP có bao nhiêu tín chỉ. Trên cây cú pháp, nhánh
`Q_COURSE_CREDITS` cho biết đây là câu hỏi về tín chỉ. Từ cây, hệ thống xác định môn
CO3085 và trường tín chỉ, rồi tra dữ liệu môn học. Kết quả là 3 tín chỉ.”

### 0:45–1:15 · Hiểu câu hỏi nối tiếp

**Trên giao diện** — Gửi “Tuần 3 học gì?” rồi gửi “Nó có liên quan đến parsing không?”
trong cùng phiên. Sang **Ngữ cảnh** ở lượt thứ hai, sau đó mở **Câu trả lời**.

```powershell
python tools/demo.py dialogue
```

**Màn hình** — Cho thấy câu đầu “Tuần 3 học gì?” trả về Chương 3. Ở câu hỏi thứ hai,
chỉ `CONTEXT_DEPENDENT`, dòng `RESOLVED` có `CH03` và câu trả lời về parsing.

**Lời dẫn** — “Câu đầu cho biết tuần 3 học Chương 3. Khi em hỏi tiếp ‘Nó có liên quan
đến parsing không?’, hệ thống dùng chương vừa nhắc để hiểu chữ ‘nó’. Kết quả tra cho
thấy Chương 3 có nội dung về parsing.”

### 1:15–1:35 · Thiếu ngữ cảnh

**Trên giao diện** — Bấm **Phiên mới**, gửi lại “Nó có liên quan đến parsing không?”.
Chỉ kết quả ở **Ngữ cảnh**, **Truy vấn KB** và **Câu trả lời**.

```powershell
python tools/demo.py missing-context
```

**Màn hình** — Cùng câu “Nó có liên quan đến parsing không?” trong phiên mới. Chỉ cây
cú pháp, `CONTEXT_DEPENDENT`, `QUERY: NO_QUERY` và thông báo thiếu ngữ cảnh.

**Lời dẫn** — “Em hỏi lại câu vừa rồi trong một phiên mới. Hệ thống nhận ra đây là
câu hỏi có tham chiếu và báo thiếu ngữ cảnh vì chưa có chương nào được nhắc tới.”

### 1:35–1:55 · KB thiếu dữ kiện

**Trên giao diện** — Chọn câu mẫu **Thiếu dữ kiện trong KB**, rồi chuyển từ **Ngữ nghĩa**
sang **Truy vấn KB** và **Câu trả lời**.

```powershell
python tools/demo.py missing-kb
```

**Màn hình** — Câu “Ai dạy NLP?” có cây cú pháp và `GET_INSTRUCTOR`. Chỉ truy vấn
`KB.course[instructor]`, trạng thái `NOT_FOUND` và thông báo không tìm thấy thông tin.

**Lời dẫn** — “Hệ thống hiểu em đang hỏi tên giảng viên và đã tra dữ liệu môn học.
Bộ dữ liệu không có tên giảng viên, nên trợ lý báo không tìm thấy thông tin.”

### 1:55–2:10 · Câu hỏi ngoài miền

**Trên giao diện** — Chọn câu mẫu **Câu hỏi ngoài miền**, rồi mở **Cây cú pháp**.

```powershell
python tools/demo.py out-of-scope
```

**Màn hình** — Câu hỏi về thời tiết cho `PARSE: ()`, `SEMANTIC: UNKNOWN()` và
`QUERY: NO_QUERY`.

**Lời dẫn** — “Câu hỏi về thời tiết nằm ngoài miền của trợ lý. Parser đánh dấu bằng
cặp ngoặc rỗng và hệ thống dừng trước bước tra dữ liệu.”

### 2:10–2:25 · C007 hỏi số buổi học mỗi tuần

**Trên giao diện** — Nhập “Môn NLP học mấy buổi mỗi tuần?”. Mở **Cây cú pháp**
để thấy `()` và **Truy vấn KB** để thấy `NO_QUERY` / `SKIPPED`.

```powershell
python src/run.py answer "Môn NLP học mấy buổi mỗi tuần?" --trace
```

**Màn hình** — Bộ thử thách kỳ vọng `GET_COURSE_INFO` cho `CO3085`, sau đó báo
`NOT_FOUND` vì KB thiếu dữ kiện. Kết quả thực tế là `UNKNOWN()` và hệ thống bỏ
qua bước tra cứu. Hai ca C007 và C008 có trong `output/evaluation.txt` của gói nộp.

**Lời dẫn** — “Câu này hỏi số buổi học mỗi tuần. Văn phạm thiếu mẫu cho dạng hỏi
này, nên hệ thống dừng ở bước phân tích cú pháp. Bộ thử thách kỳ vọng hệ thống hiểu
câu hỏi và báo thiếu dữ kiện sau khi tra KB.”

### 2:25–2:45 · C008 hỏi tuần bằng số thứ tự viết chữ

**Trên giao diện** — Chọn câu mẫu **Cách diễn đạt văn phạm chưa phủ**, rồi mở **Cây cú pháp**.

```powershell
python tools/demo.py grammar-gap
```

**Màn hình** — Câu “Tuần thứ ba tụi mình học bài gì vậy?” trả `PARSE: ()` và
`UNKNOWN()`. Bộ thử thách kỳ vọng `GET_SCHEDULE` cho `WEEK_03`, tra thấy Tuần 3
học Chương 3. Có thể chèn lại kết quả “Tuần 3 học gì?” từ cảnh hội thoại để đối
chiếu.

**Lời dẫn** — “Câu này cũng hỏi nội dung tuần 3. Văn phạm hiện tại chưa nhận cách
nói ‘tuần thứ ba’, nên parser cũng in cặp ngoặc rỗng. Đây là một ca hệ thống xử lý
sai trên bộ thử thách.”

Nếu cần bản khoảng 2 phút, giữ cảnh trả lời trực tiếp, hội thoại và thiếu dữ kiện
trong KB, rồi gộp C007 và C008 vào một cảnh ngắn.

Để luyện nhập câu hỏi từng lượt, dùng `python src/run.py interactive`. Nhập `/reset`
để xóa ngữ cảnh, rồi lặp lại câu hỏi có chữ “nó”. Dùng `/quit` để thoát. Để quay
cây cú pháp và ngữ nghĩa, dùng các lệnh trace trong từng cảnh ở trên.

## Thuyết trình 5–10 phút

Phân vai dưới đây là đề xuất theo nội dung; nhóm điền người phụ trách thực tế.

| Khoảng thời gian | Nội dung | Người trình bày |
| --- | --- | --- |
| 0:00–1:00 | Phạm vi đề, KB, lựa chọn Classical, luồng dữ liệu. | Chờ nhóm điền |
| 1:00–3:00 | CFG 26 nhánh, tokenizer, Earley và xử lý ε; chỉ một cây thật. | Chờ nhóm điền |
| 3:00–4:30 | Từ cây sang frame, FEAT, entity, query có nguồn, fallback. | Chờ nhóm điền |
| 4:30–5:30 | Resolver theo loại, reset và ca không có ngữ cảnh. | Chờ nhóm điền |
| 5:30–7:30 | Demo, chỉ số, ca sai, giới hạn; Docker/gói nộp nếu đã kiểm. | Chờ nhóm điền |
| 7:30–8:00 | Nguồn tham khảo, AI và hướng mở rộng. | Chờ nhóm điền |

## Câu hỏi cần tự giải thích được

- Predictor/scanner/completer khác nhau thế nào? Vì sao phải xử lý node nullable đã hoàn tất trước trạng thái chờ?
- Vì sao `Tuần 3 học gì? xyz` phải bị từ chối? Cây ε được lưu thế nào?
- Nhánh `Q_*` và node `WEEK_ENTITY` giúp semantic tránh đọc lại câu gốc ra sao?
- FEAT_PARSING xác định PART_I thế nào? Thêm alias ở đâu và kiểm lại bằng gì?
- Phân biệt UNKNOWN, thiếu context và NOT_FOUND. Vì sao `Ai dạy NLP?` không trả tên người?
- Vì sao không cập nhật context khi query thất bại? Một câu hỏi phần BTL có làm mất chương đang nhớ không?
- Tỷ lệ 96,88% tính trên bao nhiêu câu? Vì sao không xem đó là độ chính xác trên câu hỏi mới?
- Cách xác nhận đủ 9 output và chạy được sau giải nén? Bước Docker nào đã thực hiện thật?

## Trạng thái chuẩn bị

Video tự động `dist/course-assistant-demo.mp4` dài 2 phút 8 giây, có phụ đề và dùng
kết quả thực thi của 7 câu. Có thể chạy `python tools/demo.py` để xem cùng chuỗi
câu hỏi ở terminal hoặc đọc [bản trace](demo-transcript.txt).

Tạo lại bằng `python tools/render_demo.py`; công cụ phát triển cần Pillow và
ffmpeg, font Segoe UI/Consolas trên Windows. Trên hệ khác dùng `--font` và
`--mono-font` trỏ tới font hỗ trợ tiếng Việt. Runtime Course Assistant vẫn chỉ
cần thư viện chuẩn. Còn phân vai thuyết trình và quyết định bản video nộp.
