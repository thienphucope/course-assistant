"""Focused checks for the first parse-tree-to-meaning example."""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.entities import EntityLexicon
from hcmut.iaslab.nlp.app.semantic import SemanticInterpreter
from hcmut.iaslab.nlp.app.tree import Tree


ENTITIES = Path(__file__).resolve().parents[1] / "data" / "scaffolding" / "entities.txt"


class SemanticSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lexicon = EntityLexicon.from_file(ENTITIES)
        cls.interpreter = SemanticInterpreter(cls.lexicon)

    def test_aliases_are_case_insensitive_and_family_specific(self) -> None:
        self.assertEqual(self.lexicon.resolve_week("  TUẦN   3  "), "WEEK_03")
        self.assertEqual(self.lexicon.resolve_week("week_03"), "WEEK_03")
        self.assertEqual(self.lexicon.resolve_chapter("Chương 4"), "CH04")
        self.assertEqual(self.lexicon.resolve("COURSE_PART", "Phần I"), "COURSE_PART_I")
        self.assertEqual(self.lexicon.resolve_assignment_part("Phần I"), "PART_I")
        self.assertIsNone(self.lexicon.resolve_week("Chương 3"))

    def test_schedule_week_tree_produces_canonical_frame(self) -> None:
        tree = Tree("S", (
            Tree("QUESTION", (
                Tree("Q_SCHEDULE_WEEK", (
                    Tree("WEEK_ENTITY", ("tuần", Tree("WEEK_NUMBER", ("3",)))),
                    "học", "gì",
                )),
            )),
        ))
        frame = self.interpreter.interpret(tree)
        self.assertEqual(frame.intent, "GET_SCHEDULE")
        self.assertEqual(frame.entity, "WEEK_03")
        self.assertEqual(frame.slots, {"week": "WEEK_03"})
        self.assertEqual(frame.source_branch, "Q_SCHEDULE_WEEK")

    def test_unknown_and_optional_trees_are_distinct(self) -> None:
        self.assertEqual(self.interpreter.interpret(None).intent, "UNKNOWN")
        self.assertEqual(
            self.interpreter.interpret(Tree("Q_COURSE_CREDITS")).intent,
            "UNKNOWN",
        )
        self.assertEqual(
            self.interpreter.interpret(Tree("Q_CONTEXT_NEXT_CHAPTER")).intent,
            "UNSUPPORTED",
        )
        self.assertEqual(self.interpreter.interpret(Tree("Q_SCHEDULE_WEEK")).intent, "UNKNOWN")
        missing_week = Tree("Q_SCHEDULE_WEEK", (Tree("WEEK_ENTITY", ("tuần", "99")),))
        self.assertEqual(self.interpreter.interpret(missing_week).intent, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
