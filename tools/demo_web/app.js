"use strict";

const byId = (id) => document.getElementById(id);
const form = byId("question-form");
const question = byId("question");
const examples = byId("examples");
const turns = byId("turns");
const overview = byId("overview");
const previous = byId("previous");
const next = byId("next");

const stages = [
  ["Câu hỏi & token", showTokens],
  ["Cây cú pháp", showParse],
  ["Ngữ nghĩa", showSemantic],
  ["Intent & thực thể", showIntent],
  ["Ngữ cảnh", showContext],
  ["Truy vấn KB", showQuery],
  ["Câu trả lời", showAnswer],
];

let session = null;
let turn = null;
let stageIndex = 0;
let showAll = false;
let busy = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const stepButtons = stages.map(([label], index) => {
  const item = element("li");
  const button = element("button", "step");
  const number = element("span", "step-index", index + 1);
  number.setAttribute("aria-hidden", "true");
  button.type = "button";
  button.append(number, element("span", "", label));
  button.addEventListener("click", () => selectStage(index));
  item.append(button);
  byId("steps").append(item);
  return button;
});

function code(text, extra = "") {
  return element("pre", `code ${extra}`.trim(), text);
}

function labeled(label, content) {
  const group = element("div");
  group.append(element("p", "data-label", label), content);
  return group;
}

function details(label, content) {
  const group = element("details");
  group.append(element("summary", "", label), content);
  return group;
}

function fields(entries) {
  const list = element("dl", "field-list");
  for (const [label, value] of entries) {
    const field = element("dd");
    const text = typeof value === "string" ? value : JSON.stringify(value);
    field.append(element("code", "", value == null ? "—" : text));
    list.append(element("dt", "", label), field);
  }
  return list;
}

function badges(items, className) {
  const list = element("ul", className);
  for (const item of items) list.append(element("li", "", item));
  return list;
}

function treeItem(node) {
  const row = element("li");
  if (typeof node === "string") {
    row.append(element("span", "leaf", node));
    return row;
  }
  const branch = node.label.startsWith("Q_") ? " branch" : "";
  row.append(element("span", `node${branch}`, node.label));
  if (node.children.length === 0) {
    row.append(element("span", "leaf", "ε"));
  } else if (node.children.every((child) => typeof child === "string")) {
    for (const child of node.children) row.append(element("span", "leaf", child));
  } else {
    const children = element("ul");
    for (const child of node.children) children.append(treeItem(child));
    row.append(children);
  }
  return row;
}

function showTokens(result, body) {
  const tokens = result.tokens.length ? badges(result.tokens, "token-list") : element("p", "message", "Không có token.");
  body.append(labeled(`Token sau chuẩn hóa (${result.tokens.length})`, tokens));
}

function showParse(result, body) {
  const {accepted, tree, bracketed} = result.parse;
  if (!accepted) {
    body.append(code(bracketed), element("p", "message", "Parser không dựng được cây cú pháp cho câu này."));
    return ["Không khớp văn phạm", "warn"];
  }
  const frame = element("div", "tree-frame");
  frame.tabIndex = 0;
  frame.setAttribute("aria-label", "Cây cú pháp từ bộ phân tích Earley");
  const treeList = element("ul", "tree");
  treeList.append(treeItem(tree));
  frame.append(treeList);
  body.append(frame, details("Dạng ngoặc của cây", code(bracketed)));
  return ["Khớp văn phạm", "good"];
}

function showSemantic(result, body) {
  const {predicate, source_branch} = result.semantic;
  body.append(labeled("Vị từ", code(predicate)), fields([["Nhánh văn phạm", source_branch]]));
}

function showIntent(result, body) {
  const {intent, entity, slots} = result.semantic;
  body.append(fields([["Intent", intent], ["Thực thể trước phân giải", entity]]));
  const entries = Object.entries(slots);
  const values = entries.length ? fields(entries) : element("p", "message", "Không có tham số.");
  body.append(labeled("Tham số (slots)", values));
}

function showContext(result, body) {
  const {used, before, after, resolved} = result.context;
  const unresolved = result.query.kind === "UNRESOLVED_CONTEXT";
  if (used) {
    body.append(element("p", "message", used), labeled("Vị từ sau phân giải", code(resolved.predicate)));
  } else {
    const message = unresolved ? "Chưa đủ ngữ cảnh để phân giải tham chiếu." : "Lượt hỏi này không cần phân giải tham chiếu.";
    body.append(element("p", "message", message));
  }

  const memory = element("div", "memory");
  for (const [label, snapshot] of [["Trước lượt hỏi", before], ["Sau lượt hỏi", after]]) {
    memory.append(labeled(label, fields([
      ["Thực thể gần nhất", snapshot.last_entity],
      ["Chương", snapshot.last_chapter],
      ["Phần BTL", snapshot.last_assignment_part],
      ["Chuẩn đầu ra", snapshot.last_lo],
      ["Lịch sử thực thể", snapshot.history.join(" → ") || null],
    ])));
  }
  body.append(memory);
  if (used) return ["Đã phân giải", "good"];
  if (unresolved) return ["Thiếu ngữ cảnh", "warn"];
}

function showQuery(result, body) {
  const {query, status, kind, sources, data, reason} = result.query;
  body.append(code(query), fields([["Loại truy vấn", kind]]));
  if (reason) body.append(element("p", "message", reason));
  if (sources.length) body.append(labeled("Nguồn trong KB", badges(sources, "source-list")));
  if (data !== null) body.append(labeled("Dữ liệu truy xuất", code(JSON.stringify(data, null, 2), "json")));
  return [status, status === "FOUND" ? "good" : "warn"];
}

function showAnswer(result, body) {
  const className = result.query.found ? "answer" : "answer warn";
  body.append(element("p", className, result.answer));
  return [result.query.found ? "Có câu trả lời" : "Thông báo cho người dùng", result.query.found ? "good" : "warn"];
}

function stagePanel(index) {
  const [label, render] = stages[index];
  const panel = element("section", "stage");
  const heading = element("header", "stage-heading");
  const body = element("div", "stage-body");
  heading.append(element("h3", "", label));
  const status = render(turn, body);
  if (status) heading.append(element("span", `badge ${status[1]}`, status[0]));
  panel.append(heading, body);
  return panel;
}

function render() {
  byId("empty").hidden = Boolean(turn);
  byId("result").hidden = !turn;
  byId("history").hidden = turns.options.length < 2;
  for (const [index, button] of stepButtons.entries()) {
    button.disabled = !turn;
    if (turn && !showAll && index === stageIndex) button.setAttribute("aria-current", "step");
    else button.removeAttribute("aria-current");
  }
  if (!turn) return;

  byId("active-question").textContent = turn.question;
  overview.setAttribute("aria-pressed", String(showAll));
  overview.textContent = showAll ? "Xem từng bước" : "Xem toàn bộ";
  byId("stage-controls").hidden = showAll;
  byId("step-count").textContent = `Bước ${stageIndex + 1} / ${stages.length}`;
  previous.disabled = stageIndex === 0;
  next.disabled = stageIndex === stages.length - 1;
  const panels = showAll ? stages.map((_, index) => stagePanel(index)) : [stagePanel(stageIndex)];
  byId("stage-view").replaceChildren(...panels);
}

function selectStage(index) {
  if (!turn || index < 0 || index >= stages.length) return;
  stageIndex = index;
  showAll = false;
  render();
}

function notice(text = "") {
  byId("notice").textContent = text;
  byId("notice").hidden = !text;
}

function setBusy(value) {
  busy = value;
  question.readOnly = value;
  examples.disabled = value || examples.options.length < 2;
  byId("submit").disabled = value;
  byId("submit").textContent = value ? "Đang phân tích…" : "Phân tích";
  byId("reset").disabled = value || session === null;
  byId("trace").setAttribute("aria-busy", String(value));
}

const history = [];

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const sentence = question.value.trim();
  if (!sentence) {
    notice("Hãy nhập một câu hỏi.");
    question.focus();
    return;
  }

  notice();
  setBusy(true);
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: sentence, session}),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    session = result.session;
    turn = result;
    const index = history.push(result);
    turns.add(new Option(`${index}. ${result.question}`, index - 1, true, true));
    byId("session-label").textContent = `${index} lượt hỏi`;
    question.value = "";
    examples.value = "";
    selectStage(0);
    stepButtons[0].focus({preventScroll: true});
  } catch (error) {
    notice(error instanceof TypeError ? "Không kết nối được máy chủ demo." : error.message);
  } finally {
    setBusy(false);
  }
});

byId("reset").addEventListener("click", () => {
  session = null;
  turn = null;
  history.length = 0;
  turns.replaceChildren();
  byId("session-label").textContent = "Chưa có lượt hỏi";
  question.value = "";
  examples.value = "";
  notice();
  setBusy(false);
  render();
  question.focus();
});

turns.addEventListener("change", () => {
  turn = history[Number(turns.value)];
  selectStage(0);
});

examples.addEventListener("change", () => {
  if (!examples.value) return;
  question.value = examples.value;
  question.focus();
});

overview.addEventListener("click", () => {
  showAll = !showAll;
  render();
});

previous.addEventListener("click", () => selectStage(stageIndex - 1));
next.addEventListener("click", () => selectStage(stageIndex + 1));

document.addEventListener("keydown", (event) => {
  if (!turn || showAll || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest("input, select, textarea, [contenteditable], .tree-frame, pre")) return;
  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
  event.preventDefault();
  selectStage(stageIndex + (event.key === "ArrowRight" ? 1 : -1));
  if (event.target.matches(".step")) stepButtons[stageIndex].focus({preventScroll: true});
});

async function loadExamples() {
  try {
    const response = await fetch("/api/examples");
    if (!response.ok) throw new Error();
    for (const {label, question: sample} of await response.json()) {
      examples.add(new Option(label, sample));
    }
    examples.disabled = busy;
  } catch {
    examples.options[0].textContent = "Không tải được câu mẫu";
  }
}

render();
loadExamples();
