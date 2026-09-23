"""Evaluation uses declared labels and reports real stage-specific misses."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from hcmut.iaslab.nlp.app.cli import main
from hcmut.iaslab.nlp.app.evaluate import (evaluate_cases, load_evaluation_cases,
                                           render_evaluation_report)
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLDING = ROOT / "data" / "scaffolding"


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assistant = CourseAssistant.from_root(ROOT)

    def test_four_and_six_column_fixtures_are_loaded_without_dropping_ids(self) -> None:
        supplied = load_evaluation_cases(SCAFFOLDING / "sample_queries.txt")
        gold = load_evaluation_cases(SCAFFOLDING / "gold_queries.txt")
        challenge = load_evaluation_cases(SCAFFOLDING / "challenge_queries.txt")
        self.assertEqual((len(supplied), len(gold), len(challenge)), (34, 28, 13))
        self.assertEqual(supplied[0].case_id, "Q001")
        self.assertIsNone(supplied[0].expected_query_status)
        self.assertEqual(gold[4].answer_contains, ("tuần 4", "tuần 5"))
        self.assertIsNone(gold[25].expected_entity)
        self.assertEqual(gold[25].expected_query_status, "OUT_OF_SCOPE")

    def test_stage_scores_and_real_challenge_failures(self) -> None:
        gold = evaluate_cases(self.assistant,
                              load_evaluation_cases(SCAFFOLDING / "gold_queries.txt"),
                              "Core")
        challenge = evaluate_cases(self.assistant,
                                   load_evaluation_cases(SCAFFOLDING / "challenge_queries.txt"),
                                   "Challenge")
        self.assertEqual((gold.passed, gold.total), (28, 28))
        self.assertEqual(gold.stage_score("answer_ok"), (28, 28))
        self.assertEqual((challenge.passed, challenge.total), (11, 13))
        failed_ids = [record.case.case_id for record in challenge.records if not record.passed]
        self.assertEqual(failed_ids, ["C012", "C013"])
        self.assertTrue(all(not record.parse_ok for record in challenge.records
                            if record.case.case_id in failed_ids))
        report = render_evaluation_report([gold, challenge])
        self.assertIn("39/41 (95.1%)", report)
        self.assertIn("First failed stage: tokenizer/grammar/parser", report)
        self.assertIn("not a full human judgment", report)

    def test_missing_answer_labels_are_not_counted_as_answer_accuracy(self) -> None:
        supplied = load_evaluation_cases(SCAFFOLDING / "sample_queries.txt")[:3]
        summary = evaluate_cases(self.assistant, supplied)
        self.assertEqual(summary.stage_score("answer_ok"), (0, 0))
        self.assertEqual(summary.stage_score("query_ok"), (0, 0))
        self.assertEqual(summary.stage_score("intent_ok"), (3, 3))

    def test_malformed_fixture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "bad.txt"
            fixture.write_text("C001 | x | UNKNOWN | OUT_OF_SCOPE | IMPOSSIBLE\n",
                               encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid status"):
                load_evaluation_cases(fixture)
            fixture.write_text("C001 | x | UNKNOWN | OUT_OF_SCOPE\n"
                               "C001 | y | UNKNOWN | OUT_OF_SCOPE\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate C001"):
                load_evaluation_cases(fixture)

    def test_cli_strict_mode_marks_known_challenge_misses(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(["--root", str(ROOT), "evaluate", "--strict"])
        self.assertEqual(code, 1)
        self.assertIn("11/13", stream.getvalue())
        self.assertIn("C012", (ROOT / "output" / "evaluation.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
