# Nấc 9 (optional) — Phần III (ngữ cảnh) & RAG + Đóng gói

> Lõi bắt buộc = I (grammar+parser) + II classical (semantic→answer) + IV (eval).
> Dưới đây ✨ điểm cộng — chỉ đụng khi lõi đã chắc, KHÔNG đánh đổi phần bắt buộc.

## Phần III — Local discourse context (ngữ cảnh hội thoại) ✨
Vấn đề: câu sau trỏ về câu trước — "Chương 4 nói gì?" → "**Nó** có liên quan
parsing?". "Nó" = CH04.
- Cần **history list**: nhớ entity vừa nhắc gần nhất.
- Gặp từ trỏ ("nó", "chương này", "chương sau", "phần này") → **resolve** về entity
  trong history ("chương sau" = CH_(n+1)).
- Test set: `data/scaffolding/dialogues.txt` (nhãn `EXPECTED_REFERENCE`). Đây là lý
  do dialogues **KHÔNG phải KB** (doc kb-loader) — payload là nhãn để chấm.
- Chính là ngữ cảnh **SHRDLU 1970** hiểu "nó" (doc 00 §5), thu nhỏ.

`output/dialogue.txt`.

## RAG / LLM — Phần II lựa chọn 2 ✨
- Chunk KB → embed → **retrieve** đoạn liên quan → nhét làm context cho LLM sinh đáp.
- `faq.txt` (Q→A theo chuỗi) là corpus tự nhiên cho hướng này (doc kb-loader).
- Phần IV khi đó thêm ca **hallucination**: LLM có bịa khi KB không có không? Phải đo.
- Nhớ doc 00 §6: đây là cái **đuôi "cho biết thời hiện đại"**, KHÔNG thay lõi cổ điển.

`output/retrieval.txt`.

## Đóng gói (bắt buộc, làm cuối) 🔧
- `README.md`: thành viên, cách chạy, mô tả kiến trúc / grammar / parser / semantic
  / intent / KB.
- `Dockerfile`: bài chấm bằng Docker.

---

## Bản đồ toàn pipeline (mục lục doc)
```
00 background     vì sao có 5 trạm
01 what-is-language   Nấc 1: vô hạn↔hữu hạn
02 cfg-and-generation Nấc 2+3: CFG, sinh câu, cây
03 grammar-vs-kb      ngang: entity nối grammar↔KB, design↔run-time
kb-loader            ngang: đọc data/kb/ thành tủ tra
04 parser            Nấc 4: câu→cây, backtracking
05 semantic-intent-entity  Nấc 5: cây→predicate
06 query-kb-answer   Nấc 6: predicate→KB→đáp, not-found
07 generator         Nấc 7: grammar→samples
08 evaluation        Nấc 8: chấm accuracy, phân tích ca sai
09 optional          Phần III + RAG + đóng gói
```
Việc code thật: xem `todo.md`.
