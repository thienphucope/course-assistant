"""Batch deliverables stay aligned and work from an explicit project root."""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from hcmut.iaslab.nlp.app.cli import main
from hcmut.iaslab.nlp.app.paths import ProjectPaths


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class BatchOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name) / "project"
        shutil.copytree(SOURCE_ROOT / "data", self.root / "data")
        shutil.copytree(SOURCE_ROOT / "input", self.root / "input")

    def run_batch(self, *extra: str) -> tuple[int, str]:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(["--root", str(self.root), "batch", "--limit", "40", *extra])
        return code, stream.getvalue()

    def test_batch_recreates_eight_aligned_deliverables(self) -> None:
        code, message = self.run_batch()
        self.assertEqual(code, 0)
        self.assertIn("25 found, 1 not found, 3 outside", message)
        output = self.root / "output"
        expected = {"grammar.txt", "samples.txt", "parse-results.txt", "semantic.txt",
                    "intent-entity.txt", "query.txt", "answer.txt", "evaluation.txt"}
        self.assertEqual({path.name for path in output.iterdir()}, expected)
        self.assertEqual((output / "grammar.txt").read_text(encoding="utf-8"),
                         (self.root / "data" / "grammar.cfg").read_text(encoding="utf-8-sig"))
        self.assertEqual(len((output / "samples.txt").read_text(encoding="utf-8").splitlines()), 40)
        per_question = {name: (output / name).read_text(encoding="utf-8").splitlines()
                        for name in expected if name not in {"grammar.txt", "samples.txt",
                                                           "evaluation.txt"}}
        self.assertTrue(all(len(lines) == 29 for lines in per_question.values()))

        questions = (self.root / "input" / "sentences.txt").read_text(encoding="utf-8").splitlines()
        queries = [json.loads(line) for line in per_question["query.txt"]]
        answers = [json.loads(line) for line in per_question["answer.txt"]]
        frames = [json.loads(line) for line in per_question["intent-entity.txt"]]
        for index, question in enumerate(questions):
            self.assertEqual((queries[index]["line"], queries[index]["question"]),
                             (index + 1, question))
            self.assertEqual((answers[index]["line"], answers[index]["question"]),
                             (index + 1, question))
        self.assertEqual(per_question["semantic.txt"][3], "GET_SCHEDULE(week=WEEK_03)")
        self.assertEqual(frames[3]["entity"], "WEEK_03")
        self.assertEqual(queries[4]["sources"],
                         ["schedule.txt:WEEK 04", "schedule.txt:WEEK 05"])
        self.assertEqual([item["status"] for item in queries].count("FOUND"), 25)
        self.assertEqual([item["status"] for item in queries].count("NOT_FOUND"), 1)
        self.assertEqual([item["status"] for item in queries].count("OUT_OF_SCOPE"), 3)
        self.assertEqual(per_question["parse-results.txt"][25:28], ["()"] * 3)
        self.assertIn("không tìm thấy ngày nộp cụ thể", answers[28]["answer"])
        report = (output / "evaluation.txt").read_text(encoding="utf-8")
        self.assertIn("Sample core + out-of-scope", report)
        self.assertIn("Team challenge", report)
        self.assertIn("C012", report)

    def test_relative_input_is_resolved_under_root_and_skips_blank_comments(self) -> None:
        (self.root / "short.txt").write_text(
            "# demo\n\nTuần 3 học gì?\n  \nDeadline của bài tập lớn là khi nào?\n",
            encoding="utf-8",
        )
        code, _ = self.run_batch("--input", "short.txt")
        self.assertEqual(code, 0)
        output = self.root / "output"
        for name in ("parse-results.txt", "semantic.txt", "intent-entity.txt",
                     "query.txt", "answer.txt"):
            self.assertEqual(len((output / name).read_text(encoding="utf-8").splitlines()), 2)
        queries = [json.loads(line) for line in (output / "query.txt").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([item["status"] for item in queries], ["FOUND", "NOT_FOUND"])

    def test_empty_input_returns_clear_error(self) -> None:
        (self.root / "empty.txt").write_text("# only comment\n\n", encoding="utf-8")
        stream = io.StringIO()
        with redirect_stderr(stream):
            code = main(["--root", str(self.root), "batch", "--input", "empty.txt",
                         "--limit", "2"])
        self.assertEqual(code, 2)
        self.assertIn("No question lines", stream.getvalue())

    def test_project_discovery_works_outside_project_directory(self) -> None:
        previous = Path.cwd()
        try:
            os.chdir(self.workspace.name)
            self.assertEqual(ProjectPaths.discover().root, SOURCE_ROOT)
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
