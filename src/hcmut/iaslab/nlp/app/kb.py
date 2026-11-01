"""Load, normalize, index, and validate the supplied course knowledge base.

This module is the only place that understands the physical ``data/kb`` text
formats.  Convert them once into canonical in-memory records keyed by IDs such
as ``CH03`` and ``WEEK_03``; query code should not repeatedly parse raw text.
Validation must report broken cross-references, duplicate IDs, and missing
required fields early.  A later JSON/database adapter can implement the same
contract without changing semantics, dialogue, or answer generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class KnowledgeBase:
    """Normalized aggregate of every supported course-data collection."""

    course: dict[str, Any] = field(default_factory=dict)
    weeks: dict[str, dict[str, Any]] = field(default_factory=dict)
    chapter_weeks: dict[str, list[str]] = field(default_factory=dict)
    topics: dict[str, dict[str, Any]] = field(default_factory=dict)
    assignment: dict[str, Any] = field(default_factory=dict)
    resources: tuple[dict[str, Any], ...] = ()
    regulations: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, kb_dir: str | Path) -> "KnowledgeBase":
        """Read all required KB files and build canonical indexes."""
        directory = Path(kb_dir)
        weeks = _load_weeks(directory / "schedule.txt")
        kb = cls(
            course=_load_course(directory / "course_info.txt"),
            weeks=weeks,
            chapter_weeks=_build_chapter_weeks(weeks),
            topics=_load_topics(directory / "topics.txt"),
            assignment=_load_assignment(directory / "assignments.txt"),
            resources=tuple(_load_resources(directory / "resources.txt")),
            regulations=_load_regulations(directory / "regulations.txt"),
        )
        errors = kb.validate()
        if errors:
            raise ValueError("Invalid knowledge base:\n- " + "\n- ".join(errors))
        return kb

    def validate(self) -> list[str]:
        """Return all structural/cross-reference errors; an empty list is valid."""
        errors: list[str] = []
        if self.course.get("course_id") != "CO3085":
            errors.append("course_info.txt: expected course_id CO3085")
        for key, expected_type in {
            "credits": str, "course_description": str, "main_parts": list,
            "learning_outcomes": dict, "assessment": dict, "exam_format": dict,
        }.items():
            if not isinstance(self.course.get(key), expected_type) or not self.course.get(key):
                errors.append(f"course_info.txt: missing or invalid {key}")
        for name, collection, count in (
            ("weeks", self.weeks, 15), ("topics", self.topics, 12),
            ("resources", self.resources, 8),
        ):
            if len(collection) != count:
                errors.append(f"{name}: expected {count} records, got {len(collection)}")
        for chapter_id, record in self.topics.items():
            if not re.fullmatch(r"CH\d{2}", chapter_id) or record.get("chapter_id") != chapter_id:
                errors.append(f"{chapter_id}: invalid chapter ID or record key mismatch")
            if type(record.get("chapter_number")) is not int:
                errors.append(f"{chapter_id}: chapter_number must be int")
            elif chapter_id != f"CH{record['chapter_number']:02d}":
                errors.append(f"{chapter_id}: chapter_number disagrees with ID")
            for key, expected_type in {
                "title": str, "part": str, "summary": str, "keywords": str,
                "keyword_list": list, "subtopics": list,
            }.items():
                if not isinstance(record.get(key), expected_type) or not record.get(key):
                    errors.append(f"{chapter_id}: missing or invalid {key}")
        for week_id, record in self.weeks.items():
            if not re.fullmatch(r"WEEK_\d{2}", week_id) or record.get("week_id") != week_id:
                errors.append(f"{week_id}: invalid week ID or record key mismatch")
            if not isinstance(record.get("part"), str) or not record.get("part"):
                errors.append(f"{week_id}: missing part")
            if not isinstance(record.get("topics"), list) or not record.get("topics"):
                errors.append(f"{week_id}: missing topics list")
            chapter_id = record.get("chapter_id")
            if chapter_id is not None:
                if chapter_id not in self.topics:
                    errors.append(f"{week_id}: chapter {chapter_id} absent from topics")
                if week_id not in self.chapter_weeks.get(chapter_id, []):
                    errors.append(f"{week_id}: missing reverse index for {chapter_id}")
        for chapter_id, week_ids in self.chapter_weeks.items():
            if chapter_id not in self.topics:
                errors.append(f"{chapter_id}: reverse index refers to absent chapter")
            if not isinstance(week_ids, list):
                errors.append(f"{chapter_id}: reverse index must be a list")
                continue
            if len(week_ids) != len(set(week_ids)):
                errors.append(f"{chapter_id}: duplicate weeks in reverse index")
            for week_id in week_ids:
                if week_id not in self.weeks:
                    errors.append(f"{chapter_id}: reverse index refers to absent {week_id}")
                elif self.weeks[week_id].get("chapter_id") != chapter_id:
                    errors.append(f"{chapter_id}: reverse index disagrees with {week_id}")
        if self.assignment.get("assignment_id") != "BTL01":
            errors.append("assignments.txt: expected assignment_id BTL01")
        for key in ("title", "goal"):
            if not self.assignment.get(key):
                errors.append(f"assignments.txt: missing {key}")
        sections = self.assignment.get("sections", {})
        if not isinstance(sections, dict):
            errors.append("assignments.txt: sections must be a dict")
            sections = {}
        for section_id in ("PART_I", "PART_II", "PART_III", "PART_IV"):
            record = sections.get(section_id, {})
            if record.get("section_id") != section_id or not record.get("title"):
                errors.append(f"assignments.txt: missing or invalid {section_id}")
        resource_ids: set[str] = set()
        for record in self.resources:
            resource_id = record.get("resource_id", "")
            if resource_id in resource_ids:
                errors.append(f"resources.txt: duplicate {resource_id}")
            resource_ids.add(resource_id)
            if not re.fullmatch(r"(?:TEXTBOOK|REFERENCE)_\d+", resource_id):
                errors.append(f"resources.txt: invalid resource ID {resource_id!r}")
            if record.get("kind") not in {"TEXTBOOK", "REFERENCE"}:
                errors.append(f"{resource_id}: invalid kind")
            for key in ("title", "usage"):
                if not record.get(key):
                    errors.append(f"{resource_id}: missing {key}")
        for rule in ("attendance", "academic_integrity", "AI_usage", "source_code",
                     "assignment_sharing", "external_libraries", "LLM_RAG", "OUT_OF_SCOPE"):
            if not isinstance(self.regulations.get(rule), str) or not self.regulations.get(rule):
                errors.append(f"regulations.txt: missing or invalid {rule}")
        return errors


def _load_weeks(path: str | Path) -> dict[str, dict[str, Any]]:
    """Read WEEK blocks, preserving source order and optional schedule fields.

    ``current`` identifies the active week; ``in_topics`` tells us whether a
    bullet belongs to its topics list. The preamble before the first WEEK is
    explanatory text, not a schedule record.
    """
    path = Path(path)
    weeks: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    in_topics = False

    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue

        heading = re.fullmatch(r"WEEK\s+(\d{1,2})", line)
        if heading:
            week_id = f"WEEK_{int(heading.group(1)):02d}"
            if week_id in weeks:
                raise ValueError(f"{path.name}:{line_number}: duplicate {week_id}")
            current = {"week_id": week_id, "topics": []}
            weeks[week_id] = current
            in_topics = False
            continue

        if current is None:
            continue

        if line.startswith("- "):
            if not in_topics:
                raise ValueError(f"{path.name}:{line_number}: topic outside topics list")
            topic = line[2:].strip()
            if not topic:
                raise ValueError(f"{path.name}:{line_number}: empty topic")
            current["topics"].append(topic)
            continue

        key, separator, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not separator or key not in {"part", "chapter", "topics", "activity", "milestone"}:
            raise ValueError(f"{path.name}:{line_number}: unexpected schedule line {line!r}")
        if key == "topics":
            if value or in_topics or current["topics"]:
                raise ValueError(f"{path.name}:{line_number}: expected one 'topics:' list")
            in_topics = True
            continue

        in_topics = False
        if key in current:
            raise ValueError(f"{path.name}:{line_number}: duplicate field {key}")
        if not value:
            raise ValueError(f"{path.name}:{line_number}: empty {key}")
        current[key] = value
        if key == "chapter":
            chapter = re.fullmatch(r"Chapter\s+(\d{1,2})", value)
            if chapter is None:
                raise ValueError(f"{path.name}:{line_number}: invalid chapter {value!r}")
            current["chapter_id"] = f"CH{int(chapter.group(1)):02d}"

    if not weeks:
        raise ValueError(f"{path.name}: no WEEK records found")
    return weeks


def _build_chapter_weeks(weeks: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Index chapter IDs to week IDs in source order, skipping chapterless weeks."""
    chapter_weeks: dict[str, list[str]] = {}
    for week_id, record in weeks.items():
        chapter_id = record.get("chapter_id")
        if chapter_id is not None:
            chapter_weeks.setdefault(chapter_id, []).append(week_id)
    return chapter_weeks


def _load_topics(path: str | Path) -> dict[str, dict[str, Any]]:
    """Read chapter records, joining summary lines and preserving subtopic order.

    ``section`` distinguishes free-text summary lines from individual subtopics.
    Field headers are checked first, so they end the previous section even when
    the source does not put a blank line between sections.
    """
    path = Path(path)
    topics: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    section: str | None = None
    seen_fields: set[str] = set()

    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue

        heading = re.fullmatch(r"CHAPTER\s+(\d{1,2}):\s*(.+)", line)
        if heading:
            chapter_number = int(heading.group(1))
            chapter_id = f"CH{chapter_number:02d}"
            if chapter_id in topics:
                raise ValueError(f"{path.name}:{line_number}: duplicate {chapter_id}")
            current = {
                "chapter_id": chapter_id,
                "chapter_number": chapter_number,
                "title": heading.group(2),
                "summary": "",
                "subtopics": [],
            }
            topics[chapter_id] = current
            section = None
            seen_fields = set()
            continue

        if current is None:
            continue

        key, separator, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if separator and key in {"chapter_id", "part", "keywords", "summary", "subtopics"}:
            if key in seen_fields:
                raise ValueError(f"{path.name}:{line_number}: duplicate field {key}")
            seen_fields.add(key)
            section = None
            if key in {"summary", "subtopics"}:
                if value:
                    raise ValueError(f"{path.name}:{line_number}: expected '{key}:' on its own")
                section = key
            elif not value:
                raise ValueError(f"{path.name}:{line_number}: empty {key}")
            elif key == "chapter_id":
                if value != current["chapter_id"]:
                    raise ValueError(f"{path.name}:{line_number}: heading and chapter_id disagree")
            else:
                current[key] = value
                if key == "keywords":
                    current["keyword_list"] = [item.strip() for item in value.split(",") if item.strip()]
            continue

        if section == "summary":
            current["summary"] = (current["summary"] + " " + line).strip()
        elif section == "subtopics":
            current["subtopics"].append(line)
        else:
            raise ValueError(f"{path.name}:{line_number}: unexpected chapter line {line!r}")

    if not topics:
        raise ValueError(f"{path.name}: no CHAPTER records found")
    return topics


# Parsing helpers adapted from the frozen upstream/sample reference.
# Keep its compatibility fields because contracts.md requires exact golden output.

def _section(text: str, start: str, ends: tuple[str, ...]) -> str:
    """Extract a named section up to the earliest following section header."""
    start_match = re.search(rf"(?m)^{re.escape(start)}\s*$", text)
    if not start_match:
        return ""
    tail = text[start_match.end() :]
    positions = [match.start() for end in ends if (match := re.search(rf"(?m)^{re.escape(end)}\s*$", tail))]
    return tail[: min(positions)] if positions else tail


def _simple_fields(text: str) -> dict[str, str]:
    """Preserve the reference flat-field view, including compatibility fields."""
    fields: dict[str, str] = {}
    for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*):\s*(.+)$", text):
        fields[match.group(1)] = match.group(2).strip()
    return fields


def _parse_field_block(text: str, list_fields: set[str] | None = None) -> dict[str, Any]:
    """Parse a block with scalar continuations and explicitly named lists."""
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
            if current in result:
                raise ValueError(f"Duplicate field {current}")
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


def _load_course(path: str | Path) -> dict[str, Any]:
    """Read course fields and merge general/detailed LO descriptions."""
    text = Path(path).read_text(encoding="utf-8-sig")
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
    """Index LO IDs and join wrapped description lines."""
    outcomes: dict[str, str] = {}
    current: str | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        match = re.match(r"^(LO\d+(?:\.\d+)?)\s*-\s*(.*)$", stripped)
        if match:
            current = match.group(1)
            if current in outcomes:
                raise ValueError(f"Duplicate learning outcome {current}")
            outcomes[current] = match.group(2).strip()
        elif current and stripped:
            outcomes[current] = f"{outcomes[current]} {stripped}".strip()
    return outcomes


def _load_assignment(path: str | Path) -> dict[str, Any]:
    """Read assignment metadata and structured PART I-IV sections."""
    text = Path(path).read_text(encoding="utf-8-sig")
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
        if section_id in sections:
            raise ValueError(f"{Path(path).name}: duplicate {section_id}")
        record["section_id"] = section_id
        record["title"] = match.group(2).strip()
        sections[section_id] = record
    assignment["sections"] = sections
    return assignment


def _load_resources(path: str | Path) -> list[dict[str, Any]]:
    """Read textbook/reference blocks, excluding the trailing study note."""
    text = Path(path).read_text(encoding="utf-8-sig")
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


def _load_regulations(path: str | Path) -> dict[str, str]:
    """Join multiline rule text while preserving case-sensitive rule keys."""
    text = Path(path).read_text(encoding="utf-8-sig")
    matches = list(re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*):\s*$", text))
    rules: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = " ".join(line.strip() for line in text[match.end() : end].splitlines() if line.strip())
        if match.group(1) in rules:
            raise ValueError(f"{Path(path).name}: duplicate rule {match.group(1)}")
        rules[match.group(1)] = value
    return rules
