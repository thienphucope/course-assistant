"""Grounded, template-based answer generation."""

from __future__ import annotations

import re
from typing import Any

from .query import QueryResult
from .semantic import SemanticFrame


NOT_FOUND = "Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu của môn học."
NOT_UNDERSTOOD = "Xin lỗi, câu hỏi không thuộc văn phạm hoặc ngoài phạm vi Course Assistant."
MISSING_CONTEXT = "Xin lỗi, tôi chưa có đủ ngữ cảnh để hiểu tham chiếu trong câu hỏi này."

TOPIC_LABELS = {
    "CFG": "CFG",
    "PCFG": "PCFG",
    "WSD": "WSD",
    "QUESTION_ANSWERING": "question answering",
}


class AnswerGenerator:
    def generate(self, frame: SemanticFrame, result: QueryResult) -> str:
        if not result.found:
            if result.kind == "UNKNOWN":
                return NOT_UNDERSTOOD
            if result.kind == "UNRESOLVED_CONTEXT":
                return MISSING_CONTEXT
            return NOT_FOUND
        handler = getattr(self, f"_answer_{result.kind.lower()}", None)
        return handler(frame, result) if handler else NOT_FOUND

    @staticmethod
    def _answer_course_credits(frame: SemanticFrame, result: QueryResult) -> str:
        return f"Môn Xử lý Ngôn ngữ Tự nhiên (CO3085) có {result.data['credits']} tín chỉ."

    @staticmethod
    def _answer_course_parts(frame: SemanticFrame, result: QueryResult) -> str:
        parts = [_strip_part_prefix(value) for value in result.data["parts"]]
        return "Môn học gồm ba phần chính: " + "; ".join(parts) + "."

    @staticmethod
    def _answer_course_description(frame: SemanticFrame, result: QueryResult) -> str:
        return str(result.data["description"])

    @staticmethod
    def _answer_exam_duration(frame: SemanticFrame, result: QueryResult) -> str:
        exam = "Midterm" if result.data["exam"] == "MIDTERM" else "Final"
        duration = _minutes(str(result.data["format"]))
        suffix = f"{duration} phút" if duration else str(result.data["format"])
        return f"{exam} có thời lượng {suffix}."

    @staticmethod
    def _answer_assessment(frame: SemanticFrame, result: QueryResult) -> str:
        labels = {
            "class_attention_and_assignments": "chuyên cần và bài tập",
            "major_assignment": "bài tập lớn",
            "midterm_exam": "giữa kỳ",
            "final_exam": "cuối kỳ",
        }
        items = [f"{labels.get(key, key)}: {value}" for key, value in result.data.items()]
        return "Cách tính điểm gồm " + "; ".join(items) + "."

    @staticmethod
    def _answer_schedule_week(frame: SemanticFrame, result: QueryResult) -> str:
        record = result.data
        week = int(str(record["week_id"]).split("_")[-1])
        chapter_id = record.get("chapter_id")
        chapter = f"Chương {int(chapter_id[2:])}" if chapter_id else record.get("chapter", "không ghi chương")
        topics = ", ".join(record.get("topics", []))
        extras = []
        if record.get("activity"):
            extras.append(f"hoạt động: {record['activity']}")
        if record.get("milestone"):
            extras.append(f"mốc: {record['milestone']}")
        extra_text = f"; {'; '.join(extras)}" if extras else ""
        return f"Tuần {week} học {chapter}, gồm {topics}{extra_text}."

    @staticmethod
    def _answer_schedule_chapter(frame: SemanticFrame, result: QueryResult) -> str:
        chapter = int(str(result.data["chapter_id"])[2:])
        weeks = ", ".join(str(int(value.split("_")[-1])) for value in result.data["weeks"])
        return f"Chương {chapter} được học ở tuần {weeks}."

    @staticmethod
    def _answer_schedule_topics(frame: SemanticFrame, result: QueryResult) -> str:
        topics = " và ".join(_topic_label(str(topic)) for topic in result.data["topics"])
        weeks = ", ".join(str(int(record["week_id"].split("_")[-1])) for record in result.data["weeks"])
        return f"{topics} cùng xuất hiện trong nội dung tuần {weeks}."

    @staticmethod
    def _answer_topic_chapter(frame: SemanticFrame, result: QueryResult) -> str:
        record = result.data
        return f"Chương {record['chapter_number']} — {record['title']}: {record.get('summary', '')}"

    @staticmethod
    def _answer_topic_search(frame: SemanticFrame, result: QueryResult) -> str:
        topic = str(result.data["topic"])
        label = _topic_label(topic)
        chapters = result.data["chapters"]
        descriptions = ", ".join(f"Chương {item['chapter_number']} ({item['title']})" for item in chapters)
        return f"{label} được trình bày trong {descriptions}."

    @staticmethod
    def _answer_topic_relation(frame: SemanticFrame, result: QueryResult) -> str:
        data = result.data
        chapter = data["chapter"]
        relation = _topic_label(str(data["relation"]))
        if data["related"]:
            return f"Có. Chương {chapter['chapter_number']} có nội dung liên quan đến {relation}."
        return f"Không. Dữ liệu Chương {chapter['chapter_number']} không đề cập đến {relation}."

    @staticmethod
    def _answer_learning_outcome(frame: SemanticFrame, result: QueryResult) -> str:
        return f"{result.data['lo']}: {result.data['description']}"

    @staticmethod
    def _answer_lo_chapter(frame: SemanticFrame, result: QueryResult) -> str:
        chapter = result.data["chapter"]
        return f"{result.data['lo']} tương ứng với Chương {chapter['chapter_number']} — {chapter['title']}."

    @staticmethod
    def _answer_assignment_overview(frame: SemanticFrame, result: QueryResult) -> str:
        sections = ", ".join(value.replace("PART_", "Phần ") for value in result.data["sections"])
        return f"BTL {result.data['title']} có mục tiêu: {result.data['goal']} Các phần gồm {sections}."

    @staticmethod
    def _answer_assignment_section(frame: SemanticFrame, result: QueryResult) -> str:
        section = result.data["section"]
        if result.data.get("field") == "OUTPUTS":
            outputs = section.get("suggested_outputs", [])
            if not outputs:
                return NOT_FOUND
            return f"{section['section_id'].replace('PART_', 'Phần ')} có các output: {', '.join(outputs)}."
        requirement_keys = ("requirements", "minimum_requirements", "optional_or_extension")
        requirements: list[str] = []
        for key in requirement_keys:
            requirements.extend(section.get(key, []))
        feature = result.data.get("feature")
        prefix = "Có. " if feature else ""
        detail = ", ".join(requirements) if requirements else section.get("title", "")
        return f"{prefix}{section['section_id'].replace('PART_', 'Phần ')} — {section['title']}: {detail}."

    @staticmethod
    def _answer_deadline(frame: SemanticFrame, result: QueryResult) -> str:
        items = [
            f"tuần {int(item['week_id'].split('_')[-1])}: {item['milestone']}"
            for item in result.data
        ]
        return "Các mốc BTL trong dữ liệu mẫu là " + "; ".join(items) + "."

    @staticmethod
    def _answer_resource(frame: SemanticFrame, result: QueryResult) -> str:
        titles = [str(item.get("title", item.get("resource_id", ""))) for item in result.data]
        return "Tài liệu phù hợp: " + "; ".join(titles) + "."

    @staticmethod
    def _answer_rule(frame: SemanticFrame, result: QueryResult) -> str:
        return str(result.data["text"])


def _strip_part_prefix(value: str) -> str:
    return re.sub(r"^Part\s+[IVX]+\s*-\s*", "", value).strip()


def _minutes(value: str) -> str | None:
    match = re.search(r"(\d+)\s+minutes?", value, re.IGNORECASE)
    return match.group(1) if match else None


def _topic_label(topic: str) -> str:
    return TOPIC_LABELS.get(topic, topic.replace("_", " ").lower())
