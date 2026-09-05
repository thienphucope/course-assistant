# Nấc 2+3 — Cỗ máy sinh câu của Chomsky (CFG, chiều XUÔI)

> Từ "câu phân tầng" (Nấc 1) → luật viết lại → CFG → sinh câu → cây.

## Quan sát khơi mào: từ dính chùm thành cụm (constituency)
Mẹo **phép thay thế**: "sinh viên giỏi học NLP" → thay cả cụm bằng "họ":
"**họ** học NLP" ✓. → "sinh viên giỏi" là **một khối** (constituent). Câu = **cụm
trong cụm**.

## Luật viết lại (rewrite rule)
`A → B C` = "một A **được viết lại thành** B rồi C". Mũi tên = "đẻ ra/gồm có",
KHÔNG phải "bằng".

Văn phạm tí hon:
```
1. S  → NP VP
2. NP → N
3. NP → N ADJ
4. VP → V NP
5. N   → sinh_viên | NLP | môn
6. ADJ → giỏi
7. V   → học
```

**Hai giống loài ký hiệu** (cốt tử):
| Loại | Là gì | Ví dụ | Đặc điểm |
|---|---|---|---|
| **Non-terminal** | tên chùm trừu tượng | S, NP, VP, N, V | còn viết lại tiếp |
| **Terminal** | từ thật | sinh_viên, học, NLP | **điểm dừng**, hết chẻ |

## Dẫn xuất (derivation): bấm luật đẻ câu
Từ hạt giống `S`, đập non-terminal tới khi sạch:
```
S → NP VP → N ADJ VP → sinh_viên ADJ VP → sinh_viên giỏi VP
  → sinh_viên giỏi V NP → sinh_viên giỏi học NP → sinh_viên giỏi học N
  → sinh_viên giỏi học NLP   ← DỪNG
```

## Cây rơi ra miễn phí
```
                 S
        ┌────────┴────────┐
       NP                VP
    ┌───┴───┐        ┌────┴────┐
    N      ADJ       V        NP
    │       │        │         │
sinh_viên  giỏi     học        N
                               │
                              NLP
```

## Luật CÂY (bạn hỏi đúng cái này)
- **Khung KHÔNG cố định** — mỗi câu chọn khung riêng (câu không tính từ thì `NP→N`, mất nhánh ADJ).
- **Bất biến ĐÚNG:** non-terminal luôn ở **nút bên trong (khung)**; terminal luôn ở
  **đáy (lá), điểm dừng, không chẻ tiếp**. Lý do: non-terminal = "còn chẻ", terminal = "hết chẻ".
- Đọc **hàng lá trái→phải = câu gốc** ("yield" của cây).

## Phép màu: đệ quy ⇒ VÔ HẠN
Thêm luật tự-trỏ: `NP → N "của" NP` → "tài liệu của môn của khoa của trường…"
không điểm dừng. **8 luật hữu hạn sinh vô hạn câu** — lời giải cho bức tường Nấc 1,
gói trong một chữ: **đệ quy (recursion)**.

## Định nghĩa hình thức CFG = bộ 4
| Ký hiệu | Tên | Ví dụ |
|---|---|---|
| **V** | non-terminal | {S, NP, VP, N, V, ADJ} |
| **Σ** | terminal (từ vựng) | {sinh_viên, học, NLP, giỏi, của, môn} |
| **R** | luật viết lại | 8 luật trên |
| **S** | ký hiệu bắt đầu | S |

**"Context-Free"** = vế trái mỗi luật chỉ **một non-terminal trơ trọi** → thấy `NP`
là đập được bất kể xung quanh. Đủ mạnh bắt cấu trúc lồng (thắng máy-nối-từ), đủ đơn
giản để chạy nhanh → **điểm ngọt**, nên 70 năm sau bài này vẫn xài.

## Nối về bài tập
`output/grammar.txt` = bộ 4 trên (terminal tiếng Việt miền môn học). `output/samples.txt`
= chạy dẫn xuất hàng loạt. Còn thiếu **chiều NGƯỢC** (câu→cây) = **Parser** = Nấc 4.
