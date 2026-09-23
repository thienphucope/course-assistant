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
    resource_note: str = ""
    regulations: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, kb_dir: str | Path) -> "KnowledgeBase":
        """Load all six text collections into stable in-memory records."""
        directory = Path(kb_dir)
        weeks = _load_weeks(directory / "schedule.txt")
        topics = _load_topics(directory / "topics.txt")
        course = _load_course(directory / "course_info.txt")
        assignment = _load_assignment(directory / "assignments.txt")
        resources, resource_note = _load_resources(directory / "resources.txt")
        regulations = _load_regulations(directory / "regulations.txt")
        chapter_weeks: dict[str, list[str]] = {}
        for week_id, record in weeks.items():
            chapter_id = record.get("chapter_id")
            if chapter_id is not None:
                chapter_weeks.setdefault(chapter_id, []).append(week_id)
        kb = cls(course=course, weeks=weeks, chapter_weeks=chapter_weeks,
                 topics=topics, assignment=assignment, resources=tuple(resources),
                 resource_note=resource_note, regulations=regulations)
        errors = kb.validate()
        if errors:
            raise ValueError("Invalid course knowledge base:\n- " + "\n- ".join(errors))
        return kb

    def validate(self) -> list[str]:
        """Report invalid IDs, missing required facts, and broken references."""
        errors: list[str] = []
        if self.course:
            if self.course.get("course_id") != "CO3085":
                errors.append("course_info.txt: expected course_id CO3085")
            if not isinstance(self.course.get("credits"), int):
                errors.append("course_info.txt: missing integer credits")
            for key in ("course_description", "main_parts", "learning_outcomes",
                        "detailed_learning_outcomes", "assessment", "exam_format"):
                if not self.course.get(key):
                    errors.append(f"course_info.txt: missing {key}")
        if self.assignment:
            if self.assignment.get("assignment_id") != "BTL01":
                errors.append("assignments.txt: expected assignment_id BTL01")
            if not self.assignment.get("goal"):
                errors.append("assignments.txt: missing goal")
            for part_id in ("PART_I", "PART_II", "PART_III", "PART_IV"):
                if part_id not in self.assignment.get("parts", {}):
                    errors.append(f"assignments.txt: missing {part_id}")
        for record in self.resources:
            if not record.get("resource_id") or not record.get("title"):
                errors.append("resources.txt: resource missing id/title")
        if self.regulations and not self.regulations.get("AI_USAGE"):
            errors.append("regulations.txt: missing AI_USAGE")
        for chapter_id, record in self.topics.items():
            if not re.fullmatch(r"CH\d{2}", chapter_id):
                errors.append(f"topics.txt: invalid chapter ID {chapter_id}")
            if record.get("chapter_id") != chapter_id:
                errors.append(f"topics.txt: {chapter_id} record key mismatch")
            if "source_id_seen" in record and not record["source_id_seen"]:
                errors.append(f"topics.txt: {chapter_id} missing explicit chapter_id")
            for key in ("title", "summary", "subtopics"):
                if not record.get(key):
                    errors.append(f"topics.txt: {chapter_id} missing {key}")
        for week_id, record in self.weeks.items():
            if not re.fullmatch(r"WEEK_\d{2}", week_id):
                errors.append(f"Invalid week ID: {week_id}")
            if record.get("week_id") != week_id:
                errors.append(f"{week_id}: record week_id does not match its key")
            if not record.get("part"):
                errors.append(f"{week_id}: missing part")
            if not record.get("topics"):
                errors.append(f"{week_id}: missing topics")
            chapter_id = record.get("chapter_id")
            if chapter_id is not None:
                if not re.fullmatch(r"CH\d{2}", str(chapter_id)):
                    errors.append(f"{week_id}: invalid chapter ID {chapter_id}")
                if self.topics and chapter_id not in self.topics:
                    errors.append(f"{week_id}: {chapter_id} absent from topics.txt")
                if week_id not in self.chapter_weeks.get(chapter_id, []):
                    errors.append(f"{week_id}: missing reverse index for {chapter_id}")
        for chapter_id, week_ids in self.chapter_weeks.items():
            for week_id in week_ids:
                if week_id not in self.weeks:
                    errors.append(f"{chapter_id}: reverse index refers to absent {week_id}")
                elif self.weeks[week_id].get("chapter_id") != chapter_id:
                    errors.append(f"{chapter_id}: reverse index disagrees with {week_id}")
        return errors


def _load_weeks(path: Path) -> dict[str, dict[str, Any]]:
    """Parse one ``WEEK NN`` block at a time; ignore the file preamble."""
    weeks: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    in_topics = False
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        heading = re.fullmatch(r"WEEK\s+(\d{1,2})", line, re.IGNORECASE)
        if heading:
            week_id = f"WEEK_{int(heading.group(1)):02d}"
            if week_id in weeks:
                raise ValueError(f"{path.name}:{line_number}: duplicate {week_id}")
            current = {
                "week_id": week_id,
                "part": None,
                "chapter_id": None,
                "topics": [],
            }
            weeks[week_id] = current
            in_topics = False
            continue
        if current is None:
            continue
        if line.lower() == "topics:":
            in_topics = True
            continue
        if line.startswith("-"):
            if not in_topics:
                raise ValueError(f"{path.name}:{line_number}: topic outside topics list")
            topic = line[1:].strip()
            if not topic:
                raise ValueError(f"{path.name}:{line_number}: empty topic")
            current["topics"].append(topic)
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path.name}:{line_number}: expected 'key: value'")
        key, value = key.strip().lower(), value.strip()
        in_topics = False
        if key == "chapter":
            chapter = re.fullmatch(r"Chapter\s+(\d{1,2})", value, re.IGNORECASE)
            if not chapter:
                raise ValueError(f"{path.name}:{line_number}: invalid chapter {value!r}")
            current["chapter_id"] = f"CH{int(chapter.group(1)):02d}"
        elif key in {"part", "activity", "milestone"}:
            current[key] = value
        else:
            raise ValueError(f"{path.name}:{line_number}: unsupported field {key!r}")
    if not weeks:
        raise ValueError(f"{path.name}: no WEEK records found")
    return weeks


def _load_topics(path: Path) -> dict[str, dict[str, Any]]:
    """Keep chapter titles, keywords, summaries, and numbered subtopics."""
    chapters: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    section: str | None = None
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        heading = re.fullmatch(r"CHAPTER\s+(\d+):\s*(.+)", line, re.IGNORECASE)
        if heading:
            chapter_id = f"CH{int(heading.group(1)):02d}"
            if chapter_id in chapters:
                raise ValueError(f"{path.name}:{line_number}: duplicate {chapter_id}")
            current = {"chapter_id": chapter_id, "source_id_seen": False,
                       "title": heading.group(2),
                       "part": "", "keywords": [], "summary": "", "subtopics": []}
            chapters[chapter_id] = current
            section = None
            continue
        if current is None:
            continue
        if line.startswith("chapter_id:"):
            actual = line.partition(":")[2].strip().upper()
            if actual != current["chapter_id"]:
                raise ValueError(f"{path.name}:{line_number}: heading and chapter_id disagree")
            if current["source_id_seen"]:
                raise ValueError(f"{path.name}:{line_number}: duplicate chapter_id")
            current["source_id_seen"] = True
            section = None
        elif line.startswith("part:"):
            current["part"] = line.partition(":")[2].strip()
            section = None
        elif line.startswith("keywords:"):
            current["keywords"] = [item.strip() for item in line.partition(":")[2].split(",") if item.strip()]
            section = None
        elif line == "summary:":
            section = "summary"
        elif line == "subtopics:":
            section = "subtopics"
        elif section == "summary":
            current["summary"] = (current["summary"] + " " + line).strip()
        elif section == "subtopics":
            current["subtopics"].append(line)
        else:
            raise ValueError(f"{path.name}:{line_number}: unexpected chapter line {line!r}")
    if not chapters:
        raise ValueError(f"{path.name}: no CHAPTER records found")
    return chapters


def _load_course(path: Path) -> dict[str, Any]:
    """Read scalar course facts and named multiline/list sections."""
    course: dict[str, Any] = {}
    section: str | None = None
    list_sections = {"main_parts", "learning_outcomes", "detailed_learning_outcomes"}
    map_sections = {"assessment", "exam_format"}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.endswith(":") and line[:-1] in {"course_description", *list_sections, *map_sections}:
            section = line[:-1]
            course[section] = {} if section in map_sections or section.endswith("outcomes") else (
                [] if section in list_sections else ""
            )
            continue
        if section is None:
            match = re.fullmatch(r"([a-z][a-z_]*):\s*(.+)", line)
            if match:
                key, value = match.groups()
                if key in course:
                    raise ValueError(f"{path.name}:{line_number}: duplicate {key}")
                course[key] = value
            continue
        if section == "course_description":
            course[section] = (course[section] + " " + line).strip()
        elif section == "main_parts":
            course[section].append(line)
        elif section in {"learning_outcomes", "detailed_learning_outcomes"}:
            match = re.fullmatch(r"(LO\d+(?:\.\d+)?)\s*-\s*(.+)", line)
            if match:
                lo_id, description = match.groups()
                if lo_id in course[section]:
                    raise ValueError(f"{path.name}:{line_number}: duplicate {lo_id}")
                course[section][lo_id] = description
            elif course[section]:
                last = next(reversed(course[section]))
                course[section][last] += " " + line
            else:
                raise ValueError(f"{path.name}:{line_number}: LO continuation without ID")
        elif section in map_sections:
            key, separator, value = line.partition(":")
            if not separator or not key.strip() or not value.strip():
                raise ValueError(f"{path.name}:{line_number}: expected section key: value")
            if key.strip() in course[section]:
                raise ValueError(f"{path.name}:{line_number}: duplicate {key.strip()}")
            course[section][key.strip()] = value.strip()
    if not course.get("course_id"):
        raise ValueError(f"{path.name}: missing course_id")
    try:
        course["credits"] = int(course["credits"])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{path.name}: credits must be an integer") from exc
    return course


def _load_assignment(path: Path) -> dict[str, Any]:
    """Read assignment metadata and all four PART blocks."""
    assignment: dict[str, Any] = {"parts": {}, "extension": {}}
    current: dict[str, Any] = assignment
    active_key: str | None = None
    list_keys = {"requirements", "suggested_outputs", "minimum_requirements",
                 "suggested_intents", "optional_or_extension", "not_required"}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        heading = re.fullmatch(r"PART\s+(I|II|III|IV)\s*-\s*(.+)", line, re.IGNORECASE)
        if heading:
            part_id = f"PART_{heading.group(1).upper()}"
            if part_id in assignment["parts"]:
                raise ValueError(f"{path.name}:{line_number}: duplicate {part_id}")
            current = {"part_id": part_id, "title": heading.group(2)}
            assignment["parts"][part_id] = current
            active_key = None
            continue
        if line == "LLM/RAG EXTENSION":
            current = assignment["extension"]
            active_key = None
            continue
        if re.fullmatch(r"[-=]+", line):
            continue
        match = re.fullmatch(r"([a-z][a-z_]*):\s*(.*)", line)
        if match:
            key, value = match.groups()
            if key in current:
                raise ValueError(f"{path.name}:{line_number}: duplicate {key}")
            current[key] = ([value] if value else []) if key in list_keys else value
            active_key = key
            continue
        if active_key is not None:
            value = current[active_key]
            if isinstance(value, list):
                value.append(line.removeprefix("- "))
            elif isinstance(value, str):
                current[active_key] = (value + " " + line).strip()
            else:
                raise ValueError(f"{path.name}:{line_number}: invalid {active_key}")
    if not assignment.get("assignment_id"):
        raise ValueError(f"{path.name}: missing assignment_id")
    return assignment


def _load_resources(path: Path) -> tuple[list[dict[str, Any]], str]:
    """Read every textbook/reference record and the closing study note."""
    resources: list[dict[str, Any]] = []
    ids: set[str] = set()
    current: dict[str, Any] | None = None
    note = ""
    in_note = False
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        heading = re.fullmatch(r"(TEXTBOOK|REFERENCE)\s+(\d+)", line, re.IGNORECASE)
        if heading:
            resource_id = f"{heading.group(1).upper()}_{int(heading.group(2))}"
            if resource_id in ids:
                raise ValueError(f"{path.name}:{line_number}: duplicate {resource_id}")
            ids.add(resource_id)
            current = {"resource_id": resource_id}
            resources.append(current)
            in_note = False
            continue
        if line == "study_note:":
            current = None
            in_note = True
            continue
        if in_note:
            note = (note + " " + line).strip()
        elif current is not None:
            match = re.fullmatch(r"([a-z][a-z_]*):\s*(.+)", line)
            if not match:
                raise ValueError(f"{path.name}:{line_number}: expected resource key: value")
            key, value = match.groups()
            if key in current:
                raise ValueError(f"{path.name}:{line_number}: duplicate {key}")
            current[key] = value
    if not resources:
        raise ValueError(f"{path.name}: no resource records found")
    return resources, note


def _load_regulations(path: Path) -> dict[str, str]:
    """Read named multiline rules under their canonical uppercase IDs."""
    rules: dict[str, str] = {}
    current: str | None = None
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z_]*):\s*(.*)", line)
        if match:
            key, value = match.groups()
            current = key.upper()
            if current in rules:
                raise ValueError(f"{path.name}:{line_number}: duplicate {current}")
            rules[current] = value
        elif current is not None:
            rules[current] = (rules[current] + " " + line).strip()
    if not rules:
        raise ValueError(f"{path.name}: no regulations found")
    return rules
