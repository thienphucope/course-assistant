"""Acceptance checks for the required question forms in the shared CFG.

These tests deliberately stop at syntax. Intent/entity accuracy and KB answers
belong to later milestones; a parse must still cover every input token.
"""

import re
import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.grammar import Grammar
from hcmut.iaslab.nlp.app.parser import EarleyParser
from hcmut.iaslab.nlp.app.tokenizer import tokenize


DATA = Path(__file__).resolve().parents[1] / "data"
SAMPLE_QUERIES = DATA / "scaffolding" / "sample_queries.txt"
CHALLENGE_QUERIES = DATA / "scaffolding" / "challenge_queries.txt"


def _read_queries(path: Path) -> dict[str, str]:
    """Read fixture rows while ignoring headings and optional columns."""
    questions: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        fields = [field.strip() for field in line.split("|")]
        if len(fields) < 4 or not re.fullmatch(r"[A-Z]\d{3}", fields[0]):
            continue
        question_id, sentence = fields[:2]
        if question_id in questions:
            raise ValueError(f"Duplicate question ID {question_id} in {path}")
        questions[question_id] = sentence
    return questions


class GrammarCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = EarleyParser(Grammar.from_file(DATA / "grammar.cfg"))
        cls.samples = _read_queries(SAMPLE_QUERIES)

    def _assert_full_parse(self, sentence: str):
        result = self.parser.parse(sentence)
        self.assertTrue(result.accepted, f"No parse for: {sentence!r}")
        self.assertIsNotNone(result.tree)
        self.assertEqual(result.tree.leaves(), list(result.tokens))
        self.assertEqual(result.tree.label, "S")
        return result.tree

    def test_all_25_core_sample_questions_parse_completely(self) -> None:
        expected_ids = {f"Q{number:03d}" for number in range(1, 26)}
        self.assertTrue(expected_ids <= self.samples.keys())
        for question_id in sorted(expected_ids):
            with self.subTest(question_id=question_id):
                self._assert_full_parse(self.samples[question_id])

    def test_all_seven_required_groups_have_a_parse(self) -> None:
        # A successful parse must also take the intended grammar branch.
        representatives = {
            "course information": ("Q001", "Q_COURSE_CREDITS"),
            "schedule": ("Q004", "Q_SCHEDULE_WEEK"),
            "topics": ("Q006", "Q_TOPIC_BY_NAME"),
            "assignment": ("Q011", "Q_ASSIGNMENT_OVERVIEW"),
            "resources": ("Q018", "Q_RESOURCE"),
            "rules": ("Q014", "Q_RULE_PERMISSION"),
        }
        for group, (question_id, branch) in representatives.items():
            with self.subTest(group=group):
                tree = self._assert_full_parse(self.samples[question_id])
                self.assertIsNotNone(tree.first(branch))

        challenges = _read_queries(CHALLENGE_QUERIES)
        self.assertIn("C001", challenges)
        deadline_tree = self._assert_full_parse(challenges["C001"])
        self.assertIsNotNone(deadline_tree.first("Q_DEADLINE"))

    def test_out_of_domain_samples_and_trailing_token_are_rejected(self) -> None:
        for question_id in ("Q026", "Q027", "Q028"):
            with self.subTest(question_id=question_id):
                result = self.parser.parse(self.samples[question_id])
                self.assertFalse(result.accepted)
                self.assertIsNone(result.tree)
                self.assertEqual(result.output(), "()")

        # Earley acceptance must require the complete token span, not a prefix.
        result = self.parser.parse(self.samples["Q004"] + " abc")
        self.assertFalse(result.accepted)
        self.assertEqual(result.output(), "()")

    def test_identifier_tokens_survive_normalization(self) -> None:
        self.assertEqual(tokenize("CO3085"), ["co3085"])
        self.assertEqual(tokenize("L.O.2.5"), ["lo2.5"])
        self.assertEqual(tokenize("LLM/RAG"), ["llm/rag"])


if __name__ == "__main__":
    unittest.main()
