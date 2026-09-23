"""Natural-language rendering for grounded query results.

Answers are templates over ``SemanticFrame`` and ``QueryResult`` rather than
free-form generation.  Keep failure messages distinct for unparsed questions,
missing context, and facts absent from the KB.  Rendering must not perform new
lookups or invent details; provenance remains available in the query result.
Future multilingual or UI-specific renderers can replace this class while
retaining the same input contract.
"""

from __future__ import annotations

from .query import QueryResult
from .semantic import SemanticFrame


NOT_FOUND = "Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu môn học."
NOT_UNDERSTOOD = "Xin lỗi, câu hỏi nằm ngoài văn phạm hoặc phạm vi Course Assistant."
NOT_YET_SUPPORTED = "Xin lỗi, hệ thống chưa hỗ trợ loại câu hỏi này."
MISSING_CONTEXT = "Xin lỗi, tôi chưa có đủ ngữ cảnh để hiểu tham chiếu này."


class AnswerGenerator:
    """Render stable Vietnamese answers from structured, grounded data."""

    def generate(self, frame: SemanticFrame, result: QueryResult) -> str:
        """Select a result-kind template or a precise fallback response."""
        if result.kind == "OUT_OF_SCOPE" or frame.intent == "UNKNOWN":
            return NOT_UNDERSTOOD
        if result.kind == "MISSING_CONTEXT":
            return MISSING_CONTEXT
        if result.kind == "UNSUPPORTED_INTENT":
            return NOT_YET_SUPPORTED
        if result.kind == "DEADLINE" and not result.found:
            return "Xin lỗi, tôi không tìm thấy ngày nộp cụ thể của bài tập lớn trong dữ liệu môn học."
        if not result.found:
            return NOT_FOUND
        if result.kind == "SCHEDULE_WEEK":
            record = result.data
            week_id = record["week_id"]
            week_number = int(week_id[5:])
            chapter_id = record.get("chapter_id")
            chapter = f"Chương {int(chapter_id[2:])}" if chapter_id else None
            topics = record.get("topics", [])
            if not topics:
                return NOT_FOUND
            prefix = f"Tuần {week_number} học"
            if chapter:
                prefix += f" {chapter}"
            return f"{prefix}, gồm: {', '.join(topics)}."
        if result.kind == "COURSE_FIELD":
            field, value = result.data["field"], result.data["value"]
            if field == "credits":
                return f"Môn {frame.entity} có {value} tín chỉ."
            if field == "parts":
                return f"Môn {frame.entity} gồm: {'; '.join(value)}."
            if field == "description":
                return f"Môn {frame.entity}: {value}"
            if field == "assessment":
                return "Điểm môn học được tính: " + "; ".join(
                    f"{key.replace('_', ' ')}: {percent}" for key, percent in value.items()
                ) + "."
            if field == "instructor":
                return f"Giảng viên môn {frame.entity}: {value}."
        if result.kind == "EXAM_DURATION":
            exam = result.data["exam"]
            details = result.data["format"]
            return f"{exam} có định dạng: {details}."
        if result.kind == "SCHEDULE_CHAPTER":
            weeks = [int(record["week_id"][5:]) for record in result.data]
            return f"Chương {int(frame.entity[2:])} học vào {', '.join(f'tuần {week}' for week in weeks)}."
        if result.kind == "SCHEDULE_TOPICS":
            topics = result.data["topics"]
            weeks = [int(record["week_id"][5:]) for record in result.data["weeks"]]
            return (f"{topics[0]} và {topics[1]} cùng xuất hiện ở "
                    + ", ".join(f"tuần {week}" for week in weeks) + ".")
        if result.kind == "TOPIC_CHAPTERS":
            chapters = result.data["chapters"]
            names = ", ".join(f"Chương {int(record['chapter_id'][2:])} ({record['title']})"
                              for record in chapters)
            return f"Chủ đề {_topic_label(result.data['topic'])} có trong {names}."
        if result.kind == "TOPIC_LOCATION":
            chapters = ", ".join(f"Chương {int(record['chapter_id'][2:])}"
                                 for record in result.data["chapters"])
            weeks = ", ".join(f"tuần {int(record['week_id'][5:])}"
                               for record in result.data["weeks"])
            return (f"Chủ đề {_topic_label(result.data['topic'])} có trong {chapters}"
                    + (f"; theo lịch mẫu là {weeks}" if weeks else "") + ".")
        if result.kind == "TOPIC_OVERVIEW":
            chapter = result.data
            return (f"Chương {int(chapter['chapter_id'][2:])} ({chapter['title']}): "
                    f"{chapter['summary']}")
        if result.kind == "TOPIC_METHODS":
            chapter = result.data
            return (f"Chương {int(chapter['chapter_id'][2:])} gồm các mục: "
                    + "; ".join(chapter["subtopics"]) + ".")
        if result.kind == "TOPIC_RELATION":
            chapter = result.data["chapter"]
            evidence = result.data["evidence"].rstrip(".")
            return f"Có. Chương {int(chapter['chapter_id'][2:])} đề cập: {evidence}."
        if result.kind == "LO":
            return f"{result.data['lo']}: {result.data['description']}"
        if result.kind == "ASSIGNMENT_OVERVIEW":
            assignment = result.data
            parts = "; ".join(f"{part_id.replace('_', ' ')} - {part['title']}"
                              for part_id, part in assignment["parts"].items())
            return f"Bài tập lớn yêu cầu: {assignment['goal']} Các phần: {parts}."
        if result.kind in {"ASSIGNMENT_PART", "ASSIGNMENT_FEATURE"}:
            part = result.data
            details = (part.get("requirements") or part.get("minimum_requirements")
                       or part.get("optional_or_extension") or [])
            prefix = "Có. " if result.kind == "ASSIGNMENT_FEATURE" else ""
            return (f"{prefix}{part['part_id'].replace('_', ' ')} - {part['title']}"
                    + (f": {'; '.join(details)}." if details else "."))
        if result.kind == "ASSIGNMENT_OUTPUT":
            part = result.data
            return (f"{part['part_id'].replace('_', ' ')} cần xuất: "
                    + ", ".join(part["suggested_outputs"]) + ".")
        if result.kind == "DEADLINE":
            return f"Ngày nộp bài tập lớn: {result.data}."
        if result.kind == "RESOURCE":
            entries = []
            for resource in result.data["resources"]:
                authors = resource.get("authors") or resource.get("author")
                suffix = f" — {authors}" if authors else ""
                entries.append(f"{resource['title']}{suffix}")
            return "Tài liệu liên quan: " + "; ".join(entries) + "."
        if result.kind in {"RULE_POLICY", "RULE_PERMISSION"}:
            rule = result.data
            label = {"AI_USAGE": "sử dụng AI", "LLM_RAG": "LLM/RAG"}.get(
                rule["rule"], rule["rule"].replace("_", " ").lower()
            )
            return f"Quy định về {label}: {rule['text']}"
        return NOT_FOUND


def _topic_label(topic_id: str) -> str:
    return topic_id if topic_id in {"CFG", "PCFG", "WSD"} else topic_id.replace("_", " ").lower()
