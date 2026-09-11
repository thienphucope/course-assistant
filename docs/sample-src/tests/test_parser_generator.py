from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hcmut.iaslab.nlp.app.generator import SentenceGenerator
from hcmut.iaslab.nlp.app.grammar import Grammar
from hcmut.iaslab.nlp.app.parser import EarleyParser


class ParserGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = Grammar.from_file(ROOT / "data" / "grammar.cfg")
        cls.parser = EarleyParser(cls.grammar)

    def test_valid_question_has_tree_and_preserves_tokens(self) -> None:
        result = self.parser.parse("Cho mình hỏi tuần 3 học gì ạ?")
        self.assertTrue(result.accepted)
        self.assertEqual(result.tree.leaves(), list(result.tokens))
        self.assertIn("Q_SCHEDULE_WEEK", result.output())

    def test_out_of_domain_question_is_rejected(self) -> None:
        result = self.parser.parse("Hôm nay ở TP.HCM có mưa không?")
        self.assertFalse(result.accepted)
        self.assertEqual(result.output(), "()")

    def test_trailing_unknown_token_is_rejected(self) -> None:
        self.assertFalse(self.parser.parse("Tuần 3 học gì xyz?").accepted)

    def test_generator_respects_limit_and_round_trips(self) -> None:
        sentences, stats = SentenceGenerator(self.grammar).generate(limit=120)
        self.assertEqual(len(sentences), 120)
        self.assertEqual(len(set(sentences)), 120)
        self.assertLessEqual(len(sentences), 10_000)
        rejected = [sentence for sentence in sentences if not self.parser.parse(sentence).accepted]
        self.assertEqual(rejected, [])
        self.assertEqual(stats.produced, 120)


if __name__ == "__main__":
    unittest.main()

