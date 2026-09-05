# Nấc 7 — Generator: sinh câu từ grammar (đi xuôi, tự động, có phanh)

> Đảo của parser. Parser: câu→cây. Generator: grammar→câu. Chính là **dẫn xuất**
> (doc 02) chạy tự động hàng loạt. Một grammar, hai chiều dùng.

## Làm gì
Từ **S**, đệ quy đập non-terminal (chọn nhánh ngẫu nhiên/duyệt hết), tới khi toàn
terminal → 1 câu hợp lệ. Lặp để phủ nhiều khung → bộ câu mẫu.

## Vì sao cần phanh (≤10.000 câu)
Grammar có **đệ quy = vô hạn câu** (doc 02, luật tự-trỏ). Sinh mù → chạy mãi. Phải
cắt:
- giới hạn **độ sâu đệ quy**, hoặc
- giới hạn **tổng số câu** (spec: ≤10.000).

`ponytail`: cap cứng tổng số câu là đủ, đừng cầu kỳ sampling.

## Dùng để làm gì (không phải nộp cho có)
1. **Soi grammar**: đọc câu sinh ra → thấy câu vô lý → biết luật lỏng, vá lại.
2. **Round-trip test parser**: generate → parse lại → phải ra cây (nguồn đầu vào
   sạch cho evaluation, Nấc 8).
3. Bằng chứng grammar **phủ đủ** các cách hỏi.

## Nối bài tập
`output/samples.txt`. Cùng bộ 4 grammar với parser (doc 04) — viết grammar một
lần, parser đọc & generator đọc.
