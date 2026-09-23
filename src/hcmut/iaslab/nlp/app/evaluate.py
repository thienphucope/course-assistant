"""Regression evaluation for syntax, semantics, retrieval, answers, and dialogue.

Evaluation cases should declare expected intent/entity/status and optional
answer evidence.  Evaluate the observable ``PipelineResult`` rather than private
implementation details, and report per-stage failures so a grammar miss is not
misdiagnosed as a KB bug.  Maintain separate official, challenge, and dialogue
suites; future precision/recall or latency metrics can extend the summary
without changing application code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .pipeline import CourseAssistant, PipelineResult


@dataclass(frozen=True)
class EvaluationCase:
    """Expected behavior for one independent question."""

    question: str
    expected_intent: str
    expected_entity: str | None = None
    expected_query_status: str | None = None
    answer_contains: tuple[str, ...] = ()
    case_id: str = ""


@dataclass(frozen=True)
class EvaluationRecord:
    """One case paired with its result and stage-specific checks."""

    case: EvaluationCase
    result: PipelineResult
    parse_ok: bool
    intent_ok: bool
    entity_ok: bool
    query_ok: bool | None
    answer_ok: bool | None

    @property
    def passed(self) -> bool:
        return all(check is not False for check in
                   (self.parse_ok, self.intent_ok, self.entity_ok,
                    self.query_ok, self.answer_ok))


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregate records with derived pass counts, suitable for reports/CI."""

    records: tuple[EvaluationRecord, ...]
    name: str = "Evaluation"

    @property
    def passed(self) -> int:
        return sum(record.passed for record in self.records)

    @property
    def total(self) -> int:
        return len(self.records)

    def stage_score(self, stage: str) -> tuple[int, int]:
        """Return correct/labeled counts; unlabeled checks are not scored."""
        checks = [getattr(record, stage) for record in self.records]
        return sum(check is True for check in checks), sum(check is not None for check in checks)


@dataclass(frozen=True)
class DialogueCase:
    """Ordered turns whose shared state must be evaluated as one conversation."""

    name: str
    turns: tuple[EvaluationCase, ...]


def load_evaluation_cases(path: str | Path) -> list[EvaluationCase]:
    """Parse and validate the project evaluation-fixture format."""
    source = Path(path)
    cases: list[EvaluationCase] = []
    seen: set[str] = set()
    valid_statuses = {"FOUND", "NOT_FOUND", "OUT_OF_SCOPE",
                      "UNSUPPORTED_INTENT", "MISSING_CONTEXT"}
    for line_number, raw in enumerate(source.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if parts[0].upper() == "ID":
            continue
        if len(parts) not in {4, 5, 6}:
            raise ValueError(f"{source.name}:{line_number}: expected 4 to 6 columns")
        case_id, question, intent, entity = parts[:4]
        if not re.fullmatch(r"[A-Za-z]\d{3}", case_id):
            raise ValueError(f"{source.name}:{line_number}: invalid case ID {case_id!r}")
        if case_id in seen:
            raise ValueError(f"{source.name}:{line_number}: duplicate {case_id}")
        if not question or not intent or not entity:
            raise ValueError(f"{source.name}:{line_number}: missing required field")
        seen.add(case_id)
        status = parts[4].upper() if len(parts) >= 5 and parts[4] else None
        if status == "SKIPPED":
            status = "OUT_OF_SCOPE"
        if status is None and intent == "UNKNOWN":
            status = "OUT_OF_SCOPE"
        if status is not None and status not in valid_statuses:
            raise ValueError(f"{source.name}:{line_number}: invalid status {status}")
        terms = tuple(term.strip() for term in parts[5].split(";;") if term.strip()) if len(parts) == 6 else ()
        cases.append(EvaluationCase(
            question=question,
            expected_intent=intent,
            expected_entity=None if entity in {"OUT_OF_SCOPE", "-"} else entity,
            expected_query_status=status,
            answer_contains=terms,
            case_id=case_id,
        ))
    if not cases:
        raise ValueError(f"{source}: no evaluation cases found")
    return cases


def evaluate_cases(assistant: CourseAssistant, cases: list[EvaluationCase],
                   name: str = "Evaluation") -> EvaluationSummary:
    """Run stateless cases and score each observable pipeline stage."""
    records: list[EvaluationRecord] = []
    for case in cases:
        result = assistant.process(case.question, use_context=False)
        parse_ok = result.parse.accepted == (case.expected_intent != "UNKNOWN")
        intent_ok = result.detected_intent == case.expected_intent
        entity_ok = result.detected_entity == case.expected_entity
        query_ok: bool | None = None
        if case.expected_query_status is not None:
            query_ok = result.query.status == case.expected_query_status
            if query_ok and case.expected_query_status == "FOUND":
                query_ok = bool(result.query.sources)
        answer_ok: bool | None = None
        if case.answer_contains:
            answer = result.answer.casefold()
            answer_ok = all(term.casefold() in answer for term in case.answer_contains)
            if answer_ok and case.expected_query_status == "FOUND":
                answer_ok = not answer.startswith("xin lỗi")
        records.append(EvaluationRecord(case, result, parse_ok, intent_ok,
                                        entity_ok, query_ok, answer_ok))
    return EvaluationSummary(tuple(records), name)


def load_dialogue_cases(path: str | Path) -> list[DialogueCase]:
    """Load ordered multi-turn fixtures while preserving conversation boundaries."""
    raise NotImplementedError("Implement dialogue fixture loading")


def evaluate_dialogues(assistant: CourseAssistant, cases: list[DialogueCase]) -> EvaluationSummary:
    """Reset between dialogues, preserve state within each, and score all turns."""
    raise NotImplementedError("Implement context-aware dialogue evaluation")


def render_evaluation(summary: EvaluationSummary) -> str:
    """Return a human-readable, stage-by-stage regression report."""
    lines = [f"## {summary.name}",
             f"Cases: {summary.total}",
             f"Cases passing all declared labels: {summary.passed}/{summary.total} "
             f"({_percent(summary.passed, summary.total)})",
             "Stage results (correct/labeled):"]
    for label, stage in (("Parse", "parse_ok"), ("Intent", "intent_ok"),
                         ("Entity", "entity_ok"), ("Query", "query_ok"),
                         ("Answer evidence", "answer_ok")):
        correct, labeled = summary.stage_score(stage)
        lines.append(f"- {label}: {correct}/{labeled} ({_percent(correct, labeled)})")
    failures = [record for record in summary.records if not record.passed]
    lines.append("Failures:")
    if not failures:
        lines.append("- None on the declared labels.")
    for record in failures:
        case, result = record.case, record.result
        lines.extend([
            f"- {case.case_id or '?'}: {case.question}",
            f"  Expected: {case.expected_intent} / {case.expected_entity or '-'} / "
            f"{case.expected_query_status or 'unlabeled'}",
            f"  Actual: {result.detected_intent} / {result.detected_entity or '-'} / "
            f"{result.query.status}",
            f"  First failed stage: {_first_failed_stage(record)}.",
            f"  Answer: {result.answer}",
        ])
    return "\n".join(lines)


def render_evaluation_report(summaries: list[EvaluationSummary]) -> str:
    """Combine separated suites with the scoring rule and practical limits."""
    total = sum(summary.total for summary in summaries)
    passed = sum(summary.passed for summary in summaries)
    sections = [
        "COURSE ASSISTANT EVALUATION — CLASSICAL NLP",
        "",
        "Method: each case is processed independently (dialogue context disabled).",
        "Parse expects a complete tree for in-domain questions and () for UNKNOWN.",
        "Intent/entity compare canonical labels; query compares declared status and",
        "requires at least one source when FOUND; answer checks declared text fragments.",
        "Missing query/answer labels are excluded from those stage denominators.",
        "Answer fragments are evidence checks, not a full human judgment of wording.",
        "",
        f"Combined declared-label pass: {passed}/{total} ({_percent(passed, total)}).",
    ]
    sections.extend("\n" + render_evaluation(summary) for summary in summaries)
    sections.extend([
        "",
        "Strengths: traceable KB sources; separate OUT_OF_SCOPE and NOT_FOUND;",
        "all seven required groups have grounded core examples.",
        "Limits: rule-based grammar misses unlisted wording and missing diacritics;",
        "the KB is sample course data, not an official administrative schedule.",
        "Dialogue Q029–Q034 is optional and excluded from independent-question scores.",
        "The sample-core suite helped development; do not present its accuracy as",
        "accuracy on unseen real-world questions.",
    ])
    return "\n".join(sections) + "\n"


def _percent(correct: int, total: int) -> str:
    return f"{100 * correct / total:.1f}%" if total else "not labeled"


def _first_failed_stage(record: EvaluationRecord) -> str:
    if not record.parse_ok:
        return "tokenizer/grammar/parser (no expected full parse)"
    if not record.intent_ok or not record.entity_ok:
        return "semantic mapping/entity alias"
    if record.query_ok is False:
        return "KB lookup/query status"
    return "answer evidence/template"
