# Nấc 6 — Query → KB → Answer (run-time: chạm tủ, đổ đáp, không bịa)

> Có predicate `GET_SCHEDULE(week=3)` (Nấc 5). Giờ mới **mở tủ** (KB). Đây là chỗ
> DUY NHẤT của toàn pipeline chạm KB (doc 03).

## 3 bước
1. **Query**: predicate → dùng **loader-index** (doc kb-loader) tra bằng **entity
   làm khóa**. `week=3` → `schedule_index[3]`.
2. **Có / không**: "có thì bóc, không thì rỗng".
3. **Answer**: đổ kết quả vào **template theo intent** → câu trả lời tiếng người.

## Not-found = báo lịch sự, TUYỆT ĐỐI không bịa
Spec (faq Q13): không thấy trong KB → **thông báo không có**, không tự chế. Đây là
lời hứa "hộp kính" của cả kiến trúc (doc 00 §6). Hai kiểu rỗng, chặn ở hai nơi:
| Ca | Chặn ở đâu |
|---|---|
| "Tuần **99** học gì" (grammar OK, KB không có ngăn 99) | rỗng ở **QUERY** → "không tìm thấy" |
| "Tuần 3 có **xyz**" (sai hình dạng) | `()` ở **PARSER** → "không hiểu/không hỗ trợ" |

(doc 03 bảng 2 ca — cùng gốc: grammar lo hình dạng, KB lo nội dung.)

## Template theo intent
Mỗi intent một khuôn câu, chừa chỗ đổ data:
```
GET_SCHEDULE → "Tuần {week} học {chapter}: {topics}."
GET_COURSE_INFO(credits) → "Môn {course} có {credits} tín chỉ."
```
Data thật lấy từ loader. **KHÔNG ghép chữ tự do** → giữ đáp án bám KB, không phóng
tác (nếu không lại rơi vào "bịa" mà cả kiến trúc đang tránh).

## Vì sao đây là plumbing 🔧
Không có quyết định thiết kế lớn — đọc index, kiểm rỗng, đổ template. Ít trí tuệ,
nhiều **cẩn thận** (nhất là nhánh not-found) (doc 00 §7).

## Nối bài tập
`output/query.txt` (truy vấn dựng ra), `output/answer.txt` (đáp cuối). Cần
**loader** (doc kb-loader) làm nền.
