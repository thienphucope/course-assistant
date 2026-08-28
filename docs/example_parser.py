# -*- coding: utf-8 -*-
"""Ví dụ nhỏ minh hoạ thuật toán NLP cổ điển của Course Assistant.

Nguyên lý (KHÔNG dùng LLM, KHÔNG học tham số):
  - heuristic  : luật viết tay + cắt cụm từ cố định khi tokenize
  - đệ quy     : parse_symbol() gọi lại chính nó để dựng cây con
  - brute force: thử lần lượt từng luật, gặp nhánh tắc thì backtrack

Pipeline thu nhỏ: câu -> token -> cây cú pháp -> predicate ngữ nghĩa.
Chạy: python example_parser.py   (in ra trace backtrack + tự kiểm bằng assert)
"""

# Văn phạm phi ngữ cảnh (CFG). Non-terminal = key trong GRAMMAR, còn lại là terminal.
GRAMMAR = {
    # Cố ý để SCHEDULE_Q trước CREDIT_Q -> câu hỏi tín chỉ sẽ phải backtrack 1 lần.
    "S":          [["SCHEDULE_Q"], ["CREDIT_Q"]],
    "CREDIT_Q":   [["môn", "COURSE", "có", "bao_nhiêu", "tín_chỉ"]],
    "SCHEDULE_Q": [["tuần", "NUM", "học", "gì"]],
    "COURSE":     [["nlp"], ["ai"], ["hđh"]],
    "NUM":        [["5"], ["6"], ["7"]],
}
PHRASES = ["bao nhiêu", "tín chỉ"]  # cụm cố định -> gộp thành 1 token (heuristic tiếng Việt)


def tokenize(text):
    t = text.lower().strip().rstrip("?").strip()
    for p in PHRASES:
        t = t.replace(p, p.replace(" ", "_"))
    return t.split()


def parse_symbol(sym, tokens, pos, depth, trace):
    """Khớp `sym` bắt đầu tại `pos`. Trả (cây_con, vị_trí_mới) hoặc None nếu tắc."""
    pad = "  " * depth
    if sym not in GRAMMAR:                                  # terminal
        if pos < len(tokens) and tokens[pos] == sym:
            trace.append(f"{pad}. khop terminal '{sym}' @{pos}")
            return (sym, pos + 1)
        trace.append(f"{pad}x can '{sym}' @{pos}, thay {tokens[pos:pos+1]}")
        return None

    for i, rule in enumerate(GRAMMAR[sym]):                 # brute force: thử từng luật
        trace.append(f"{pad}thu {sym} luat #{i}: {rule}")
        children, p = [], pos
        for s in rule:                                      # đệ quy xuống các thành phần
            r = parse_symbol(s, tokens, p, depth + 1, trace)
            if r is None:                                   # nhánh tắc
                children = None
                break
            children.append(r[0])
            p = r[1]
        if children is not None:
            trace.append(f"{pad}=> {sym} khop bang luat #{i}")
            return ((sym, children), p)
        trace.append(f"{pad}<= backtrack khoi {sym} luat #{i}")
    return None


def parse(text):
    tokens = tokenize(text)
    trace = []
    r = parse_symbol("S", tokens, 0, 0, trace)
    if r is None or r[1] != len(tokens):                    # phải ăn HẾT token mới hợp lệ
        return None, tokens, trace
    return r[0], tokens, trace


def leaf_under(tree, label):
    """DFS tìm token lá đầu tiên nằm dưới non-terminal `label` (để rút entity)."""
    if isinstance(tree, str):
        return None
    lab, kids = tree
    if lab == label:
        n = kids[0]
        while not isinstance(n, str):
            n = n[1][0]
        return n
    for k in kids:
        got = leaf_under(k, label)
        if got:
            return got
    return None


def to_semantic(tree):
    """Cây cú pháp -> biểu diễn ngữ nghĩa (predicate). Heuristic theo nhãn nhánh."""
    label, kids = tree
    if label == "S":
        return to_semantic(kids[0])
    if label == "CREDIT_Q":
        return f"GET_CREDIT(course={leaf_under(tree, 'COURSE').upper()})"
    if label == "SCHEDULE_Q":
        return f"GET_SCHEDULE(week={leaf_under(tree, 'NUM')})"
    return "UNKNOWN()"


def pretty(tree, depth=0):
    if isinstance(tree, str):
        return "  " * depth + tree
    label, kids = tree
    return "\n".join(["  " * depth + label] + [pretty(k, depth + 1) for k in kids])


if __name__ == "__main__":
    q = "Môn NLP có bao nhiêu tín chỉ?"
    tree, toks, trace = parse(q)
    print("Cau    :", q)
    print("Token  :", toks)
    print("\n--- TRACE (de quy + brute force + backtrack) ---")
    print("\n".join(trace))
    print("\n--- CAY CU PHAP ---")
    print(pretty(tree))
    sem = to_semantic(tree)
    print("\nSemantic:", sem, "   (buoc tiep: tra KB credits=3 -> 'Mon NLP co 3 tin chi.')")

    # Tự kiểm: câu hợp lệ ra đúng predicate; câu ngoài văn phạm ra ().
    assert sem == "GET_CREDIT(course=NLP)"
    assert to_semantic(parse("Tuần 5 học gì?")[0]) == "GET_SCHEDULE(week=5)"
    assert parse("Hôm nay trời đẹp")[0] is None      # ngoài văn phạm -> ()
    print("\nSelf-check passed.")
