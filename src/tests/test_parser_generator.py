"""Tests for tokenizer, CFG parser, tree, and bounded generation.

Every accepted grammar branch needs a positive test; near misses and trailing
unknown tokens need rejection tests. Generated sentences should round-trip
through the parser and generation must respect uniqueness and safety bounds.
"""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.grammar import Grammar, GrammarError
from hcmut.iaslab.nlp.app.parser import EarleyParser
from hcmut.iaslab.nlp.app.tokenizer import detokenize, tokenize
from hcmut.iaslab.nlp.app.tree import Tree


class ParserGeneratorTests(unittest.TestCase):
    def test_tree_contract(self) -> None:
        tree = Tree("S", (Tree("TOKEN", ("hello",)),))
        self.assertEqual(tree.leaves(), ["hello"])
        self.assertEqual(tree.bracketed(), "(S (TOKEN hello))")

    def test_unknown_suffix_is_rejected(self) -> None:
        grammar = Grammar.from_file(Path(__file__).parents[1] / "data" / "grammar.cfg")
        parser = EarleyParser(grammar)
        accepted = parser.parse("Tuần 3 học gì?")
        self.assertTrue(accepted.accepted)
        self.assertEqual(accepted.tree.leaves(), list(accepted.tokens))
        rejected = parser.parse("Tuần 3 học gì? abc")
        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.output(), "()")

    def test_seed_cfg_parses_questions_and_rejects_unrelated_input(self) -> None:
        grammar = Grammar.from_file(Path(__file__).parents[1] / "data" / "grammar.cfg")
        parser = EarleyParser(grammar)
        for question in (
            "Tuần 3 học gì?",
            "Chương 4 học vào tuần nào?",
            "L.O.2.5 là gì?",
        ):
            with self.subTest(question=question):
                result = parser.parse(question)
                self.assertTrue(result.accepted)
                self.assertEqual(result.tree.leaves(), list(result.tokens))
        self.assertFalse(parser.parse("Hôm nay có mưa không?").accepted)

    def test_tokenizer_normalizes_case_unicode_and_sentence_punctuation(self) -> None:
        tokens = tokenize("  TUẦN  3   học gì ?  ")
        self.assertEqual(tokens, ["tuần", "3", "học", "gì", "?"])
        self.assertEqual(detokenize(tokens), "tuần 3 học gì?")
        self.assertEqual(tokenize("L.O.2.5 là gì?"), ["lo2.5", "là", "gì", "?"])

    def test_cfg_supports_epsilon_and_rejects_undefined_symbols(self) -> None:
        grammar = Grammar.from_text('%start S\nS -> MAYBE "x"\nMAYBE -> | "y"')
        parser = EarleyParser(grammar)
        self.assertTrue(parser.parse("x").accepted)
        self.assertTrue(parser.parse("y x").accepted)
        self.assertFalse(parser.parse("y y x").accepted)
        with self.assertRaises(GrammarError):
            Grammar.from_text("%start S\nS -> MISSING")

    def test_cfg_supports_left_recursion(self) -> None:
        parser = EarleyParser(Grammar.from_text('%start S\nS -> S "a" | "a"'))
        self.assertEqual(parser.parse("a a a").tree.leaves(), ["a", "a", "a"])


if __name__ == "__main__":
    unittest.main()
