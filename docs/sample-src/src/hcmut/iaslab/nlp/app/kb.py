"""Load the supplied semi-structured text files into queryable indexes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu knowledge-base file: {path}")
    return path.read_text(encoding="utf-8")


def _section(text: str, start: str, ends: tuple[str, ...]) -> str:
    start_match = re.search(rf"(?m)^{re.escape(start)}\s*$", text)
    if not start_match:
        return ""
    tail = text[start_match.end() :]
    positions = [match.start() for end in ends if (match := re.search(rf"(?m)^{re.escape(end)}\s*$", tail))]
    return tail[: min(positions)] if positions else tail


def _simple_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*):\s*(.+)$", text):
        fields[match.group(1)] = match.group(2).strip()
    return fields


def _parse_field_block(text: str, list_fields: set[str] | None = None) -> dict[str, Any]:
    list_fields = list_fields or set()
    result: dict[str, Any] = {}
    current: str | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or set(stripped) == {"-"}:
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$", stripped)
        if match:
            current = match.group(1)
            value = match.group(2).strip()
            result[current] = [value] if current in list_fields and value else ([] if current in list_fields else value)
            continue
        if current is None:
            continue
        value = stripped[2:].strip() if stripped.startswith("- ") else stripped
        if current in list_fields:
            result.setdefault(current, []).append(value)
        elif result.get(current):
            result[current] = f"{result[current]} {value}".strip()
        else:
            result[current] = value
    return result


@dataclass(frozen=True)
class KnowledgeBase:
    course: dict[str, Any]
    weeks: dict[str, dict[str, Any]]
    chapter_weeks: dict[str, list[str]]
    topics: dict[str, dict[str, Any]]
    assignment: dict[str, Any]
    resources: list[dict[str, Any]]
    regulations: dict[str, str]
    source_dir: Path

    @classmethod
    def load(cls, source_dir: str | Path) -> "KnowledgeBase":
        root = Path(source_dir)
        course = _load_course(_read(root / "course_info.txt"))
        weeks, chapter_weeks = _load_schedule(_read(root / "schedule.txt"))
        topics = _load_topics(_read(root / "topics.txt"))
        assignment = _load_assignment(_read(root / "assignments.txt"))
        resources = _load_resources(_read(root / "resources.txt"))
        regulations = _load_regulations(_read(root / "regulations.txt"))
        return cls(course, weeks, chapter_weeks, topics, assignment, resources, regulations, root)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.course.get("course_id") != "CO3085":
            errors.append("course_info.txt không có course_id=CO3085")
        if len(self.weeks) != 15:
            errors.append(f"schedule.txt: cần 15 tuần, đọc được {len(self.weeks)}")
        if len(self.topics) != 12:
            errors.append(f"topics.txt: cần 12 chương, đọc được {len(self.topics)}")
        if len(self.resources) != 8:
            errors.append(f"resources.txt: cần 8 tài liệu, đọc được {len(self.resources)}")
        required_rules = {"AI_usage", "LLM_RAG", "source_code", "external_libraries"}
        if not required_rules.issubset(self.regulations):
            errors.append("regulations.txt thiếu một hoặc nhiều quy định bắt buộc")
        return errors


def _load_course(text: str) -> dict[str, Any]:
    course: dict[str, Any] = _simple_fields(text)
    description = _section(text, "course_description:", ("Mục tiêu:",))
    course["course_description"] = " ".join(line.strip() for line in description.splitlines() if line.strip())

    parts = _section(text, "main_parts:", ("learning_outcomes:",))
    course["main_parts"] = [line.strip() for line in parts.splitlines() if line.strip()]

    lo_block = _section(text, "learning_outcomes:", ("detailed_learning_outcomes:",))
    detailed_block = _section(text, "detailed_learning_outcomes:", ("assessment:",))
    course["learning_outcomes"] = _parse_los(lo_block + "\n" + detailed_block)

    assessment = _section(text, "assessment:", ("exam_format:",))
    course["assessment"] = _simple_fields(assessment)
    exam = _section(text, "exam_format:", ())
    course["exam_format"] = _simple_fields(exam)
    return course


def _parse_los(text: str) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    current: str | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        match = re.match(r"^(LO\d+(?:\.\d+)?)\s*-\s*(.*)$", stripped)
        if match:
            current = match.group(1)
            outcomes[current] = match.group(2).strip()
        elif current and stripped:
            outcomes[current] = f"{outcomes[current]} {stripped}".strip()
    return outcomes


def _load_schedule(text: str) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    matches = list(re.finditer(r"(?m)^WEEK\s+(\d{2})\s*$", text))
    weeks: dict[str, dict[str, Any]] = {}
    chapter_weeks: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        week_id = f"WEEK_{int(match.group(1)):02d}"
        record = _parse_field_block(text[match.end() : end], {"topics"})
        record["week_id"] = week_id
        chapter_text = str(record.get("chapter", ""))
        chapter_match = re.search(r"\d+", chapter_text)
        if chapter_match:
            chapter_id = f"CH{int(chapter_match.group()):02d}"
            record["chapter_id"] = chapter_id
            chapter_weeks.setdefault(chapter_id, []).append(week_id)
        weeks[week_id] = record
    return weeks, chapter_weeks


def _load_topics(text: str) -> dict[str, dict[str, Any]]:
    matches = list(re.finditer(r"(?m)^CHAPTER\s+(\d+):\s*(.+)$", text))
    topics: dict[str, dict[str, Any]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        record = _parse_field_block(text[match.end() : end], {"subtopics"})
        chapter_id = str(record.get("chapter_id") or f"CH{int(match.group(1)):02d}")
        record["chapter_id"] = chapter_id
        record["chapter_number"] = int(match.group(1))
        record["title"] = match.group(2).strip()
        keywords = record.get("keywords", "")
        record["keyword_list"] = [item.strip() for item in str(keywords).split(",") if item.strip()]
        topics[chapter_id] = record
    return topics


def _load_assignment(text: str) -> dict[str, Any]:
    assignment: dict[str, Any] = _simple_fields(text)
    goal_match = re.search(r"(?ms)^goal:\s*\n(.*?)(?=^PART I\s+-)", text)
    assignment["goal"] = " ".join(goal_match.group(1).split()) if goal_match else ""
    sections: dict[str, dict[str, Any]] = {}
    matches = list(re.finditer(r"(?m)^PART\s+(I|II|III|IV)\s+-\s*(.+)$", text))
    for index, match in enumerate(matches):
        end_candidates = [matches[index + 1].start()] if index + 1 < len(matches) else []
        extension = re.search(r"(?m)^LLM/RAG EXTENSION\s*$", text[match.end() :])
        if extension:
            end_candidates.append(match.end() + extension.start())
        end = min(end_candidates) if end_candidates else len(text)
        section_id = f"PART_{match.group(1)}"
        record = _parse_field_block(
            text[match.end() : end],
            {"requirements", "minimum_requirements", "suggested_outputs", "suggested_intents", "optional_or_extension"},
        )
        record["section_id"] = section_id
        record["title"] = match.group(2).strip()
        sections[section_id] = record
    assignment["sections"] = sections
    return assignment


def _load_resources(text: str) -> list[dict[str, Any]]:
    matches = list(re.finditer(r"(?m)^(TEXTBOOK|REFERENCE)\s+(\d+)\s*$", text))
    resources: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        if "study_note:" in block:
            block = block.split("study_note:", 1)[0]
        record = _parse_field_block(block)
        record["resource_id"] = f"{match.group(1)}_{match.group(2)}"
        record["kind"] = match.group(1)
        resources.append(record)
    return resources


def _load_regulations(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*):\s*$", text))
    rules: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = " ".join(line.strip() for line in text[match.end() : end].splitlines() if line.strip())
        rules[match.group(1)] = value
    return rules
