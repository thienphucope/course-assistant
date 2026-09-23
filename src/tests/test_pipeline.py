"""Tests for semantics, query, answer, and full pipeline orchestration.

Assert each intermediate artifact in ``PipelineResult`` so failures identify the
responsible stage. Add one case for every intent, explicit missing-KB behavior,
out-of-domain behavior, and ordered dialogue fixtures with reset boundaries.
"""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.parser import ParseResult
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant, PipelineResult
from hcmut.iaslab.nlp.app.query import QueryResult
from hcmut.iaslab.nlp.app.semantic import SemanticFrame


class PipelineTests(unittest.TestCase):
    def test_pipeline_result_exposes_semantic_contract(self) -> None:
        raw = SemanticFrame("GET_SCHEDULE", "WEEK_03", {"week": "WEEK_03"})
        result = PipelineResult(
            sentence="sample",
            parse=ParseResult("sample", ("sample",), None),
            raw_semantic=raw,
            semantic=raw,
            query=QueryResult("KB.weeks[WEEK_03]", False, "SCHEDULE_WEEK"),
            answer="sample answer",
        )
        self.assertEqual(result.detected_intent, "GET_SCHEDULE")
        self.assertEqual(result.detected_entity, "WEEK_03")

    def test_all_intents_are_grounded_end_to_end(self) -> None:
        assistant = CourseAssistant.from_root(Path(__file__).resolve().parents[1])
        cases = {
            "GET_COURSE_INFO": "Môn NLP có bao nhiêu tín chỉ?",
            "GET_SCHEDULE": "Tuần 3 học gì?",
            "GET_TOPIC": "Chương nào nói về CFG?",
            "GET_LO": "L.O.2.5 là gì?",
            "GET_ASSIGNMENT": "Phần I của bài tập lớn là gì?",
            "GET_RESOURCE": "Tài liệu nào liên quan đến Python NLP?",
            "GET_RULE": "Quy định về sử dụng AI là gì?",
        }
        for intent, question in cases.items():
            with self.subTest(intent=intent):
                result = assistant.process(question, use_context=False)
                self.assertEqual(result.semantic.intent, intent)
                self.assertTrue(result.query.found)
                self.assertTrue(result.query.sources)
                self.assertFalse(result.answer.startswith("Xin lỗi"))

    def test_dialogue_state_is_scoped_and_resettable(self) -> None:
        self.skipTest("Optional dialogue extension is outside the required baseline")


if __name__ == "__main__":
    unittest.main()
