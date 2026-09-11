"""Template tests for KB loading, schema validation, and reverse indexes.

Replace skipped cases as each loader is implemented. Test counts, canonical
keys, multiline fields, optional values, malformed records, and all cross-file
references rather than checking only one happy-path fact.
"""

import unittest

from hcmut.iaslab.nlp.app.kb import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    def test_loader_preserves_all_source_records(self) -> None:
        self.skipTest("TODO: load the template fixture and assert record counts")

    def test_validation_reports_all_broken_references(self) -> None:
        self.skipTest("TODO: construct an invalid KnowledgeBase and assert errors")

    def test_empty_contract_is_explicit(self) -> None:
        kb = KnowledgeBase()
        self.assertEqual(kb.course, {})
        self.assertEqual(kb.resources, ())


if __name__ == "__main__":
    unittest.main()
