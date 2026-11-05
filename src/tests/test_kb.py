"""Template tests for KB loading, schema validation, and reverse indexes.

Replace skipped cases as each loader is implemented. Test counts, canonical
keys, multiline fields, optional values, malformed records, and all cross-file
references rather than checking only one happy-path fact.
"""

import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from hcmut.iaslab.nlp.app.kb import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    def test_loader_preserves_all_source_records(self) -> None:
        kb = KnowledgeBase.load(Path(__file__).resolve().parents[1] / "data/kb")
        self.assertEqual((len(kb.weeks), len(kb.topics), len(kb.resources)), (15, 12, 8))
        self.assertEqual(kb.chapter_weeks["CH04"], ["WEEK_04", "WEEK_05"])
        self.assertNotIn("chapter_id", kb.weeks["WEEK_15"])
        self.assertIn("hiểu ngôn ngữ tự nhiên", kb.course["learning_outcomes"]["LO1.1"])
        self.assertEqual(kb.resources[-1]["resource_id"], "REFERENCE_5")
        self.assertNotIn("study_note", kb.resources[-1])
        self.assertEqual(kb.validate(), [])

    def test_validation_reports_all_broken_references(self) -> None:
        kb = KnowledgeBase.load(Path(__file__).resolve().parents[1] / "data/kb")
        weeks = deepcopy(kb.weeks)
        weeks["WEEK_03"]["chapter_id"] = "CH99"
        reverse = deepcopy(kb.chapter_weeks)
        reverse["CH04"].append("WEEK_99")
        errors = replace(kb, weeks=weeks, chapter_weeks=reverse).validate()
        self.assertTrue(any("CH99" in error for error in errors))
        self.assertTrue(any("WEEK_99" in error for error in errors))
        self.assertTrue(any("disagrees" in error for error in errors))

    def test_loader_rejects_duplicate_week(self) -> None:
        source = Path(__file__).resolve().parents[1] / "data/kb"
        with TemporaryDirectory() as directory:
            target = Path(directory) / "kb"
            shutil.copytree(source, target)
            with (target / "schedule.txt").open("a", encoding="utf-8") as handle:
                handle.write("\nWEEK 03\n")
            with self.assertRaisesRegex(ValueError, "duplicate WEEK_03"):
                KnowledgeBase.load(target)

    def test_loader_rejects_broken_cross_reference(self) -> None:
        source = Path(__file__).resolve().parents[1] / "data/kb"
        with TemporaryDirectory() as directory:
            target = Path(directory) / "kb"
            shutil.copytree(source, target)
            schedule = target / "schedule.txt"
            schedule.write_text(
                schedule.read_text(encoding="utf-8").replace("Chapter 3", "Chapter 99"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "CH99"):
                KnowledgeBase.load(target)

    def test_loader_reports_missing_file(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                KnowledgeBase.load(directory)

    def test_empty_contract_is_explicit(self) -> None:
        kb = KnowledgeBase()
        self.assertEqual(kb.course, {})
        self.assertEqual(kb.resources, ())


if __name__ == "__main__":
    unittest.main()
