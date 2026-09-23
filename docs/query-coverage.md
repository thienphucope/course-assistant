# Đối chiếu câu hỏi mẫu với CFG và kho tri thức

Nguồn kiểm tra: `src/data/scaffolding/sample_queries.txt`, `src/data/grammar.cfg` và sáu file trong `src/data/kb/`. Các file này đã được đồng bộ từ bộ dữ liệu mẫu gốc. Bảng “CFG seed” phía dưới ghi trạng thái **trước khi mở rộng grammar ở Mốc 2** để thấy vì sao từng luật được thêm. Tokenizer đã chuẩn hóa `L.O.2.5` thành token `lo2.5`; dấu `?` được `SUFFIX` chấp nhận.

**Kết quả hiện tại:** Q001–Q025 được nhận dạng 25/25, cho đúng nhãn intent/entity của bộ mẫu và có đáp án kèm nguồn KB. Ba câu ngoài miền Q026–Q028 bị từ chối, cho cây `()` và intent `UNKNOWN`. Sáu câu hội thoại Q029–Q034 cũng được grammar nhận dạng, nhưng các nhánh phụ thuộc ngữ cảnh còn chờ phần tùy chọn. Ca tự bổ sung C001 được hiểu là `GET_DEADLINE`/`BTL01` và trả không tìm thấy ngày nộp cụ thể.

`intent/entity` là nhãn có sẵn trong bộ câu hỏi mẫu. `Q_*` là nhánh cú pháp, không đồng nhất với intent: nhiều nhánh có thể cùng ánh xạ đến một intent. ID trong cột entity phải được giữ nguyên hoặc có phép chuẩn hóa công khai giữa semantic và KB.

## Q001–Q025: bộ câu đơn lõi

| ID | Câu hỏi rút gọn | Nhánh `Q_*` hiện có / đề xuất | Intent / entity kỳ vọng | Fact cần tra trong KB | CFG seed |
| --- | --- | --- | --- | --- | --- |
| Q001 | Môn NLP có bao nhiêu tín chỉ? | `Q_COURSE_CREDITS` | `GET_COURSE_INFO` / `CO3085` | `course_info.txt`: `course_id`, `credits = 3` | **Mở rộng** `COURSE_ENTITY` với “môn NLP” |
| Q002 | CO3085 có mấy tín chỉ? | `Q_COURSE_CREDITS` | `GET_COURSE_INFO` / `CO3085` | `course_info.txt`: `credits = 3` | **Mở rộng** `CREDIT_QUESTION` với “mấy tín chỉ” |
| Q003 | Môn học gồm những phần nào? | `Q_COURSE_PARTS` | `GET_COURSE_INFO` / `CO3085` | `course_info.txt`: `main_parts` (3 phần của môn học) | **Mở rộng** `COURSE_ENTITY` với “môn học”; cần hiểu đây là *phần của môn*, không phải phần của BTL |
| Q004 | Tuần 3 học gì? | `Q_SCHEDULE_WEEK` | `GET_SCHEDULE` / `WEEK_03` | `schedule.txt`: `WEEK 03` → `chapter: Chapter 3`, `topics` | **Khớp** |
| Q005 | Chương 4 học vào tuần nào? | `Q_SCHEDULE_CHAPTER` | `GET_SCHEDULE` / `CH04` | `schedule.txt`: `WEEK 04` và `WEEK 05` cùng có `chapter: Chapter 4`; cần trả đủ hai tuần | **Khớp** |
| Q006 | Chương nào nói về CFG? | `Q_TOPIC_BY_NAME` | `GET_TOPIC` / `CFG` | `topics.txt`: `CH03` có `keywords: CFG` và mục `3.1 Context-Free Grammars`; `schedule.txt` cũng nhắc CFG ở tuần 3 | **Khớp** |
| Q007 | PCFG được học ở đâu? | Đề xuất `Q_TOPIC_LOCATION` (hoặc mở rộng nhóm `Q_TOPIC_BY_NAME`) | `GET_TOPIC` / `PCFG` | `topics.txt`: `CH03` mục 3.2 và `CH06` mục 6.5; `schedule.txt`: `WEEK 03`, `WEEK 07`. “Ở đâu” chưa chốt nghĩa là chương, tuần hay cả hai | **Mở rộng** mẫu “được học ở đâu”; thêm `PCFG` vào `TOPIC_ENTITY` |
| Q008 | Chương nào nói về semantic grammar? | `Q_TOPIC_BY_NAME` | `GET_TOPIC` / `SEMANTIC_GRAMMAR` | `topics.txt`: `CH10`, `keywords` và mục `10.2 Semantic grammars` | **Khớp** (`TOPIC_ENTITY -> "semantic" "grammar"`) |
| Q009 | L.O.2.5 là gì? | `Q_LO` | `GET_LO` / `LO2.5` | `course_info.txt`: `detailed_learning_outcomes`, dòng `LO2.5` | **Chuẩn hóa** `L.O.2.5` → token/ID `lo2.5`; CFG chỉ có terminal `"lo2.5"` |
| Q010 | L.O.4.2 liên quan đến nội dung nào? | `Q_LO` mở rộng hoặc nhánh riêng `Q_LO_CONTENT` | `GET_LO` / `LO4.2` | `course_info.txt`: `LO4.2` = ngữ cảnh diễn ngôn cục bộ và sự tham chiếu; `topics.txt`: `CH12` là chương tương ứng nếu muốn trả vị trí | **Mở rộng** mẫu “liên quan đến nội dung nào” và chuẩn hóa `L.O.4.2` |
| Q011 | BTL yêu cầu xây dựng những gì? | `Q_ASSIGNMENT_OVERVIEW` | `GET_ASSIGNMENT` / `BTL01` | `assignments.txt`: `goal`, yêu cầu `PART I`, `PART II` (các phần sau theo trạng thái ghi trong file) | **Mở rộng** mẫu “yêu cầu xây dựng những gì” |
| Q012 | Phần I của BTL là gì? | `Q_ASSIGNMENT_PART` | `GET_ASSIGNMENT` / `PART_I` | `assignments.txt`: `PART I - Grammar and Parser`, `requirements`, `suggested_outputs` | **Khớp**; `PART_I` phải gắn với `BTL01`, khác `main_parts` của môn |
| Q013 | BTL có phần hỏi đáp không? | `Q_ASSIGNMENT_FEATURE` | `GET_ASSIGNMENT` / `PART_II` | `assignments.txt`: `PART II - Semantic Interpretation and QA`, yêu cầu `answer generation` | **Khớp**; từ đặc trưng “hỏi đáp” phải ánh xạ đến `PART_II` |
| Q014 | Có được dùng LLM/RAG không? | `Q_RULE` mở rộng với dạng xin phép; hoặc `Q_RULE_PERMISSION` | `GET_RULE` / `LLM_RAG` | `regulations.txt`: `LLM_RAG`; `assignments.txt`: `LLM/RAG EXTENSION`, `status: optional` | **Mở rộng** mẫu “Có được dùng … không?”; `RULE_TOPIC` đã có `"llm/rag"` |
| Q015 | Quy định về sử dụng AI là gì? | `Q_RULE` | `GET_RULE` / `AI_USAGE` | `regulations.txt`: `AI_usage` | **Mở rộng** `RULE_TOPIC` với “sử dụng AI” (`"ai"` đơn lẻ đã có) |
| Q016 | Midterm bao nhiêu phút? | `Q_COURSE_EXAM_DURATION` | `GET_COURSE_INFO` / `MIDTERM` | `course_info.txt`: `exam_format.midterm = 60 minutes` | **Khớp** |
| Q017 | Final bao nhiêu phút? | `Q_COURSE_EXAM_DURATION` | `GET_COURSE_INFO` / `FINAL` | `course_info.txt`: `exam_format.final = 90 minutes` | **Khớp** |
| Q018 | Tài liệu tham khảo về statistical NLP? | `Q_RESOURCE` | `GET_RESOURCE` / `STATISTICAL_NLP` | `resources.txt`: `REFERENCE 1`, `usage: statistical NLP`; `TEXTBOOK 2` cũng ghi statistical methods, nên cần quy tắc chọn/trả nhiều nguồn | **Mở rộng** mẫu “tài liệu tham khảo về … là gì?” |
| Q019 | Tài liệu nào liên quan đến Python NLP? | `Q_RESOURCE` | `GET_RESOURCE` / `PYTHON_NLP` | `resources.txt`: `REFERENCE 2`, tên *Natural Language Processing with Python*, `usage: practical NLP with Python` | **Mở rộng** “liên quan đến” thay vì “nói về” |
| Q020 | Chương 12 nói về gì? | `Q_TOPIC_BY_CHAPTER` | `GET_TOPIC` / `CH12` | `topics.txt`: `CH12`, `summary`, `subtopics` | **Khớp** |
| Q021 | Chương nào học về reference? | `Q_TOPIC_BY_NAME` | `GET_TOPIC` / `REFERENCE` | `topics.txt`: `CH12`, `keywords`/`summary`/mục `12.4–12.5` về reference | **Mở rộng** “học về”; thêm `reference` vào `TOPIC_ENTITY` |
| Q022 | Chương nào học về question answering? | `Q_TOPIC_BY_NAME` | `GET_TOPIC` / `QUESTION_ANSWERING` | `topics.txt`: `CH11`, mục `11.5 Procedural semantics and question answering`; `CH08` mục 8.5 nói về simple questions nhưng không phải nhãn QA chính | **Mở rộng** “học về”; `question answering` đã có trong `TOPIC_ENTITY` |
| Q023 | Chương nào học về selectional restriction? | `Q_TOPIC_BY_NAME` | `GET_TOPIC` / `SELECTIONAL_RESTRICTION` | `topics.txt`: `CH09`, mục `9.1–9.2` | **Mở rộng** “học về”; thêm `selectional restriction` vào `TOPIC_ENTITY` |
| Q024 | Chương 10 có những phương pháp gì? | `Q_TOPIC_BY_CHAPTER` mở rộng hoặc `Q_TOPIC_METHODS` | `GET_TOPIC` / `CH10` | `topics.txt`: `CH10`, `summary` và `subtopics` 10.1–10.4 (grammatical relations, semantic grammars, template matching, semantically driven parsing) | **Mở rộng** mẫu “có những phương pháp gì?” |
| Q025 | Chương 11 có liên quan đến hỏi đáp không? | `Q_TOPIC_RELATION` | `GET_TOPIC` / `CH11` | `topics.txt`: `CH11`, `summary` và mục 11.5 xác nhận question answering | **Mở rộng** `TOPIC_ENTITY` với “hỏi đáp”; khung `RELATION_PHRASE` đã khớp |

**Ghi chú về dữ kiện:** `schedule.txt` là kế hoạch 15 tuần *mẫu*. Với Q005 phải đọc tất cả record trùng chương. Với Q007, trả các chương và tuần tìm được; với Q018, trả các tài liệu khớp thay vì chỉ lấy kết quả đầu tiên. Với Q010, chỉ coi mô tả LO4.2 trong `course_info.txt` là fact trực tiếp; liên hệ LO4.2 đến CH12 là suy luận bổ sung, không mặc nhiên đưa vào đáp án.

## Ca ngoài miền và ca thiếu fact

Q026–Q028 **đã có trong** `sample_queries.txt`; các ca này không thuộc 25 câu lõi cần parse. Khi parser không nhận dạng, semantic/query nên cho `UNKNOWN` / `OUT_OF_SCOPE` theo hợp đồng hệ thống. Không diễn giải việc CFG seed không nhận dạng là minh chứng parser đã chạy đúng.

| ID | Câu hỏi | Intent / entity trong bộ mẫu | Kỳ vọng |
| --- | --- | --- | --- |
| Q026 | Hôm nay ở TP.HCM có mưa không? | `UNKNOWN` / `OUT_OF_SCOPE` | Ngoài miền thời tiết; không truy vấn KB môn học |
| Q027 | Ai là tổng thống của Pháp? | `UNKNOWN` / `OUT_OF_SCOPE` | Ngoài miền chính trị; không truy vấn KB môn học |
| Q028 | Hãy giải bài tập xác suất này giúp tôi. | `UNKNOWN` / `OUT_OF_SCOPE` | Yêu cầu giải bài tập, không phải tra dữ kiện KB môn học |
| TỰ BỔ SUNG C001 | Deadline của bài tập lớn là khi nào? | `GET_DEADLINE` / `BTL01` (nhãn do nhóm đề xuất) | **CFG seed khớp** nhánh `Q_DEADLINE`; `assignments.txt` và `regulations.txt` không có *ngày giờ deadline cụ thể*, nên query phải trả `NOT_FOUND` và answer nói chưa có thông tin ngày nộp. Không lấy mốc checkpoint/“final submission” trong `schedule.txt` làm ngày deadline |

`Q029–Q034` thuộc ví dụ hội thoại có tham chiếu ngữ cảnh trong file mẫu; đánh giá riêng nếu nhóm làm Phần III. Bảng này tập trung vào Q001–Q025 và các ca ngoài miền/thiếu dữ kiện của Mốc 0.
