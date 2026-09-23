"""End-to-end smoke checks for the first grounded Course Assistant question."""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.answer import NOT_UNDERSTOOD
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant


ROOT = Path(__file__).resolve().parents[1]


class FirstVerticalSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assistant = CourseAssistant.from_root(ROOT)

    def test_week_three_is_grounded_in_schedule(self) -> None:
        result = self.assistant.process("Tuần 3 học gì?", use_context=False)

        self.assertTrue(result.parse.accepted)
        self.assertEqual(result.parse.tree.leaves(), list(result.parse.tokens))
        self.assertEqual(result.semantic.intent, "GET_SCHEDULE")
        self.assertEqual(result.semantic.entity, "WEEK_03")
        self.assertEqual(result.semantic.slots["week"], "WEEK_03")
        self.assertTrue(result.query.found)
        self.assertIn("schedule.txt", result.query.sources[0])
        self.assertIn("Tuần 3", result.answer)
        self.assertIn(result.query.data["topics"][0], result.answer)

    def test_out_of_domain_question_stops_before_kb_lookup(self) -> None:
        result = self.assistant.process(
            "Hôm nay ở TP.HCM có mưa không?", use_context=False
        )

        self.assertEqual(result.parse.output(), "()")
        self.assertEqual(result.semantic.intent, "UNKNOWN")
        self.assertFalse(result.query.found)
        self.assertEqual(result.query.kind, "OUT_OF_SCOPE")
        self.assertEqual(result.query.sources, [])
        self.assertEqual(result.answer, NOT_UNDERSTOOD)

    def test_course_credit_query_is_grounded(self) -> None:
        result = self.assistant.process(
            "CO3085 có bao nhiêu tín chỉ?", use_context=False
        )

        self.assertTrue(result.parse.accepted)
        self.assertEqual(result.semantic.intent, "GET_COURSE_INFO")
        self.assertEqual(result.semantic.entity, "CO3085")
        self.assertEqual(result.semantic.slots["field"], "credits")
        self.assertEqual(result.semantic.source_branch, "Q_COURSE_CREDITS")
        self.assertEqual(result.query.kind, "COURSE_FIELD")
        self.assertTrue(result.query.found)
        self.assertEqual(result.query.sources, ["course_info.txt:credits"])
        self.assertIn("3 tín chỉ", result.answer)


if __name__ == "__main__":
    unittest.main()
