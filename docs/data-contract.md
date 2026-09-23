# Mốc 0 - hợp đồng dữ liệu và ID

Ngày chốt: 22/09/2026. Các quyết định dưới đây do nhóm chọn trước khi hoàn thiện parser, semantic và KB loader.

## 1. Nguồn dữ liệu khi chạy

`src/` là project root để chạy và đóng gói. `ProjectPaths.from_root(src)` trỏ tới `src/data/grammar.cfg`, `src/data/kb/` và `src/data/scaffolding/`. Sáu file KB và các câu mẫu, hội thoại, FAQ đầy đủ đã được đưa từ `data/` gốc vào `src/data/`; `src/data/` là **bản dùng lúc chạy và nộp**. `data/` gốc giữ nguyên làm bản tham chiếu nguồn, không được chương trình đọc xen kẽ. Khi sửa dữ kiện sau này, sửa bản chạy trong `src/data/` và ghi nguồn/thay đổi; đừng duy trì hai bản runtime khác nhau.

Giữ `src/data/grammar.cfg` là CFG của nhóm, không lấy grammar từ KB. `src/data/scaffolding/entities_reference.txt` là bản lexicon mô tả gốc; `src/data/scaffolding/entities.txt` là bảng alias → ID chuẩn cho mã nguồn. Nguồn và giới hạn của bộ dữ liệu ở `src/data/00_README.txt`: lịch 15 tuần, một số mốc BTL và quy định là dữ liệu **mẫu**, không phải lịch/quy định hành chính chính thức.

## 2. ID chuẩn và quy tắc nối dữ liệu

Không đổi ID đã xuất hiện trong KB và `sample_queries.txt`. Parser tạo cây; semantic lấy loại thực thể từ nhánh cây và chuẩn hóa cách gọi trong `entities.txt`; KB loader chuẩn hóa heading/key của file text sang cùng ID.

| Gia đình | Cách nói / cách ghi trong file | ID nội bộ | Nơi tra |
| --- | --- | --- | --- |
| Môn học | `NLP`, `Môn NLP`, `CO3085` | `CO3085` | `course_info.txt: course_id` |
| Tuần | `Tuần 3`, heading `WEEK 03` | `WEEK_03` | `schedule.txt` |
| Chương | `Chương 4`, `Chapter 4` | `CH04` | `topics.txt: chapter_id`; `schedule.txt: chapter` |
| Chuẩn đầu ra | `L.O.2.5`, `LO2.5` | `LO2.5` | `course_info.txt: detailed_learning_outcomes` |
| Bài tập lớn | `BTL`, `bài tập lớn` | `BTL01` | `assignments.txt: assignment_id` |
| Phần của BTL | `Phần I của BTL` | `PART_I` | heading `PART I` trong `assignments.txt` |
| Chủ đề | `CFG`, `PCFG`, `semantic grammar`, `reference` | `CFG`, `PCFG`, `SEMANTIC_GRAMMAR`, `REFERENCE` | `topics.txt`/`schedule.txt` |
| Quy định | `sử dụng AI`, key `AI_usage` | `AI_USAGE` | `regulations.txt` |
| Quy định | `LLM/RAG`, key `LLM_RAG` | `LLM_RAG` | `regulations.txt` |
| Tài liệu theo chủ đề | `statistical NLP`, `Python NLP` | `STATISTICAL_NLP`, `PYTHON_NLP` | tìm theo `title`/`usage` trong `resources.txt` |

`Phần I` xuất hiện ở cả nội dung môn học và BTL. Chỉ `ASSIGNMENT_PART` được chuẩn hóa thành `PART_I`; `COURSE_PART` dùng `COURSE_PART_I`. Semantic phải chọn gia đình từ nhánh cú pháp và ngữ cảnh câu, không tra alias toàn cục. Ví dụ Q012 “Phần I của BTL” dùng `PART_I`. Q003 “môn học gồm những phần nào” lấy `main_parts` của `course_info.txt`.

Các mã topic/resource là **khóa truy vấn**, không nhất thiết là trường ID vật lý trong file KB. Ví dụ `STATISTICAL_NLP` dùng để lọc tài liệu có `usage`/`title` liên quan. `PCFG` có thể xuất hiện ở nhiều chương/tuần; truy vấn nên giữ đủ kết quả. Với Q010, chỉ phần mô tả `LO4.2` trong `course_info.txt` là fact trực tiếp; liên kết LO4.2 → CH12 là suy luận bổ sung, không mặc nhiên coi là có trong KB.

## 3. Định dạng câu kiểm thử

Giữ **bốn cột bắt buộc** của bộ câu mẫu: `ID | QUERY | EXPECTED_INTENT | EXPECTED_ENTITY`. Cho phép thêm hai cột **tùy chọn** ở cuối: `EXPECTED_QUERY_STATUS | REQUIRED_ANSWER_TERMS`, trong đó nhiều mảnh đáp án ngăn bởi `;;`. `evaluate.py` hiện đọc cả dòng bốn lẫn sáu cột. Bản `sample_queries.txt` gốc giữ nguyên; `gold_queries.txt` thêm trạng thái và mảnh đáp án cho Q001–Q028; `challenge_queries.txt` chứa ca nhóm tự viết. Q029–Q034 thuộc hội thoại tùy chọn, không gộp vào điểm câu đơn.

Giá trị status: `FOUND` nếu có fact, `NOT_FOUND` nếu câu được hiểu nhưng KB thiếu fact, `OUT_OF_SCOPE` nếu parser không nhận câu. `OUT_OF_SCOPE` trong Q026–Q028 là nhãn **entity kỳ vọng**, không phải ngày hay fact trong KB. `QueryResult` có các trường `(query, found, kind, data, sources, reason)` và thuộc tính suy ra `status`; `kind` giữ loại truy vấn cụ thể như `SCHEDULE_CHAPTER` hoặc `DEADLINE`.

`sample_queries.txt` có Q001–Q025 câu lõi, Q026–Q028 ngoài miền và Q029–Q034 ba cặp có ngữ cảnh. Đánh giá dialogue riêng nếu làm Phần III. Trong bản dialogue dùng lúc chạy, một nhãn `PART_I_GRAMMAR_PARSER` của dữ liệu gốc được chuẩn hóa thành `PART_I` để khớp Q012/Q033/Q034; nội dung câu hỏi và đáp án giữ nguyên. `challenge_queries.txt` chứa ca nhóm tự viết `C001` về deadline cụ thể: grammar nhận câu, nhưng KB không có ngày nên phải trả `NOT_FOUND`.

## 4. Bảng truy vết và ranh giới dữ kiện

`docs/query-coverage.md` đối chiếu từng Q001–Q025 với nhánh `Q_*`, intent/entity, trường KB và phần grammar còn thiếu. Đây là bảng thiết kế tĩnh, chưa phải kết quả chạy parser. Khi code xong, bổ sung kết quả thực tế và dùng bảng để sửa lỗi.

Không tự tạo ngày deadline: `assignments.txt` chỉ mô tả yêu cầu BTL, `schedule.txt` chỉ có checkpoint theo tuần. Không có tên giảng viên trong sáu file KB. Những câu hỏi cần dữ kiện vắng mặt phải trả không tìm thấy. Nguồn KB là dữ liệu mẫu theo `00_README.txt`, nên README và báo cáo nộp bài phải nêu giới hạn đó.
