# T06 · 🔧 Cố định I/O giữa các tầng: hợp đồng + golden test

- **Trạng thái:** xong
- **Phụ trách:** Phúc
- **Ngày xong / Commit:** 22/10/2026 · commit chứa file này

## Đã làm

- [x] `docs/contracts.md`: cứng / lỏng cho từng tầng; bảng 26 nhánh → intent / entity / slots;
      bảng `kind` → `data` / `sources`; cấu trúc `KnowledgeBase`; luật dialogue; quy trình đổi
      hợp đồng.
- [x] `tools/make_golden.py`: chạy code nhánh `sample` (đóng băng) với `src/data/` hiện tại, ghi
      golden vào `src/tests/golden/` (2049 câu tokenizer/parser, 2027 cây → frame, 192 frame →
      result/answer, 6 hội thoại, 50 câu end-to-end, `kb.json`).
- [x] `src/tests/test_contract_*.py` (8 file) + `contract_support.py`: mỗi tầng test độc lập trên
      đầu vào golden của nó; tầng chưa làm → skip.
- [x] Sửa 3 kết quả của sample trong golden: output Phần II/III/IV phải `found = False`.
- [x] Hằng `NOT_FOUND` trong `answer.py` theo nguyên văn đề ("…trong dữ liệu **của** môn học.").

## Kiểm chứng

- Chạy bộ test bằng code sample: pass hết, trừ đúng 3 bản ghi bug đã sửa (test bắt được bug).
- Chạy trên skeleton `main`: toàn bộ test hợp đồng skip, không fail.

## Ghi chú

- Đổi `src/data/` (grammar, KB, câu test) → chạy lại `python tools/make_golden.py`.
- Không sửa tay golden; đổi hợp đồng theo `docs/contracts.md` §10.

## Thiết kế triển khai hiện tại

### Thiết kế oracle và kiểm thử độc lập
[`contracts.md`](../../contracts.md) cố định dữ liệu qua ranh giới, không cố định thuật toán hay mọi câu chữ. [`make_golden.py`](../../../tools/make_golden.py) lấy code đóng băng ở `sample` bằng `git archive`, chạy trong thư mục tạm với **data/grammar hiện tại của nhóm** rồi ghi fixture. Nó không import implementation đang kiểm làm oracle.

### Định dạng fixture
- `tokenizer.jsonl`: text → token, 2.077 bản ghi; `parser.jsonl`: câu → cây dạng `[label, child, ...]` hoặc null, 2.077 bản ghi.
- `semantic.jsonl`: 2.034 cây → frame; frame có intent/entity/slots/source_branch.
- `query.jsonl` và `answer.jsonl`: 205 frame. Query so found/kind/sources và data khi found; answer so loại fallback và fact bắt buộc, không buộc giống reference_answer từng chữ.
- `dialogue.jsonl`: 6 phiên, frame trước/sau resolve từng lượt. `cases.jsonl`: 64 câu, gồm 42 official và 22 challenge. `kb.json`: bảy collection, so giá trị và kiểu theo cấu trúc.

### Sửa baseline có kiểm soát
`extend_reference()` thêm nhóm FEAT và hai alias đã chốt trong hợp đồng. `run_query()` sửa ba case output Phần II/III/IV: sample trả fallback thì golden phải found=False. Adapter ở tooling, không sửa nhánh `sample`, không sửa tay golden để làm test xanh.

`reference_pass` trong cases giữ việc baseline end-to-end có trả lời đúng hay không; C018 là một lỗi baseline đã sửa ở query, nên bộ test in 1/3 improvement targets fixed. Hai target còn lại C007/C008 là giới hạn grammar. Không hiểu nhầm số này thành challenge chỉ đạt 1/3: tổng hiện là 20/22.

### Cách nghiệm thu và giới hạn
`contract_support.py` tái dựng Tree/frame/result và báo tối đa 10 mismatch. Helper có thể skip NotImplementedError cho skeleton; ở code hoàn thiện, toàn bộ 47 test hiện chạy không skip. Test counterexample trong `tests.test_audit_regressions` kiểm lỗi baseline có thể bỏ sót: thiếu slot resource, sai assignment, context sau LO, false acceptance và dữ liệu đánh giá hỏng.

Chạy `python tools/make_golden.py` khi đổi hợp đồng/data; sau đó chạy suite và xem diff fixture. Golden là baseline tương thích, không phải bằng chứng độc lập rằng tất cả logic baseline đúng. Không có golden khớp nguyên văn chín output; dùng T16/đóng gói để đối chiếu thêm.
