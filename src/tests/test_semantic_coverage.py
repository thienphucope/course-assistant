"""Check real parse trees against supplied intent/entity labels and every core branch."""

import json
import re
import tempfile
import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.entities import EntityLexicon
from hcmut.iaslab.nlp.app.grammar import Grammar
from hcmut.iaslab.nlp.app.output import write_semantic_results
from hcmut.iaslab.nlp.app.parser import EarleyParser
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
from hcmut.iaslab.nlp.app.semantic import SemanticInterpreter


ROOT = Path(__file__).resolve().parents[1]


class SemanticCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        grammar = Grammar.from_file(ROOT / "data" / "grammar.cfg")
        cls.parser = EarleyParser(grammar)
        cls.interpreter = SemanticInterpreter(
            EntityLexicon.from_file(ROOT / "data" / "scaffolding" / "entities.txt")
        )
        cls.grammar = grammar

    def interpret(self, question: str):
        result = self.parser.parse(question)
        self.assertTrue(result.accepted, question)
        return self.interpreter.interpret(result.tree)

    def test_all_25_supplied_independent_questions_match_gold_labels(self) -> None:
        fixture = (ROOT / "data" / "scaffolding" / "sample_queries.txt").read_text(
            encoding="utf-8-sig"
        )
        checked = 0
        for line in fixture.splitlines():
            if not re.match(r"Q0(?:0[1-9]|1\d|2[0-5])\s*\|", line):
                continue
            case_id, question, intent, entity = (part.strip() for part in line.split("|", 3))
            with self.subTest(case=case_id):
                frame = self.interpret(question)
                self.assertEqual((frame.intent, frame.entity), (intent, entity))
                self.assertIsNotNone(frame.source_branch)
            checked += 1
        self.assertEqual(checked, 25)

    def test_every_required_q_branch_has_semantic_mapping(self) -> None:
        # These questions cover required branches absent from the 25 gold rows.
        extra = [
            ("NLP học về gì?", "Q_COURSE_DESCRIPTION", "GET_COURSE_INFO", "CO3085"),
            ("Midterm thi khi nào?", "Q_COURSE_EXAM_TIME", "GET_COURSE_INFO", "MIDTERM"),
            ("Điểm được tính như thế nào?", "Q_COURSE_ASSESSMENT", "GET_COURSE_INFO", "CO3085"),
            ("Ai dạy môn NLP?", "Q_INSTRUCTOR", "GET_COURSE_INFO", "CO3085"),
            ("CFG và PCFG nằm ở tuần nào?", "Q_SCHEDULE_TOPICS", "GET_SCHEDULE", "CFG"),
            ("Phần I cần xuất file gì?", "Q_ASSIGNMENT_OUTPUT", "GET_ASSIGNMENT", "PART_I"),
        ]
        for question, branch, intent, entity in extra:
            with self.subTest(branch=branch):
                frame = self.interpret(question)
                self.assertEqual((frame.source_branch, frame.intent, frame.entity),
                                 (branch, intent, entity))
        week_topics = self.interpret("CFG và PCFG nằm ở tuần nào?")
        self.assertEqual(week_topics.slots["topics"], ["CFG", "PCFG"])

        all_branches = {rule.lhs for rule in self.grammar.rules if rule.lhs.startswith("Q_")}
        required_branches = {name for name in all_branches if not name.startswith("Q_CONTEXT_")}
        gold_questions = [
            line.split("|", 3)[1].strip()
            for line in (ROOT / "data" / "scaffolding" / "sample_queries.txt")
            .read_text(encoding="utf-8-sig").splitlines()
            if re.match(r"Q0(?:0[1-9]|1\d|2[0-5])\s*\|", line)
        ]
        observed = {self.interpret(question).source_branch for question in gold_questions}
        observed.update(self.interpret(question).source_branch for question, *_ in extra)
        observed.add(self.interpret("Deadline của bài tập lớn là khi nào?").source_branch)
        self.assertEqual(observed, required_branches)

    def test_aliases_are_resolved_from_tree_nodes(self) -> None:
        cases = [
            ("Chương nào nói về context-free grammar?", "CFG"),
            ("L.O.2.5 là gì?", "LO2.5"),
            ("Cho mình hỏi Chương 4 học vào tuần nào nhé?", "CH04"),
            ("Có được dùng thư viện ngoài không?", "EXTERNAL_LIBRARIES"),
            ("Bài tập lớn có phần parser không?", "PART_I"),
        ]
        for question, expected in cases:
            with self.subTest(question=question):
                self.assertEqual(self.interpret(question).entity, expected)

    def test_out_of_scope_and_missing_fact_are_not_confused(self) -> None:
        out_of_scope = self.parser.parse("Hôm nay ở TP.HCM có mưa không?")
        self.assertFalse(out_of_scope.accepted)
        self.assertEqual(self.interpreter.interpret(out_of_scope.tree).intent, "UNKNOWN")
        deadline = self.interpret("Deadline của bài tập lớn là khi nào?")
        self.assertEqual((deadline.intent, deadline.entity), ("GET_DEADLINE", "BTL01"))

    def test_chapter_schedule_uses_both_week_records(self) -> None:
        result = CourseAssistant.from_root(ROOT).process("Chương 4 học vào tuần nào?")
        self.assertEqual((result.semantic.intent, result.semantic.entity),
                         ("GET_SCHEDULE", "CH04"))
        self.assertEqual(result.query.kind, "SCHEDULE_CHAPTER")
        self.assertTrue(result.query.found)
        self.assertIn("tuần 4", result.answer)
        self.assertIn("tuần 5", result.answer)

    def test_semantic_files_keep_input_order_and_json_ids(self) -> None:
        questions = (ROOT / "input" / "sentences.txt").read_text(encoding="utf-8").splitlines()
        frames = [self.interpreter.interpret(self.parser.parse(question).tree)
                  for question in questions]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_semantic_results(output, frames)
            predicates = (output / "semantic.txt").read_text(encoding="utf-8").splitlines()
            records = [json.loads(line) for line in
                       (output / "intent-entity.txt").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(predicates), len(questions))
        self.assertEqual(len(records), len(questions))
        self.assertEqual(predicates[3], "GET_SCHEDULE(week=WEEK_03)")
        self.assertEqual(records[3]["entity"], "WEEK_03")
        self.assertEqual(predicates[25:28], ["UNKNOWN()"] * 3)
        self.assertEqual(records[28]["intent"], "GET_DEADLINE")


if __name__ == "__main__":
    unittest.main()
