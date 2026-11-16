"""Independent counterexamples found while documenting completed tickets."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from hcmut.iaslab.nlp.app.answer import NOT_FOUND
from hcmut.iaslab.nlp.app.dialogue import DialogueContext
from hcmut.iaslab.nlp.app.evaluate import EvaluationCase, evaluate_cases, load_evaluation_cases, load_dialogue_cases
from hcmut.iaslab.nlp.app.grammar import Grammar, GrammarError
from hcmut.iaslab.nlp.app.generator import SentenceGenerator
from hcmut.iaslab.nlp.app.output import write_grammar
from hcmut.iaslab.nlp.app.parser import ParseResult
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
from hcmut.iaslab.nlp.app.query import QueryResult
from hcmut.iaslab.nlp.app.semantic import SemanticFrame
from hcmut.iaslab.nlp.app.tree import Tree

SRC = Path(__file__).resolve().parents[1]
REPO = SRC.parent


class AuditRegressions(unittest.TestCase):
    def setUp(self):
        self.assistant = CourseAssistant.from_root(SRC)

    def test_missing_resource_topic_must_not_match_every_book(self):
        for slots in ({}, {"topic": None}, {"topic": ""}, {"topic": "   "}):
            with self.subTest(slots=slots):
                frame = SemanticFrame("GET_RESOURCE", slots=slots)
                result = self.assistant.components.query_engine.execute(frame)
                self.assertFalse(result.found)
                self.assertEqual(self.assistant.components.answer_generator.generate(frame, result), NOT_FOUND)

    def test_unknown_chapter_has_no_resource_recommendation(self):
        for slots in ({"chapter": "CH99", "topic": "CH99"}, {"topic": "CH99"}):
            with self.subTest(slots=slots):
                result = self.assistant.components.query_engine.execute(SemanticFrame("GET_RESOURCE", slots=slots))
                self.assertFalse(result.found)

    def test_other_assignment_does_not_return_btl01_facts(self):
        for intent, slots in (("GET_ASSIGNMENT", {"assignment": "OTHER", "section": "OVERVIEW"}),
                              ("GET_ASSIGNMENT", {"assignment": "OTHER", "section": "PART_I"}),
                              ("GET_DEADLINE", {"assignment": "OTHER"})):
            with self.subTest(intent=intent, slots=slots):
                self.assertFalse(self.assistant.components.query_engine.execute(SemanticFrame(intent, slots=slots)).found)

    def test_chapter_from_lo_answer_becomes_the_recent_chapter(self):
        for question in ("Chương 4 nói về gì?", "LO2.5 là gì?", "Nội dung này nằm ở chương nào?"):
            self.assertTrue(self.assistant.process(question).query.found)
        result = self.assistant.process("Nó có liên quan đến parsing không?")
        self.assertEqual(result.semantic.entity, "CH06")
        self.assertEqual(self.assistant.components.context.last_chapter, "CH06")

    def test_zero_history_limit_is_bounded_without_disabling_typed_context(self):
        context = DialogueContext(history_limit=0)
        for _ in range(3):
            context.update(SemanticFrame("GET_TOPIC", "CH03"), QueryResult("test", True, "TOPIC_CHAPTER"))
        self.assertEqual(context.history, [])
        self.assertEqual(context.last_chapter, "CH03")

    def test_bare_lowercase_symbol_is_not_a_quoted_terminal(self):
        for symbol in ("missing", "MISSING_lower"):
            with self.subTest(symbol=symbol), self.assertRaises(GrammarError):
                Grammar.from_text(f"%start S\nS -> {symbol}")

    def test_accepted_out_of_scope_parse_cannot_score_as_correct(self):
        result = self.assistant.process("Hôm nay trời có mưa không?")
        result.parse = ParseResult(result.sentence, result.parse.tokens, Tree("S", tuple(result.parse.tokens)))
        fake = Mock()
        fake.process.return_value = result
        summary = evaluate_cases(fake, [EvaluationCase("X001", result.sentence, "UNKNOWN", "OUT_OF_SCOPE", "SKIPPED")])
        self.assertEqual(summary.joint_correct, 0)
        self.assertIn("false acceptance", summary.records[0].diagnosis)

    def test_not_found_answer_must_use_the_fallback_even_with_required_terms(self):
        result = self.assistant.process("Tuần 99 học gì?")
        result.answer = "không tìm thấy thông tin này; tuần 99 học nội dung tự tạo"
        fake = Mock()
        fake.process.return_value = result
        summary = evaluate_cases(fake, [EvaluationCase("X001", result.sentence, "GET_SCHEDULE", "WEEK_99",
                                                      "NOT_FOUND", ("không tìm thấy thông tin này",))])
        self.assertFalse(summary.records[0].answer_correct)

    def test_malformed_duplicate_and_invalid_status_cases_are_rejected(self):
        records = ["X001 | question | UNKNOWN\n",
                   "X0001 | question | UNKNOWN | OUT_OF_SCOPE | SKIPPED\n",
                   "X001 | question | UNKNOWN | OUT_OF_SCOPE | MAYBE\n",
                   "X001 | question | UNKNOWN | OUT_OF_SCOPE | SKIPPED\n" * 2]
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "cases.txt"
            for record in records:
                with self.subTest(record=record), self.assertRaises(ValueError):
                    path.write_text(record, encoding="utf-8")
                    load_evaluation_cases(path)

    def test_broken_or_duplicate_dialogue_cannot_disappear_from_scoring(self):
        valid = 'DIALOGUE 01\nU1: Chương 3 nói về gì?\nEXPECTED_REFERENCE: nó -> CH03\n'
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "dialogues.txt"
            for record in ('DIALOGUE 01\nU1: Chương 3 nói về gì?\n', valid * 2, ''):
                with self.subTest(record=record), self.assertRaises(ValueError):
                    path.write_text(record, encoding="utf-8")
                    load_dialogue_cases(path)

    def test_checker_fails_for_new_challenge_regression(self):
        with TemporaryDirectory() as temporary:
            grammar = Path(temporary) / "grammar.cfg"
            grammar.write_text((SRC / "data/grammar.cfg").read_text(encoding="utf-8").replace(
                '"dịch" "máy"', '"máy" "dịch"'), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(REPO / "tools/check_grammar.py"),
                                        "--grammar", str(grammar), "--samples", "26"],
                                       capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
            self.assertIn("C013", completed.stdout)
            self.assertIn("challenge regressions", completed.stdout)

    def test_grammar_export_preserves_trailing_lines(self):
        source = (SRC / "data/grammar.cfg").read_text(encoding="utf-8") + "\n\n"
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "grammar.txt"
            write_grammar(path, source)
            self.assertEqual(path.read_text(encoding="utf-8"), source)
            self.assertNotIn(b"\r", path.read_bytes())

    def test_checker_uses_explicit_cfg_when_default_cfg_is_broken(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(SRC / "data", root / "data")
            (root / "data/grammar.cfg").write_text("not a CFG", encoding="utf-8")
            completed = subprocess.run([sys.executable, str(REPO / "tools/check_grammar.py"),
                                        "--root", str(root), "--grammar", str(SRC / "data/grammar.cfg"),
                                        "--samples", "26"], capture_output=True, text=True,
                                       encoding="utf-8", timeout=30)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("official: 42/42", completed.stdout)

    def test_generation_terminates_for_nonproductive_and_nullable_growth(self):
        for rules in ('S -> S S', 'S -> S S |', 'S -> "x" "y"'):
            with self.subTest(rules=rules):
                sentences, stats = SentenceGenerator(Grammar.from_text('%start S\n' + rules)).generate(1, max_tokens=1)
                self.assertEqual(sentences, [])
                self.assertLess(stats.explored_forms, 100)
                self.assertTrue(stats.truncated)

    def test_length_cap_keeps_short_sentence_behind_nested_nullable(self):
        grammar = Grammar.from_text('%start S\nS -> A A A A A A A A "x"\nA -> B B B B B B B B B B\nB -> ')
        sentences, stats = SentenceGenerator(grammar).generate(5, max_tokens=1)
        self.assertEqual(sentences, ["X"])
        self.assertFalse(stats.truncated)

    def test_checker_notes_known_gap_that_now_passes(self):
        spec = importlib.util.spec_from_file_location("check_grammar_under_test", REPO / "tools/check_grammar.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        checker.KNOWN_CHALLENGE_GAPS = checker.KNOWN_CHALLENGE_GAPS | {"C001"}
        output = io.StringIO()
        with redirect_stdout(output):
            code = checker.main(["--samples", "26"])
        self.assertEqual(code, 0, output.getvalue())
        self.assertIn("NOTE: known challenge gaps now pass: C001", output.getvalue())


if __name__ == "__main__":
    unittest.main()
