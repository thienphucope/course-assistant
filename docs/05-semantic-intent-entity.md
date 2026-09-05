# Nấc 5 — Cây → nghĩa: predicate = intent + entity

> Có cây (Nấc 4) rồi. Nhưng "ráp đúng ≠ hiểu" (doc 00 §4): cây mới là HÌNH DẠNG,
> chưa là Ý ĐỊNH. Trạm này dịch **cây → predicate**.

## Sản phẩm cần rút: predicate
`GET_SCHEDULE(week=3)`. Gồm 2 mảnh, cả 2 **đã cài sẵn trong cây** nếu grammar
thiết kế đúng:
- **intent** = hỏi *loại* gì.
- **entity** = hỏi về *cái cụ thể* nào.

## Grammar quyết định điều này DỄ hay KHÓ (chốt thiết kế)
Khung đã chốt: `S → PRE Q POST`.
- **PRE/POST** = tiểu từ lịch sự/kết câu ("cho mình hỏi", "ạ", "vậy") — **rỗng
  nghĩa** → bước này **vứt thẳng**, không vào predicate.
- **Q rẽ theo intent**: `Q → Q_SCHED | Q_TOPIC | …`, mỗi nhánh chứa **ô trống =
  entity**.

Nhờ vậy:
| Mảnh | Rơi ra từ đâu |
|---|---|
| intent | **nhãn nút con của Q** (`Q_SCHED` → GET_SCHEDULE) — 1 bảng ánh xạ |
| entity | **terminal điền ô trống** (`WEEK`→"3"), chuẩn hóa qua entities.txt → WEEK_03 |

→ Cả hai **rơi ra từ cây**, không phải đoán. Đây là phần thưởng của việc đổ công
vào grammar ("cây rơi ra miễn phí", doc 02).

## Thuật toán (đơn giản đến bất ngờ)
1. Duyệt cây, tìm nút **Q**, đọc nhãn nhánh con → tra bảng → **intent**.
2. Trong nhánh đó, gom terminal ở các slot → chuẩn hóa bằng **entity vocab**
   (entities.txt ②) → **entity**.
3. Câu là `()` (Nấc 4 từ chối) hoặc không khớp intent nào → **UNKNOWN**.

## Classical vs Statistical — chọn 1 (đã chốt: Classical)
- **Classical** (bài này): intent/entity suy từ **cấu trúc cây + keyword/luật**.
  KHÔNG cần ML hay dữ liệu huấn luyện. Rõ ràng, không bịa.
- **Statistical**: học từ dữ liệu gán nhãn (đếm/ML) để **thay** tầng này. Là hướng
  thay thế, không chạy song song.

(doc 00 §7: đây là chỗ rẽ 🔀 lớn thứ nhì của cả pipeline.)

## KHÔNG đụng KB ở đây
Nhắc doc 03 §2: bước này chỉ cây→predicate. Predicate mới là **"phiếu yêu cầu"**
(tìm week=3). Lục tủ là việc của QUERY (doc 06). Trộn 2 cái = nguồn rối #1.

## Nối bài tập
`output/semantic.txt` (predicate), `output/intent-entity.txt` (nhãn intent +
entity trích). Là đầu vào cho query.
