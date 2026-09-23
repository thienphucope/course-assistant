"""Behavioral checks for bounded CFG sentence generation."""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.generator import MAX_SENTENCES, SentenceGenerator
from hcmut.iaslab.nlp.app.grammar import Grammar
from hcmut.iaslab.nlp.app.parser import EarleyParser


class SentenceGeneratorTests(unittest.TestCase):
    def test_epsilon_unique_and_exact_statistics(self) -> None:
        grammar = Grammar.from_text(
            '%start S\nS -> OPTIONAL "x" | "x"\nOPTIONAL -> | "y"'
        )
        sentences, stats = SentenceGenerator(grammar).generate(limit=10, max_tokens=2)
        self.assertEqual(sentences, ["x", "y x"])
        self.assertEqual(stats.requested, 10)
        self.assertEqual(stats.produced, 2)
        self.assertGreater(stats.explored_forms, 2)
        self.assertFalse(stats.truncated)

    def test_left_recursion_and_token_limit(self) -> None:
        grammar = Grammar.from_text('%start S\nS -> S "a" | "a"')
        sentences, stats = SentenceGenerator(grammar).generate(limit=10, max_tokens=3)
        self.assertEqual(sentences, ["a", "a a", "a a a"])
        self.assertTrue(stats.truncated)

    def test_state_cap_stops_nullable_recursion(self) -> None:
        grammar = Grammar.from_text('%start S\nS -> S S |')
        sentences, stats = SentenceGenerator(grammar, max_states=20).generate(
            limit=100, max_tokens=2
        )
        self.assertEqual(sentences, [""])
        self.assertLessEqual(stats.explored_forms, 20)
        self.assertTrue(stats.truncated)

    def test_output_cap_and_invalid_bounds(self) -> None:
        grammar = Grammar.from_text('%start S\nS -> "x"')
        sentences, stats = SentenceGenerator(grammar).generate(limit=MAX_SENTENCES + 1)
        self.assertEqual(sentences, ["x"])
        self.assertEqual(stats.requested, MAX_SENTENCES + 1)
        self.assertTrue(stats.truncated)
        with self.assertRaises(ValueError):
            SentenceGenerator(grammar).generate(limit=-1)
        with self.assertRaises(ValueError):
            SentenceGenerator(grammar).generate(max_tokens=-1)
        with self.assertRaises(ValueError):
            SentenceGenerator(grammar, max_states=0)

    def test_project_sentences_parse_with_shared_grammar(self) -> None:
        grammar = Grammar.from_file(Path(__file__).parents[1] / "data" / "grammar.cfg")
        sentences, stats = SentenceGenerator(grammar).generate(limit=50, max_tokens=24)
        self.assertEqual(stats.produced, 50)
        self.assertEqual(len(sentences), len(set(sentences)))
        parser = EarleyParser(grammar)
        for sentence in sentences:
            with self.subTest(sentence=sentence):
                self.assertTrue(parser.parse(sentence).accepted)


if __name__ == "__main__":
    unittest.main()
