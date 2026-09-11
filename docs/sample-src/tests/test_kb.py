from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hcmut.iaslab.nlp.app.kb import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = KnowledgeBase.load(ROOT / "data" / "kb")

    def test_all_source_records_are_loaded(self) -> None:
        self.assertEqual(self.kb.validate(), [])
        self.assertEqual(len(self.kb.weeks), 15)
        self.assertEqual(len(self.kb.topics), 12)
        self.assertEqual(len(self.kb.resources), 8)

    def test_reverse_chapter_to_week_index(self) -> None:
        self.assertEqual(self.kb.chapter_weeks["CH04"], ["WEEK_04", "WEEK_05"])

    def test_multiline_learning_outcome_is_joined(self) -> None:
        value = self.kb.course["learning_outcomes"]["LO4"]
        self.assertIn("hỏi đáp đơn giản", value)

    def test_milestones_are_not_hardcoded(self) -> None:
        milestone_weeks = [week for week, record in self.kb.weeks.items() if record.get("milestone")]
        self.assertEqual(milestone_weeks, ["WEEK_08", "WEEK_12", "WEEK_15"])


if __name__ == "__main__":
    unittest.main()

