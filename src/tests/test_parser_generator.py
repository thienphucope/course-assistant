"""Template tests for tokenizer, CFG parser, tree, and bounded generation.

Every accepted grammar branch needs a positive test; near misses and trailing
unknown tokens need rejection tests. Generated sentences should round-trip
through the parser and generation must respect uniqueness and safety bounds.
"""

import unittest
from collections import Counter
from pathlib import Path

from hcmut.iaslab.nlp.app.grammar import Grammar, GrammarError
from hcmut.iaslab.nlp.app.parser import EarleyParser
from hcmut.iaslab.nlp.app.generator import SentenceGenerator
from hcmut.iaslab.nlp.app.tree import Tree


class ParserGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar = Grammar.from_file(Path(__file__).resolve().parents[1] / "data/grammar.cfg")
        cls.parser = EarleyParser(cls.grammar)

    def test_tree_contract(self) -> None:
        tree = Tree("S", (Tree("TOKEN", ("hello",)),))
        self.assertEqual(tree.leaves(), ["hello"])
        self.assertEqual(tree.bracketed(), "(S (TOKEN hello))")

    def test_valid_question_round_trips(self) -> None:
        sentences, stats = SentenceGenerator(self.grammar).generate(260)
        self.assertEqual(stats.produced, 260)
        self.assertEqual(len(sentences), len(set(sentences)))
        branches = Counter()
        for sentence in sentences:
            self.assertTrue(sentence[0].isupper())
            self.assertTrue(sentence.endswith("?"))
            result = self.parser.parse(sentence)
            self.assertTrue(result.accepted, sentence)
            self.assertEqual(result.tree.leaves(), list(result.tokens))
            branches.update(node.label for node in result.tree.walk() if node.label.startswith("Q_"))
        self.assertEqual(len(branches), 26)
        self.assertLessEqual(max(branches.values()) - min(branches.values()), 1)

    def test_unknown_suffix_is_rejected(self) -> None:
        self.assertTrue(self.parser.parse("Tuần 3 học gì?").accepted)
        self.assertFalse(self.parser.parse("Tuần 3 học gì? xyz").accepted)

    def test_nullable_completion_and_left_recursion(self):
        grammar = Grammar.from_text('%start S\nS -> A A\nA -> | "x" A')
        parser = EarleyParser(grammar)
        self.assertTrue(parser.parse("").accepted)
        self.assertEqual(len(parser.parse_trees("x")), 2)
        left = EarleyParser(Grammar.from_text('%start S\nS -> S "x" | "x"'))
        self.assertTrue(left.parse("x x x").accepted)

    def test_ambiguity_and_nullable_cycles_are_bounded(self):
        parser = EarleyParser(Grammar.from_text('%start S\nS -> A | B\nA -> "x"\nB -> "x"'))
        self.assertEqual(len(parser.parse_trees("x")), 2)
        cyclic = EarleyParser(Grammar.from_text('%start S\nS -> S |'))
        self.assertEqual(len(cyclic.parse_trees("")), 2)

    def test_loader_rejects_undefined_symbols(self):
        with self.assertRaises(GrammarError):
            Grammar.from_text('%start S\nS -> UNDEFINED')


if __name__ == "__main__":
    unittest.main()
