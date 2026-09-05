# Background — Vì sao pipeline NLP cổ điển lại có hình dạng này

> Tài liệu nền. Chưa vào bước kỹ thuật nào — chỉ kể **câu chuyện** vì sao loài
> người nghĩ ra cái pipeline Grammar → Parser → Semantic → KB → Answer, chứ
> không phải cách khác. Khi thấy được **nỗi đau** mà mỗi giai đoạn sinh ra để
> giải quyết, mọi thứ hết rối: "à, phải thế thôi".

---

## 1. Giấc mơ gốc: nói chuyện với cái máy

**1950, Alan Turing** viết một bài báo hỏi: "Máy có nghĩ được không?" Ông đề
xuất một trò chơi — nếu bạn nhắn tin qua lại mà không phân biệt được đầu bên kia
là người hay máy, thì coi như máy "hiểu". Từ đó cả ngành đặt mục tiêu: **làm máy
giao tiếp bằng ngôn ngữ người.**

Nhưng bắt tay vào mới thấy một bức tường: **ngôn ngữ không giống toán.** Toán có
luật rõ. Còn câu chữ thì mù mờ, một câu mười nghĩa, và **vô hạn** — bạn có thể
nói câu chưa ai từng nói bao giờ mà người nghe vẫn hiểu. Làm sao dạy máy một thứ
vô hạn?

---

## 2. Cú hích lớn nhất: Chomsky và ý tưởng "luật sinh ra câu"

**1957, Noam Chomsky**, một nhà ngôn ngữ học, thả một quả bom trí tuệ. Ông nói:

> Bạn **không** học ngôn ngữ bằng cách thuộc lòng từng câu. Bạn học một **bộ luật
> hữu hạn**, và bộ luật đó **sinh ra vô hạn câu**.

Đây là khoảnh khắc bản lề của cả ngành. Hãy cảm cho kỹ:
- Số câu tiếng Việt đúng ngữ pháp là **vô hạn**.
- Nhưng não bạn thì **hữu hạn**.
- Vậy trong đầu bạn không phải là "danh sách câu", mà là một **cỗ máy luật** để
  ráp câu.

Chomsky gọi đó là **generative grammar** — văn phạm sinh. Và ông xếp các loại
luật thành thang bậc (Chomsky hierarchy); một nấc trong đó tên là **Context-Free
Grammar (CFG)** — chính là chữ CFG trong bài này.

👉 Đây là lý do **tồn tại "Grammar"**: nó là nỗ lực viết ra cái cỗ máy luật hữu
hạn mô tả "câu nào là hợp lệ".

---

## 3. Hệ quả kỹ thuật: muốn HIỂU thì phải làm ngược lại

Nếu luật **sinh ra** câu (đi xuôi), thì để **hiểu** một câu, máy phải **truy
ngược**: "câu này được ráp từ những luật nào?"

Quá trình truy ngược đó chính là **Parsing**. Kết quả — cái "sơ đồ đã ráp thế
nào" — là **cây cú pháp**.

Ẩn dụ: grammar là **công thức nấu ăn**, câu là **món ăn dọn ra bàn**. Parser là
đầu bếp nếm món rồi **dựng lại công thức**. Nếu không có công thức nào ra được món
này → món "sai luật" → máy từ chối.

👉 Đây là lý do tồn tại **"Parser"**: nó là cái máy truy-ngược-từ-câu-về-luật.

---

## 4. Bài học đắt giá: ráp đúng ≠ hiểu

Đây là chỗ nhiều người trẻ vấp. Chomsky tự đưa ví dụ kinh điển:

> *"Colorless green ideas sleep furiously"* (Những ý tưởng xanh không màu ngủ một
> cách giận dữ).

Câu này **đúng ngữ pháp 100%** nhưng **vô nghĩa**. Ngược lại "Tôi ăn cơm rồi" thì
cả đúng lẫn có nghĩa.

Nhận ra điều này, người ta hiểu: **cú pháp (structure) và ngữ nghĩa (meaning) là
hai tầng khác nhau.** Biết câu ráp thế nào **chưa** cho biết nó **muốn gì**. Phải
có thêm một trạm dịch từ "cấu trúc" sang "ý định".

👉 Đây là lý do tồn tại **"Semantic / Intent"**: cầu nối từ *hình dạng câu* sang
*điều câu muốn*.

---

## 5. Và ý nghĩa cũng vô dụng nếu không nối với thế giới

Giả sử máy hiểu câu muốn "hỏi lịch tuần 3". Rồi sao? Nó phải **có chỗ để tra** mới
trả lời được. Cái kho tri thức đó = **Knowledge Base**. Không có KB thì hiểu để
làm gì — như hiểu câu hỏi "sách ở kệ nào" nhưng cả đời chưa bước vào thư viện.

👉 Đây là lý do tồn tại **"KB → Query → Answer"**: nối ý nghĩa với dữ liệu thật để
đẻ ra câu trả lời.

**Cột mốc sống động nhất:** **1970, Terry Winograd** làm **SHRDLU** — một chương
trình sống trong "thế giới khối hộp" ảo. Bạn gõ "Đặt khối đỏ lên khối xanh", nó
**parse câu → hiểu ý → tra trạng thái thế giới → làm / trả lời**. Nó thậm chí hiểu
"nó" là khối nào từ câu trước (ngữ cảnh!).

**Bài tập lớn này về bản chất là một SHRDLU thu nhỏ** — thay "thế giới khối hộp"
bằng "thông tin 1 môn học". Cái pipeline Grammar → Parser → Semantic → KB → Answer
ta đang phải làm chính là kiến trúc SHRDLU 1970. Ta đang đi lại con đường của
Winograd.

---

## 6. Vì sao bài bắt làm kiểu "cổ" này, khi đã có ChatGPT?

Đây là phần lịch sử giúp hết ấm ức. Cả ngành đã dao động như con lắc giữa **hai
trường phái**:

| | Trường phái LUẬT (rationalist) | Trường phái DỮ LIỆU (empiricist) |
|---|---|---|
| Niềm tin | Hiểu ngôn ngữ = viết ra hệ luật | Không cần hiểu luật, **đếm** đủ dữ liệu là ra |
| Thời hoàng kim | 1950s–1980s (Chomsky, SHRDLU) | 1990s–nay (thống kê → deep learning → LLM) |
| Đại diện | CFG, parser, luật viết tay | Naive Bayes → word2vec (2013) → Transformer (2017) → GPT/ChatGPT (2022) |

Con lắc đã đu như sau:
- **1954**: máy dịch (Georgetown–IBM) hứa hão, thổi phồng.
- **1966**: **ELIZA** — con bot giả vờ làm bác sĩ tâm lý bằng **ghép mẫu chữ**,
  không hiểu gì, mà người ta vẫn tưởng thật. Bài học: **giả vờ hiểu ≠ hiểu**.
- **1966**: báo cáo ALPAC phủ nhận máy dịch → **mùa đông AI**, mất tiền tài trợ.
- **~1990**: dân làm nhận dạng tiếng nói chán viết luật tay, quay sang **xác suất
  + dữ liệu**. Có câu (giai thoại) gắn với Fred Jelinek ở IBM:

  > *"Mỗi lần tôi đuổi một nhà ngôn ngữ học, độ chính xác lại tăng."*

  → **trường phái dữ liệu (phe lười) thắng thế.** Không thèm hiểu luật ngữ pháp
  nữa, cứ đổ data vào — thế mà lại hay.
- **2017 → nay**: Transformer → LLM. Máy giờ **nuốt cả internet** rồi đoán chữ
  tiếp theo. Nó *có vẻ* hiểu mọi thứ.

**Vậy tại sao vẫn học đường cũ?** Vì LLM là một **hộp đen**: nó trả lời hay nhưng
ta **không thấy** nó hiểu bằng cách nào, và nó **bịa** (hallucinate) tỉnh bơ. Còn
con đường Grammar → Parser → Semantic là **hộp kính**: mỗi bước nhìn thấu được,
sai ở đâu chỉ ra được, và **không bao giờ bịa** (không có luật → nói "không
biết").

Bài này bắt ta **tự tay dựng cỗ máy hiểu**, để *thật sự thấy* ngôn ngữ được máy
mổ xẻ ra sao — thứ mà nếu chỉ gọi API ChatGPT thì sẽ chẳng bao giờ nhìn thấy.
RAG/LLM chỉ là cái đuôi "cho biết thời hiện đại", không phải phần cốt lõi.

---

## 7. Bản đồ: chỗ nào một-đường, chỗ nào nhiều-hướng / tốn công

Ở mức background thôi, để biết sau này đổ sức vào đâu:

- **Grammar (viết CFG)** — 🔥 **tốn công nhất, nhiều lựa chọn thiết kế nhất.** Phủ
  bao nhiêu loại câu, gom cụm từ ra sao, xử lý cách nói khác nhau của cùng 1 ý —
  đây là nơi ăn thời gian và cũng là nơi ăn điểm.
- **Parser** — ⚙️ **gần như một đường.** Thuật toán parse là kiến thức chuẩn
  (đệ quy / bảng), ít phải "sáng tạo". Viết đúng một lần, dùng mãi.
- **Semantic → Intent/Entity** — 🔀 **nhiều hướng thứ nhì.** Đây là chỗ rẽ
  **classical (luật/keyword) vs statistical (xác suất/ML)**. Chọn hướng nào là
  quyết định lớn.
- **KB + Query + Answer** — 🔧 **chủ yếu là plumbing** (đường ống). Đọc file, tra
  cứu, đổ template. Ít trí tuệ, nhiều cẩn thận.
- **Ngữ cảnh hội thoại (Phần III)** & **RAG (Phần II lựa chọn 2)** — ✨ **optional,
  điểm cộng.** Đầu tư khi đã chắc phần lõi.

**Trục xương sống, một câu:** Chomsky bảo "luật sinh ra câu" → nên muốn hiểu thì
truy ngược ra cây (parse) → cây chưa phải nghĩa nên dịch sang ý định (semantic) →
ý định nối vào kho biết (KB) → đẻ câu trả lời. Năm trạm đó không phải ai bịa ra
cho vui — mỗi trạm là một bức tường ai đó từng đâm đầu vào suốt 70 năm.
