"""Template tests for tokenizer, CFG parser, tree, and bounded generation.

Every accepted grammar branch needs a positive test; near misses and trailing
unknown tokens need rejection tests. Generated sentences should round-trip
through the parser and generation must respect uniqueness and safety bounds.
"""

import unittest

from hcmut.iaslab.nlp.app.tree import Tree


class ParserGeneratorTests(unittest.TestCase):
    def test_tree_contract(self) -> None:
        tree = Tree("S", (Tree("TOKEN", ("hello",)),))
        self.assertEqual(tree.leaves(), ["hello"])
        self.assertEqual(tree.bracketed(), "(S (TOKEN hello))")

    def test_valid_question_round_trips(self) -> None:
        self.skipTest("TODO: implement tokenizer, grammar loader, parser, and generator")

    def test_unknown_suffix_is_rejected(self) -> None:
        self.skipTest("TODO: assert that parsing spans every input token")


if __name__ == "__main__":
    unittest.main()
