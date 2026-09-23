# Mốc 2 - Grammar, parser và sinh câu

Mốc 1 chứng minh **một câu** đi từ input đến đáp án. Mốc 2 hoàn thiện **Phần I của đề**: grammar phủ các nhóm câu, parser xuất cây hoặc `()`, generator sinh câu từ chính grammar đó. Semantic/KB cho toàn bộ nhánh vẫn là việc của các mốc sau.

## Chạy Phần I

Từ thư mục `src/`:

```powershell
python -X utf8 run.py --root . part1
```

Trong môi trường Codex hiện tại, nếu `python` không có trên PATH:

```powershell
& 'C:\Users\huyba\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run.py --root . part1
```

Lệnh mặc định sinh tối đa 10.000 câu. Để thử nhanh, dùng `part1 --limit 100`.

Lệnh đọc `data/grammar.cfg` và `input/sentences.txt`, rồi ghi:

| File | Nội dung |
| --- | --- |
| `output/grammar.txt` | Bản văn phạm dùng cho lần chạy. |
| `output/samples.txt` | Mỗi dòng một câu sinh từ CFG; không quá 10.000 dòng. |
| `output/parse-results.txt` | Mỗi dòng là cây của câu tương ứng trong `input/sentences.txt`, hoặc `()` nếu ngoài grammar. |

`input/sentences.txt` hiện gồm 25 câu lõi Q001–Q025, 3 câu ngoài miền Q026–Q028 và một câu tự bổ sung hỏi ngày deadline. Câu deadline có **cú pháp hợp lệ**, dù KB không có ngày nộp; parser chỉ quyết định tính hợp grammar, không quyết định có dữ kiện trả lời hay không.

## Những đoạn code chính

1. `grammar.py:Grammar.from_file/from_text` đọc `%start S`, các luật `A -> ... | ...`, terminal trong dấu nháy và nhánh rỗng (epsilon). Nó kiểm tra ký hiệu chưa định nghĩa và lưu các rule theo vế trái. File nguồn là `data/grammar.cfg`.
2. `tokenizer.py:tokenize` chuẩn hóa Unicode/chữ hoa và tách dấu câu. Ví dụ `L.O.2.5` trở thành terminal `lo2.5`, còn `?` là một token riêng. Parser và grammar loader dùng cùng quy tắc terminal này.
3. `parser.py:EarleyParser.parse` giữ các trạng thái trong bảng theo vị trí token. Nó dự đoán luật có thể đi tiếp, so terminal với token hiện tại, rồi ghép các nhánh đã hoàn thành thành `Tree`. Nó chỉ chấp nhận khi một cây `S` phủ **toàn bộ** câu; từ dư làm kết quả thành `()`.
4. `generator.py:SentenceGenerator.generate` đi từ ký hiệu bắt đầu `S`, lần lượt thay nonterminal bằng các rule của **cùng `Grammar` object**. Nó duyệt có giới hạn, bỏ câu trùng, chặn số token/trạng thái và chặn cứng 10.000 câu. `detokenize` ghép terminal thành câu dễ đọc.
5. `cli.py` gọi parser/generator, còn `output.py` ghi ba file theo đúng thứ tự. Lệnh `part1` không gọi semantic hay KB; đây là đầu ra Phần I.

Ví dụ một đoạn grammar đã thêm để phủ cách hỏi khác nhau mà không chép nguyên từng câu mẫu:

```text
Q_COURSE_CREDITS -> COURSE_ENTITY "có" CREDIT_QUESTION
CREDIT_QUESTION -> CREDIT_QUANTITY "tín" "chỉ"
CREDIT_QUANTITY -> "bao" "nhiêu" | "mấy"
```

Nhờ vậy “Môn NLP có bao nhiêu tín chỉ?” và “CO3085 có mấy tín chỉ?” dùng chung cấu trúc hỏi tín chỉ. Grammar giữ **kiểu câu**, không chứa đáp án `3 tín chỉ`.

## Kết quả và cách hiểu

- Q001–Q025: **25/25** câu lõi parse được. Bảy nhóm bắt buộc đều có câu hợp lệ; nhóm deadline được kiểm bằng ca tự bổ sung C001.
- Q026–Q028: **3/3** câu ngoài miền bị từ chối và ghi `()`.
- `part1` trên input hiện có: **26 cây / 29 câu**, ba dòng còn lại là `()`.
- `samples.txt`: **10.000 dòng khác nhau**, tất cả parse lại được bằng cùng CFG; khi sinh đủ 10.000, cả 29 nhánh `Q_*` hiện có đều xuất hiện. File khoảng 0,55 MB.
- Bộ test tại thời điểm hoàn thành mốc này: kiểm tra cú pháp, dữ liệu, semantic của lát cắt mốc 1 và tính chất generator. Các test end-to-end cho mọi intent và dialogue vẫn chờ các mốc sau.

**Quan trọng:** 25/25 ở đây là **độ phủ cú pháp**, không phải 25/25 câu đã được trả lời đúng. Hiện `semantic.py` mới chuyển nhánh `Q_SCHEDULE_WEEK` thành yêu cầu tra KB; các nhánh mới như `Q_TOPIC_LOCATION`, `Q_LO_CONTENT`, `Q_RULE_PERMISSION` đang trả `UNSUPPORTED` cho đến Mốc 3–4.
