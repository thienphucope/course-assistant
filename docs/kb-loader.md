# KB Loader — biến file .txt "như văn xuôi" thành tủ tra được

> Cross-cutting như 03. Cách đọc `data/kb/*.txt` thành cấu trúc query lúc chạy.
> Plumbing 🔧, không phải việc não — nhưng bỏ qua thì cả run-time đứng hình.

## Cảm giác "vô cấu trúc" là bẫy
Mở file thấy giống văn xuôi tiếng người → tưởng không parse nổi. Sai. Có người
ngồi đặt cấu trúc **bằng tay**: dấu `:`, dòng header đều đặn. Nó là
**semi-structured** — *lỏng nhưng đều*, không raw prose, cũng không JSON.

## 3 khuôn lặp — loader chỉ cần bám đúng 3 cái này
| Khuôn | Trông như | Thấy ở |
|---|---|---|
| `key: value` | `credits: 3`, `chapter: Chapter 3` | course_info (đầu file), mọi block |
| **RECORD block**: 1 dòng header rồi field con | `WEEK 03` / `CHAPTER 3:` → dòng dưới | schedule, topics |
| **list item** | `- context-free grammar`, `3.1.1 …`, `LO2.5 - …` | topics list, subtopics, LO |

Loader = `split` theo header → trong block `partition(":")` lấy field → dòng `- `
gom thành list. Hết.

## Nguyên tắc: mỗi file 1 loader, index theo ENTITY
Header mỗi file khác nhau (`WEEK` vs `CHAPTER:` vs phẳng) → **không có loader vạn
năng** → **6 loader nhỏ** (~15–25 dòng/file). Output mỗi loader = dict **keyed
theo entity bạn sẽ tra** (khớp "ô trống = entity", doc 03).

| File | Header block | Khóa index | Phục vụ intent |
|---|---|---|---|
| `schedule` | `WEEK NN` | week (+ đảo: chapter→week) | GET_SCHEDULE |
| `topics` | `CHAPTER N:` | chapter_id + keyword search | GET_TOPIC ("CFG" trong keywords → CH03) |
| `course_info` | `key:` phẳng | tên field | GET_COURSE_INFO (credits, midterm 60') |
| `course_info` §LO | `LOx.y - text` | LO id | GET_LO |
| `assignments` | block phần BTL | part id | GET_ASSIGNMENT |
| `resources` | mục tài liệu | chủ đề/keyword | GET_RESOURCE |
| `regulations` | mục quy định | chủ đề luật | GET_RULE |

## Bằng chứng: 20 dòng parse `schedule.txt`
```python
import re, io
weeks, cur, key = {}, None, None
for raw in io.open("data/kb/schedule.txt", encoding="utf-8"):
    line = raw.rstrip("\n")
    m = re.match(r"WEEK (\d+)", line)
    if m:
        cur = {}; weeks[int(m.group(1))] = cur; key = None
    elif cur is not None:
        if line.startswith("- "):              # list item
            cur.setdefault(key, []).append(line[2:].strip())
        elif ":" in line:                       # key: value (hoặc header list)
            k, _, v = line.partition(":"); key = k.strip(); v = v.strip()
            if v: cur[key] = v
```
Chạy thật ra:
```
weeks parsed        : 15
GET_SCHEDULE week=3 : chapter=Chapter 3 | topics=context-free grammar, ...
Chapter 4 -> weeks  : [4, 5]      ← đảo chiều "chương học tuần nào" cũng ra
milestones          : {8: 'checkpoint 1', 12: 'checkpoint 2', 15: 'final'}
```
→ "Vô cấu trúc" mà trả lời đúng 3 kiểu câu hỏi, kể cả câu đảo chiều.

## 3 mép xấu phải xử tay (mỗi cái vài dòng)
1. **Value nhiều dòng** — `summary:` trong topics chạy tới dòng trống/`key:` kế →
   gom lại, đừng cắt 1 dòng.
2. **Dòng wrap thụt lề** — `LO4` ở course_info xuống dòng "     hỏi đáp…" → nối lại.
3. **Key không đồng nhất** — `midterm_exam: 30 percent` (assessment) vs
   `midterm: …60 minutes` (exam_format). Hai chỗ, hai kiểu → đừng tra mù 1 key.

## Nối bài tập
Loader là **nền của bước QUERY** (doc 06): design-time bạn viết loader; run-time
máy gọi. `faq.txt`/`dialogues.txt` **KHÔNG** qua khuôn này (cơ chế chuỗi/nhãn) →
nằm `scaffolding/`, không phải core KB.
