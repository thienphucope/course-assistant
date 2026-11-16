# T05 · 🔧 Quyết định về pipeline trong PR #2 (Bách)

- **Trạng thái:** xong
- **Phụ trách:** Phúc (lead)
- **Ngày xong / Commit:** 22/10/2026 · commit chứa file này

PR #2 tự hiện thực toàn bộ pipeline (loader, tokenizer, parser, semantic, KB, query, answer,
evaluate, CLI), 12 file docs, 9 file test (50 test pass) — ngoài phạm vi phase 1.

## Quyết định

**Codebase chuẩn = skeleton trên `main`** (`src/hcmut/iaslab/nlp/app/`, dựng theo bản tham
khảo ở nhánh `sample`). Không dùng code của PR #2 làm nền; PR #2 đóng, không merge.

Lý do:
- Skeleton đã cố định I/O giữa các tầng (`docs/contracts.md`) và có golden test cho từng tầng —
  cả nhóm code theo một khung, nghiệm thu bằng máy.
- Tokenizer của PR #2 tách `context-free` thành 3 token, lệch grammar `src/data/grammar.cfg`
  (232 câu sinh ra không parse lại được); PR #2 cũng viết lại `entities.txt`,
  `sample_queries.txt`, `dialogues.txt` theo format riêng.

## Phần của PR #2 vẫn dùng được

- Phần grammar (entity list, `môn học`, `tài liệu tham khảo…`) đã gộp vào `main` —
  `T03-grammar-phase1.md` mục 3.2.
- Code trong PR có thể **chuyển dần vào đúng module của skeleton** khi Bách nhận task tầng
  tương ứng: cách làm bên trong mỗi tầng là tự do, miễn pass test hợp đồng của tầng đó
  (`docs/contracts.md`).

## Thiết kế triển khai hiện tại

### Quyết định kiến trúc
Chọn package [`src/hcmut/iaslab/nlp/app/`](../../../src/hcmut/iaslab/nlp/app) làm codebase chung. Từng tầng triển khai trong module của mình và trao đổi `Tree`, `SemanticFrame`, `QueryResult`, `PipelineResult`. Skeleton xuất phát từ `3358550`; có thể tham khảo code `sample` nhưng không thay toàn bộ nền bằng nhánh PR #2.

### Các ranh giới giữ ổn định
Tokenizer tạo terminal cho grammar; parser dựng cây có nhãn; semantic đọc cây và alias, không đọc KB; query dùng frame để tìm fact trong KB đã nạp; answer render result; context bao quanh query/answer theo thứ tự T16. Cách cài bên trong được thay đổi nếu giữ các hợp đồng này.

Quyết định giải quyết xung đột giữa các implementation có tokenizer, entity ID và cấu trúc dữ liệu khác nhau. Chuyển một thuật toán từ nhánh tham khảo phải đặt đúng module, giữ I/O và qua golden lẫn ca phản ví dụ; không chỉ dựa vào test tự viết trong nhánh đó.

### Đối chiếu và nguồn
`pipeline.py` dựng `PipelineComponents`; `requirements.txt` chỉ có chú thích, lõi chạy bằng thư viện chuẩn Python. Runtime chọn Classical NLP, không gọi LLM để thay parser/semantic/query. Code T12/T13 tích hợp ở `95df6db`; các tầng đã hoàn thiện tiếp trên cùng skeleton. Nguồn tham khảo và hỗ trợ AI nằm trong báo cáo/README, nhóm vẫn cần review và tự giải thích code.

**Nghiệm thu:** test hợp đồng từng tầng và test end-to-end. Việc thông qua codebase không tự xác nhận chất lượng mọi cách hỏi hoặc Docker; các phần đó có nghiệm thu riêng.
