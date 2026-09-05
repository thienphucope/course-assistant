# Bài tập lớn NLP (CO3085) — Trợ lý hỗ trợ học tập (Course Assistant)

> Bản trích sạch từ `NLPAssignment-Course Assistant.pdf` (11 trang) để đọc nhanh.
> Trung thành với đề; phân tích/đề xuất kiến trúc xem `docs/architecture.md`.
> Đánh dấu của **đề**: `*` = phần mở rộng (Phần III); LLM/RAG = "không bắt buộc".

## 1. Giới thiệu
Xây một hệ thống **Course Assistant** trong **miền hẹp** (thông tin 1 môn học):
người dùng hỏi bằng ngôn ngữ tự nhiên để tra cứu/hỏi đáp. Vận dụng: văn phạm &
phân tích cú pháp; biểu diễn & diễn giải ngữ nghĩa; nhận diện ý định + thông tin;
truy xuất & hỏi đáp; ngữ cảnh hội thoại đơn giản; NLP dựa luật hoặc thống kê; mở
rộng LLM/RAG mức cơ bản. **Nhóm 3–4 sinh viên.**

## 2. Ngữ cảnh bài toán
Được cấp một **knowledge base** của môn học, có thể gồm: thông tin chung; đề cương;
lịch học/kế hoạch; nội dung chủ đề; thông tin bài tập; yêu cầu & thời hạn BTL; quy
định; tài liệu tham khảo.

Ví dụ câu hỏi: "Môn NLP có bao nhiêu tín chỉ?", "Tuần 5 học nội dung gì?", "Phần
CFG và Parsing ở tuần nào?", "Deadline BTL khi nào?", "Tài liệu nào nói về CFG?",
"BTL có được dùng công cụ AI không?".

Hỗ trợ cả **ngữ cảnh cục bộ**: "Tuần 5 học gì?" → … → "Tài liệu của **phần này** ở
đâu?" (phải hiểu "phần này" từ lượt trước). Phạm vi **giới hạn trong miền dữ liệu**
— không cần trả lời câu ngoài miền.

## 3. Phần I — Văn phạm & Parser  *(bắt buộc)*

### 3.1 Viết rule/văn phạm cho miền
Văn phạm tối thiểu phủ các nhóm: hỏi **thông tin chung**; **nội dung/chủ đề**; **lịch
học**; **thông tin bài tập**; **thời hạn**; **tài liệu**; **quy định**; và một số câu
liên quan trong miền.
- **Input**: dữ liệu nội bộ (file grammar trong `data/` hoặc `models/`).
- **Output**: `output/grammar.txt`

### 3.2 Giải thuật sinh câu
Dùng văn phạm sinh câu hợp lệ. Mỗi dòng 1 câu; phải hợp văn phạm; **tối đa 10.000
câu**.
- **Output**: `output/samples.txt`

### 3.3 Bộ phân tích cú pháp (parser)
- **Input**: `input/sentences.txt` (mỗi dòng 1 câu).
- **Output**: `output/parse-results.txt` — mỗi câu hợp lệ → **cây cú pháp**; câu
  không hợp lệ / ngoài văn phạm → in `()`.

## 4. Phần II — Diễn giải ngữ nghĩa & Course Assistant  *(bắt buộc, chọn 1 hướng)*
Dựa trên Phần I. Chọn **1 trong 2**; cả hai đều **phải dùng & thể hiện kết quả Phần I**.

### 4.1 Lựa chọn 1 — Classical/Statistical NLP
Chuỗi xử lý:
```
Input → Parsing → Semantic Representation → Intent/Entity → Query → Knowledge Base → Answer
```
Các loại truy vấn định trước (ví dụ): `GET_COURSE_INFO`, `GET_TOPIC`, `GET_SCHEDULE`,
`GET_ASSIGNMENT`, `GET_DEADLINE`, `GET_RESOURCE`, `GET_RULE`.

Các bước + output:
1. **Biểu diễn ngữ nghĩa**: câu (sau parse) → predicate. VD "Môn NLP có bao nhiêu
   tín chỉ?" → `GET_CREDIT(course=NLP)`; "Deadline BTL?" → `GET_DEADLINE(assignment=
   PROJECT)`. → `output/semantic.txt`
2. **Intent + thông tin**: xác định loại yêu cầu + thông tin cần tra. Dùng **luật /
   keyword matching / thống kê / ML** tùy ý. **Không yêu cầu Deep Learning/LLM.** →
   `output/intent-entity.txt`
3. **Query tới KB**: từ semantic → truy vấn dữ liệu. → `output/query.txt`
4. **Truy xuất & sinh câu trả lời**. → `output/answer.txt`
5. **Không tìm thấy**: nếu KB không có / ngoài phạm vi → **thông báo phù hợp**, KHÔNG
   tự tạo thông tin. VD: "Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu
   của môn học."

### 4.2 Lựa chọn 2 — Mở rộng LLM/RAG
**Không phải yêu cầu bắt buộc** (phần mở rộng). Tối thiểu:
```
User Question → Retrieve relevant info → Retrieved Context → LLM → Answer
```
Các bước: (1) cơ chế truy xuất; (2) prompt/context cho LLM; (3) sinh đáp từ thông
tin truy xuất; (4) nếu được, dẫn nguồn; (5) xử lý không tìm thấy.
**Không bắt buộc**: Agent/Multi-Agent, tool calling phức tạp, fine-tuning, huấn
luyện LM, RAG quy mô lớn, kiến trúc DL phức tạp. Được dùng model/thư viện công khai
nhưng phải trình bày rõ cách dùng & hiểu pipeline.
- **Output tối thiểu**: `output/retrieval.txt`, `output/answer.txt` (câu hỏi vào; tài
  liệu truy xuất; câu trả lời).

## 5. Phần III* — Xử lý ngữ cảnh hội thoại cục bộ  *(mở rộng, không bắt buộc)*
Xử lý tương tác liên tiếp dùng thông tin lượt trước ("phần này" ← nội dung vừa trao
đổi). **Không cần Dialogue Manager phức tạp** — chỉ vài trường hợp tham chiếu định
trước.
- **Output**: `output/dialogue.txt` — hội thoại vào; ngữ cảnh dùng; kết quả diễn
  giải; câu trả lời.

## 6. Phần IV — Đánh giá hệ thống  *(bắt buộc)*
Xây tập kiểm thử bao phủ: câu hợp lệ; **các cách diễn đạt khác nhau** của cùng 1 yêu
cầu; câu **ngoài phạm vi**; câu **KB không có thông tin**; (nếu làm Phần III) câu có
ngữ cảnh.

Báo cáo tối thiểu: số câu kiểm thử; số câu đúng; **độ chính xác**/chỉ số phù hợp; một
số ca **trả lời sai**; **phân tích nguyên nhân lỗi**; ưu/nhược của phương pháp.
Nếu LLM/RAG: thêm ví dụ đáp đúng-có-căn-cứ, câu KB không có, và ca **hallucination**.
- **Output**: `output/evaluation.txt`

## 7. Yêu cầu khác
- **7.1 Ngôn ngữ/môi trường**: **Java hoặc Python**. Phải chạy được trong môi trường
  quy định + hướng dẫn cài/chạy đầy đủ. **Docker** dùng để chấm → nộp `Dockerfile`.
- **7.2 Dữ liệu**: BTC cấp KB chung. Được bổ sung data kiểm thử nhưng **ghi rõ nguồn**,
  không đổi bản chất bài, không tạo đáp ngoài phạm vi.
- **7.3 Giới hạn thư viện**: được dùng thư viện NLP/ML công khai. **Classical: KHÔNG
  được dùng LLM thay toàn bộ xử lý NLP cốt lõi.** LLM/RAG: phải mô tả rõ model / cách
  truy xuất / cách dựng prompt / cách đánh giá.
- **7.4 Nộp bài**: `MSSV1-MSSV2-MSSV3-MSSV4.zip`, gồm tối thiểu:
  ```
  project/
    src/       mã nguồn
    data/      dữ liệu cần thiết
    models/    model/config nếu có
    input/     dữ liệu đầu vào mẫu
    output/    kết quả chạy thử
    README.md  hướng dẫn cài & chạy
    Dockerfile môi trường chạy
  ```
  Zip **< 10MB**; file/model lớn → upload nơi khác + link trong README.
- **7.5 README.md** mô tả tối thiểu: thành viên; cài đặt; cách chạy; **kiến trúc**;
  **grammar**; **parser**; **semantic**; **intent/entity**; **KB & cách truy vấn**;
  lựa chọn Classical/Statistical hoặc LLM/RAG; cách đánh giá; **hạn chế**.
- **7.6 Báo cáo & Demo**: nộp source, README, output, **báo cáo**, **video demo ngắn**.
  Video thể hiện: nhận câu hỏi; xử lý chính; kết quả phân tích/semantic; câu trả lời;
  1 ca không trả lời được. (LLM/RAG: thêm truy xuất + context.) Có thể được gọi
  **thuyết trình** (tuần 13–14, 5–10 phút/nhóm).

## 8. Trung thực học thuật
Tự làm & **hiểu rõ** code/thuật toán. Được tham khảo giáo trình, tài liệu khoa học,
thư viện/framework công khai, công cụ AI theo quy định — nhưng phải kiểm tra & giải
thích lại được. **Không dùng hệ thống mình không hiểu để thay toàn bộ phần NLP.**
Cấm: sao chép code giữa nhóm; chia sẻ phần quan trọng; dùng API/hệ có sẵn thay toàn
bộ thành phần NLP bắt buộc; trình bày thứ không hiểu. Ghi rõ nguồn ngoài.

## 9. Sản phẩm cuối cùng
Phải thể hiện **pipeline NLP hoàn chỉnh**:
```
Natural Language Input → Grammar/Parser → Syntactic Representation
  → Semantic Interpretation → Intent/Entity → Knowledge Base/Retrieval → Answer
```
Có thể mở rộng `Knowledge Base → Retrieval → LLM → Grounded Answer`, **nhưng LLM/RAG
KHÔNG thay các yêu cầu NLP cốt lõi**. Mục tiêu: áp dụng kiến thức NLP để phân tích,
xây dựng và **đánh giá** một hệ thống trong miền cụ thể.
