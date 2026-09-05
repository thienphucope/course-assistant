# Nấc 1 — "Ngôn ngữ là gì?" (và cái chết của 2 câu trả lời ngây thơ)

> Tóm tắt dòng suy nghĩ Chomsky trước khi ông viết luật ngữ pháp nào.

## Định nghĩa cho máy
Một **ngôn ngữ** = **tập câu**, mỗi câu **dài hữu hạn**, ghép từ **tập từ hữu hạn**.
Nghịch lý lòi ra ngay:
- Tập từ: hữu hạn. Mỗi câu: hữu hạn. **Nhưng số câu: VÔ HẠN** ("Tôi biết bạn biết
  tôi biết…" nối mãi được).
- Não người: hữu hạn, nói được vô hạn câu.

→ **Câu hỏi trung tâm của cả ngành:** mô tả tập **vô hạn** bằng phương tiện
**hữu hạn** kiểu gì? Trong đầu phải có **cỗ máy hữu hạn sinh vô hạn**.

## Câu trả lời ngây thơ #1: liệt kê danh sách → CHẾT
Vô hạn thì không lưu nổi; và con người **hiểu được câu chưa từng nghe**. Danh sách
không giải thích nổi. → Ngôn ngữ **không phải kho câu**, mà là **quy trình sinh câu**.

## Câu trả lời ngây thơ #2: máy nối từ → CHẾT ở câu lồng nhau
Mô hình đơn giản nhất: sinh câu trái→phải, chọn từ sau dựa từ trước
(**finite-state / Markov**). Nhét xác suất vào → chính là **n-gram**, tổ tiên
"phe dữ liệu/phe lười" và cụ tổ xa của cách LLM đoán từ.

**Nhát dao Chomsky:** cặp "nếu … thì …" lồng nhau tùy sâu:
```
Nếu [ nếu [ nếu … thì … ] thì … ] thì tôi ở nhà.
```
Mỗi "nếu" đòi đúng một "thì", khớp như ngoặc lồng. Máy-nối-từ chỉ có **hữu hạn
trạng thái** → không đếm nổi "còn nợ mấy chữ *thì*" khi lồng sâu tùy ý → vỡ.

→ Ngôn ngữ có **phụ thuộc lồng nhau, tầm xa, sâu tùy ý**; không mô hình tuyến tính
nào bắt được. Câu **không phẳng** — nó **phân tầng (hierarchy)**, cụm trong cụm.

## Chốt
1. Ngôn ngữ = tập **vô hạn** → cần **máy hữu hạn** sinh ra.
2. Danh sách → chết. Máy-nối-từ → chết ở câu lồng.
3. Suy ra: câu có **cấu trúc phân tầng** → viết thành luật chính là **CFG** (Nấc 2+3).

> Ghi chú: Chomsky chỉ giết mô hình nối-từ **thời đó**. 2017 Transformer quay lại
> với "attention" — nhớ được tầm xa — vá đúng cái lỗ này. Con lắc Luật ↔ Dữ liệu.
