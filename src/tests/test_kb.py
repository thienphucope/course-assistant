"""Template tests for KB loading, schema validation, and reverse indexes.

Replace skipped cases as each loader is implemented. Test counts, canonical
keys, multiline fields, optional values, malformed records, and all cross-file
references rather than checking only one happy-path fact.
"""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.answer import AnswerGenerator, NOT_FOUND, NOT_UNDERSTOOD
from hcmut.iaslab.nlp.app.kb import KnowledgeBase
from hcmut.iaslab.nlp.app.query import QueryEngine
from hcmut.iaslab.nlp.app.semantic import SemanticFrame


KB_DIR = Path(__file__).resolve().parents[1] / "data" / "kb"


class KnowledgeBaseTests(unittest.TestCase):
    def test_loader_preserves_all_source_records(self) -> None:
        kb = KnowledgeBase.load(KB_DIR)
        self.assertEqual(len(kb.weeks), 15)
        self.assertEqual(len(kb.topics), 12)
        self.assertEqual(kb.chapter_weeks["CH04"], ["WEEK_04", "WEEK_05"])
        self.assertEqual(kb.weeks["WEEK_03"]["chapter_id"], "CH03")
        self.assertIn("context-free grammar", kb.weeks["WEEK_03"]["topics"])
        self.assertEqual(kb.validate(), [])

    def test_validation_reports_all_broken_references(self) -> None:
        kb = KnowledgeBase(
            weeks={"WEEK_03": {"week_id": "WEEK_03", "part": "Syntax", "topics": ["CFG"], "chapter_id": "CH99"}},
            topics={"CH03": {"chapter_id": "CH03"}},
        )
        errors = kb.validate()
        self.assertTrue(any("CH99 absent" in error for error in errors))
        self.assertTrue(any("missing reverse index" in error for error in errors))

    def test_empty_contract_is_explicit(self) -> None:
        kb = KnowledgeBase()
        self.assertEqual(kb.course, {})
        self.assertEqual(kb.resources, ())


class ScheduleQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = QueryEngine(KnowledgeBase.load(KB_DIR))
        cls.answers = AnswerGenerator()

    def test_week_question_uses_schedule_fact_and_source(self) -> None:
        frame = SemanticFrame("GET_SCHEDULE", "WEEK_03", {"week": "WEEK_03"})
        result = self.engine.execute(frame)
        self.assertTrue(result.found)
        self.assertEqual(result.kind, "SCHEDULE_WEEK")
        self.assertEqual(result.query, "KB.weeks[WEEK_03]")
        self.assertEqual(result.sources, ["schedule.txt:WEEK 03"])
        answer = self.answers.generate(frame, result)
        self.assertIn("Tuần 3", answer)
        self.assertIn("context-free grammar", answer)

    def test_unknown_and_missing_week_have_distinct_fallbacks(self) -> None:
        unknown = SemanticFrame.unknown()
        outside = self.engine.execute(unknown)
        self.assertEqual(outside.kind, "OUT_OF_SCOPE")
        self.assertEqual(self.answers.generate(unknown, outside), NOT_UNDERSTOOD)

        missing = SemanticFrame("GET_SCHEDULE", "WEEK_99", {"week": "WEEK_99"})
        no_fact = self.engine.execute(missing)
        self.assertEqual(no_fact.kind, "SCHEDULE_WEEK")
        self.assertFalse(no_fact.found)
        self.assertEqual(self.answers.generate(missing, no_fact), NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
