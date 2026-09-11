"""Evaluation for labelled queries and local-context dialogues."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .answer import MISSING_CONTEXT, NOT_FOUND, NOT_UNDERSTOOD
from .pipeline import CourseAssistant, PipelineResult
from .tokenizer import normalize_text


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    query: str
    expected_intent: str
    expected_entity: str
    expected_query_status: str = "FOUND"
    expected_answer_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationRecord:
    case: EvaluationCase
    result: PipelineResult
    actual_intent: str
    actual_entity: str
    actual_query_status: str
    intent_correct: bool
    entity_correct: bool
    query_correct: bool
    answer_correct: bool

    @property
    def correct(self) -> bool:
        return self.intent_correct and self.entity_correct and self.query_correct and self.answer_correct

    @property
    def diagnosis(self) -> str:
        if self.correct:
            return "OK"
        if not self.result.parse.accepted and self.case.expected_intent != "UNKNOWN":
            return "Grammar thiếu mẫu hoặc từ đồng nghĩa; parser trả ()."
        if self.case.expected_intent == "UNKNOWN" and self.result.parse.accepted:
            return "Grammar nhận nhầm câu ngoài miền (false acceptance)."
        if not self.intent_correct:
            return "Nhánh semantic grammar ánh xạ sai intent."
        if not self.entity_correct:
            return "Trích xuất/chuẩn hóa entity hoặc phân giải ngữ cảnh sai."
        if not self.query_correct:
            return f"Trạng thái query sai: expected={self.case.expected_query_status}, actual={self.actual_query_status}."
        if not self.answer_correct:
            expected = ", ".join(self.case.expected_answer_terms) or "đúng loại câu trả lời/fallback"
            return f"Câu trả lời không chứa kết quả mong đợi: {expected}."
        return "OK"


@dataclass(frozen=True)
class EvaluationSummary:
    records: tuple[EvaluationRecord, ...]

    @property
    def total(self) -> int:
        return len(self.records)

    @property
    def intent_correct(self) -> int:
        return sum(record.intent_correct for record in self.records)

    @property
    def entity_correct(self) -> int:
        return sum(record.entity_correct for record in self.records)

    @property
    def joint_correct(self) -> int:
        return sum(record.correct for record in self.records)

    @property
    def query_correct(self) -> int:
        return sum(record.query_correct for record in self.records)

    @property
    def answer_correct(self) -> int:
        return sum(record.answer_correct for record in self.records)

    def percentage(self, value: int) -> float:
        return 100.0 * value / self.total if self.total else 0.0


def load_evaluation_cases(path: str | Path) -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        parts = [part.strip() for part in raw.split("|")]
        if len(parts) < 4 or not re.fullmatch(r"[A-Z]\d{3}", parts[0]):
            continue
        expected_status = parts[4].upper() if len(parts) >= 5 and parts[4] else _default_query_status(parts[2])
        expected_terms = tuple(
            term.strip() for term in parts[5].split(";;") if term.strip()
        ) if len(parts) >= 6 else ()
        cases.append(EvaluationCase(*parts[:4], expected_status, expected_terms))
    return cases


def evaluate_cases(
    assistant: CourseAssistant, cases: list[EvaluationCase], reset_context: bool = True
) -> EvaluationSummary:
    if reset_context:
        assistant.reset_context()
    records: list[EvaluationRecord] = []
    for case in cases:
        result = assistant.process(case.query, use_context=True)
        actual_intent = result.detected_intent
        actual_entity = result.detected_entity or ("OUT_OF_SCOPE" if actual_intent == "UNKNOWN" else "NONE")
        actual_query_status = _query_status(result)
        records.append(
            EvaluationRecord(
                case=case,
                result=result,
                actual_intent=actual_intent,
                actual_entity=actual_entity,
                actual_query_status=actual_query_status,
                intent_correct=actual_intent == case.expected_intent,
                entity_correct=actual_entity == case.expected_entity,
                query_correct=actual_query_status == case.expected_query_status,
                answer_correct=_answer_matches(case, result, actual_query_status),
            )
        )
    return EvaluationSummary(tuple(records))


def _default_query_status(expected_intent: str) -> str:
    if expected_intent == "UNKNOWN":
        return "SKIPPED"
    if expected_intent == "GET_INSTRUCTOR":
        return "NOT_FOUND"
    return "FOUND"


def _query_status(result: PipelineResult) -> str:
    if result.query.found:
        return "FOUND"
    if result.query.kind in {"UNKNOWN", "UNRESOLVED_CONTEXT"}:
        return "SKIPPED"
    return "NOT_FOUND"


def _answer_matches(case: EvaluationCase, result: PipelineResult, actual_status: str) -> bool:
    if actual_status != case.expected_query_status:
        return False
    answer = normalize_text(result.answer)
    if case.expected_answer_terms:
        return all(normalize_text(term) in answer for term in case.expected_answer_terms)
    if actual_status == "FOUND":
        return bool(answer) and result.answer not in {NOT_FOUND, NOT_UNDERSTOOD, MISSING_CONTEXT}
    if actual_status == "NOT_FOUND":
        return result.answer == NOT_FOUND
    return result.answer in {NOT_UNDERSTOOD, MISSING_CONTEXT}


def render_evaluation(official: EvaluationSummary, challenge: EvaluationSummary) -> str:
    lines = [
        "COURSE ASSISTANT - EVALUATION REPORT",
        "====================================",
        "",
        "Phương pháp: chấm end-to-end intent, entity, trạng thái query và fact bắt buộc trong câu trả lời.",
        "Câu CONTEXT_DEPENDENT được chấm intent trước phân giải và entity sau phân giải.",
        "Câu UNKNOWN đúng khi parser từ chối và hệ thống không truy vấn KB.",
        "",
    ]
    lines.extend(_render_summary("A. BỘ KIỂM THỬ DO ĐỀ CUNG CẤP", official))
    lines.append("")
    lines.extend(_render_summary("B. BỘ THỬ THÁCH BỔ SUNG", challenge))
    lines.extend(
        [
            "",
            "C. PHÂN TÍCH LỖI",
            "-----------------",
        ]
    )
    errors = [record for summary in (official, challenge) for record in summary.records if not record.correct]
    if errors:
        for record in errors:
            lines.append(
                f"{record.case.case_id}: {record.case.query} | expected="
                f"{record.case.expected_intent}/{record.case.expected_entity} | actual="
                f"{record.actual_intent}/{record.actual_entity} | {record.diagnosis}"
            )
    else:
        lines.append("Không có ca sai trong hai bộ kiểm thử hiện tại.")
    lines.extend(
        [
            "",
            "D. ƯU ĐIỂM VÀ HẠN CHẾ",
            "----------------------",
            "Ưu điểm: kết quả quyết định được, giải thích được bằng cây cú pháp, chạy offline,",
            "không hallucination và phân biệt rõ lỗi cú pháp với thiếu dữ liệu KB.",
            "Hạn chế: grammar đóng không hiểu mọi cách diễn đạt; thêm từ đồng nghĩa hoặc mẫu",
            "câu mới cần cập nhật grammar. Ngữ cảnh chỉ giữ thực thể gần nhất và các quan hệ",
            "định trước, chưa xử lý tham chiếu xa hay nhập nhằng hội thoại phức tạp.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_summary(title: str, summary: EvaluationSummary) -> list[str]:
    lines = [
        title,
        "-" * len(title),
        f"Số câu: {summary.total}",
        f"Intent đúng: {summary.intent_correct}/{summary.total} ({summary.percentage(summary.intent_correct):.2f}%)",
        f"Entity đúng: {summary.entity_correct}/{summary.total} ({summary.percentage(summary.entity_correct):.2f}%)",
        f"Query/status đúng: {summary.query_correct}/{summary.total} ({summary.percentage(summary.query_correct):.2f}%)",
        f"Answer/fact đúng: {summary.answer_correct}/{summary.total} ({summary.percentage(summary.answer_correct):.2f}%)",
        f"Đúng end-to-end: {summary.joint_correct}/{summary.total} ({summary.percentage(summary.joint_correct):.2f}%)",
        "",
        "ID | Kết quả | Expected | Actual | Parse | Query expected/actual | Answer",
    ]
    for record in summary.records:
        status = "PASS" if record.correct else "FAIL"
        parse_status = "tree" if record.result.parse.accepted else "()"
        answer_status = "ok" if record.answer_correct else "sai"
        lines.append(
            f"{record.case.case_id} | {status} | {record.case.expected_intent}/{record.case.expected_entity} | "
            f"{record.actual_intent}/{record.actual_entity} | {parse_status} | "
            f"{record.case.expected_query_status}/{record.actual_query_status} | {answer_status}"
        )
    return lines


@dataclass(frozen=True)
class DialogueCase:
    dialogue_id: str
    questions: tuple[str, ...]
    expected_reference: str


def load_dialogue_cases(path: str | Path) -> list[DialogueCase]:
    text = Path(path).read_text(encoding="utf-8")
    headers = list(re.finditer(r"(?m)^DIALOGUE\s+(\d+)\s*$", text))
    cases: list[DialogueCase] = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        block = text[header.end() : end]
        questions = tuple(match.group(1).strip() for match in re.finditer(r"(?m)^U\d+:\s*(.+)$", block))
        reference = re.search(r'(?m)^EXPECTED_REFERENCE:.*->\s*([^\s"]+)', block)
        if questions and reference:
            cases.append(DialogueCase(f"D{int(header.group(1)):02d}", questions, reference.group(1)))
    return cases


def render_dialogue_evaluation(assistant: CourseAssistant, cases: list[DialogueCase]) -> str:
    lines = [
        "LOCAL DISCOURSE CONTEXT RESULTS",
        "================================",
        "",
    ]
    passed = 0
    for case in cases:
        assistant.reset_context()
        results = [assistant.process(question, use_context=True) for question in case.questions]
        final = results[-1]
        expected = "PART_I" if case.expected_reference == "PART_I_GRAMMAR_PARSER" else case.expected_reference
        actual = final.detected_entity or "NONE"
        correct = actual == expected and final.query.found
        passed += int(correct)
        lines.append(f"{case.dialogue_id} | {'PASS' if correct else 'FAIL'} | expected={case.expected_reference} | resolved={actual}")
        for turn, result in enumerate(results, start=1):
            lines.append(f"U{turn}: {result.sentence}")
            lines.append(f"PARSE{turn}: {result.parse.output()}")
            lines.append(f"SEMANTIC{turn}: {result.semantic.predicate}")
            if result.context_used:
                lines.append(f"CONTEXT{turn}: {result.context_used}")
            lines.append(f"A{turn}: {result.answer}")
        lines.append("")
    accuracy = 100.0 * passed / len(cases) if cases else 0.0
    lines.append(f"Tổng: {passed}/{len(cases)} hội thoại đúng ({accuracy:.2f}%).")
    return "\n".join(lines) + "\n"
