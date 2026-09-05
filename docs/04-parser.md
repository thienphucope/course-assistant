# Nấc 4 — Parser: câu → cây (đi ngược, và cái giá của nó)

> Chiều XUÔI (sinh câu, doc 02) xong. Giờ chiều NGƯỢC: cầm câu, dựng lại cây.
> Chính là "đầu bếp nếm món rồi dựng lại công thức" (doc 00 §3).

## Vì sao đi-ngược KHÓ hơn đi-xuôi
- **Xuôi** (generate): cầm luật, tự chọn nhánh, đập tới khi ra chữ — mỗi bước bạn
  CHỦ ĐỘNG, không sợ sai.
- **Ngược** (parse): cầm chuỗi chữ, phải ĐOÁN nó ráp từ luật nào. Nhiều luật cùng
  đẻ được khúc đầu → phải **THỬ**. Đoán sai → cụt → **lùi** thử cách khác.

Đó là **backtracking (thử–sai–lùi)**. Ẩn dụ: xuôi = nấu theo công thức; ngược =
nhìn món lạ, thử "chắc luộc?" nếm sai, thử "chắc hấp?"… tới khi khớp.

## Top-down + backtracking (recursive-descent) — đủ cho bài này
1. Bắt đầu từ **S**. Khớp `S → NP VP`: thử khớp NP ở đầu chuỗi, rồi VP ở phần còn lại.
2. Non-terminal nhiều luật → thử luật 1; con trỏ token kẹt → **lùi**, thử luật 2…
3. Terminal → so đúng chữ ở con trỏ; khớp thì **nuốt 1 token**, tiến con trỏ.

## Điều kiện HỢP LỆ (chặt — đừng quên vế 2)
Cây hợp lệ ⇔ (a) truy được về **S** **VÀ** (b) **ăn HẾT token**.
- Token thừa: "tuần 3 học gì **xyz**" → parse xong còn dư → **FAIL**.
- Token thiếu: hết chữ mà luật còn đòi → **FAIL**.

→ "Khớp được phần đầu" KHÔNG tính. Phải trọn vẹn cả câu.

## Trace nhỏ (thử–sai–lùi thật, văn phạm tí hon doc 02)
Câu: `sinh_viên học NLP`
```
S→NP VP ; NP: thử luật "N ADJ" → khớp N=sinh_viên, đòi ADJ nhưng gặp "học" ✗
         → LÙI, thử luật "N" → NP=[sinh_viên] ✓ (con trỏ ở "học")
        VP→V NP → V=học ✓ → NP→N → N=NLP ✓ → hết token ✓ → NHẬN
```
Cái nhánh ADJ thử-rồi-bỏ chính là backtracking.

## Ngoài grammar → `()` (từ chối, không bịa)
Không cách ráp nào ăn hết token → câu **ngoài grammar** → xuất cây rỗng `()`.
Đây là "chặn ở grammar" của doc 03: câu sai **HÌNH DẠNG** dừng ngay đây, chưa kịp
hỏi KB. Là cơ chế **không-bịa** ở tầng cú pháp.

## Nhập nhằng: 1 câu, nhiều cây
Grammar cho >1 cây cho cùng câu = **ambiguity**. Bài này lấy **cây đầu tiên** tìm
được là đủ — đừng vẽ; chọn cây theo xác suất (PCFG, Chương 6) là chuyện optional.

## Parser gần như MỘT-ĐƯỜNG ⚙️
Thuật toán chuẩn, viết đúng **1 lần dùng mãi**, KHÔNG phụ thuộc số intent. Thêm
intent → sửa **grammar**, KHÔNG sửa parser (doc 00 §7). Vì thế nó ⚙️, không 🔥.

## Nối bài tập
`output/parse-results.txt` = mỗi câu → cây (hoặc `()`). Là **đầu vào cho Nấc 5**
(cây → nghĩa).
