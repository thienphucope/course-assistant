# Khái niệm xuyên suốt — Grammar vs KB (và Design-time vs Run-time)

> Không thuộc nấc Chomsky nào; là hiểu biết kiến trúc chạy ngang. Nút thắt hay
> gây rối nhất.

## 1. Grammar KHÔNG cần KB để gắn với nhau
Thứ gắn grammar lại = **chính các luật của nó** (`S → NP VP`…), không phải KB.

**Ẩn dụ: tờ ĐƠN vs cái TỦ hồ sơ.**
- **Grammar = tờ đơn tra cứu.** Bố cục do bạn thiết kế tay; có ô trống `[tuần ___]`.
  Thiết kế xong mà chưa cần mở tủ.
- **KB = tủ hồ sơ.** Ngăn kéo đánh số, nhồi dữ liệu, chẳng cần biết tờ đơn tồn tại.
- **Gặp nhau ở ĐÚNG 1 điểm = ô trống = ENTITY.** Điền "3" → anh thư ký (semantic+query)
  cầm đơn đi tới ngăn 3 rút nội dung. Thư ký là **chỗ DUY NHẤT** đơn chạm tủ.

**Hai ca chứng minh độc lập:**
| Câu | Grammar | KB | Kết quả |
|---|---|---|---|
| "Tuần **99** học gì?" | ✓ hợp lệ, ô=99 | ✗ không có ngăn 99 | parse OK → "không tìm thấy" |
| "Tuần 3 có **bài tập** nào?" | ✗ không có mẫu → `()` | (ngăn 3 CÓ data) | chặn ở grammar, khỏi hỏi KB |

→ Grammar lo **HÌNH DẠNG** câu; KB lo **NỘI DUNG**; nối bằng **entity**.

## 2. Design-time vs Run-time (chỗ 90% người lẫn)
- **XÂY (bạn, 1 lần lúc code):** đọc KB để viết luật — nhưng chỉ đọc **schema + vocab**.
- **CHẠY (máy, mỗi câu hỏi):** bước intent **KHÔNG đụng KB**; chỉ biến cây→predicate.
  KB bị đọc ở **bước sau (query)**.

## 3. KB có 3 lớp — chỉ cần đọc 2 lớp trên để XÂY
| Lớp | Là gì | Ví dụ | Ai đọc / khi nào |
|---|---|---|---|
| **① Schema** (nhãn ngăn) | KB có những LOẠI gì | "có lịch/tín chỉ/topic/deadline" | Bạn, design-time → quyết định **intent**. Bắt buộc. |
| **② Entity vocab** | TÊN hợp lệ + đồng nghĩa | NLP=CO3085; CFG… | Bạn nạp design-time; máy tra runtime. |
| **③ Data/facts** | nội dung THẬT | tuần 3 = [CFG, Parsing] | **Chỉ đọc ở QUERY — run-time.** |

Dựng grammar+intent chỉ cần ① + ②. KHÔNG cần thuộc ③.

## 4. Luồng runtime — ai chạm KB khi nào
```
câu → parse → intent        →  query        →  answer
              (KHÔNG đọc KB)    (ĐỌC KB ③)      (dùng kết quả)
              cây→predicate     chạm KB DUY NHẤT
```
"Có knowledge thì bóc, không thì rỗng" = hành vi bước **QUERY**, nằm **sau** intent.
Intent chỉ ghi phiếu "tìm week=99"; query mới lục tủ.

## 5. Data này KHÔNG thuần raw — 2 rổ
| Rổ | Folder | Bản chất | Máy có query không? |
|---|---|---|---|
| **KB thật** | `data/kb/` | nội dung môn học | **CÓ** — tủ để tra lúc chạy |
| **Phao** (scaffolding) | `data/scaffolding/` + `00_README.txt` | gợi ý để XÂY | **KHÔNG** — bạn đọc lúc code |

- `entities.txt` = lớp ① + ② dọn sẵn (**cho luôn cả list INTENT**).
- `sample_queries.txt` = test có nhãn đáp án (cho Phần IV).

## 6. Với DATA KHÁC thì sao? (câu hỏi tự mở rộng)
Ngoài đời không ai phát phao → **bạn phải tự bóc intent**:
1. Đọc data lạ → nó **trả lời được LOẠI gì** (schema①).
2. Nghĩ **người dùng hỏi gì** mà data đáp được.
3. **Intent = giao** `{data đáp được}` ∩ `{người dùng hỏi}`.
4. Tự bóc entity vocab② (tên, đồng nghĩa).

Ví dụ KB bệnh viện → tự đẻ `GET_LICH_KHAM, GET_BAC_SI, GET_CHI_PHI`. **Intent là
QUYẾT ĐỊNH THIẾT KẾ**, không tự rơi ra. `entities.txt` ở đây = bước 1–4 đã làm hộ.
