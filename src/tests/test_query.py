"""T12/T13 integration: execute frames against the real loaded text KB."""

import unittest
from copy import deepcopy

from hcmut.iaslab.nlp.app.kb import KnowledgeBase
from hcmut.iaslab.nlp.app.query import QueryEngine
from hcmut.iaslab.nlp.app.semantic import SemanticFrame
from tests.contract_support import DATA, frame, load, plain


class QueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBase.load(DATA / "kb")

    def test_all_golden_frames_against_real_loaded_kb(self):
        engine = QueryEngine(self.kb)
        before = deepcopy(self.kb)
        for record in load("query.jsonl"):
            with self.subTest(frame=record["frame"]):
                actual = engine.execute(frame(record["frame"]))
                expected = record["result"]
                self.assertEqual(actual.found, expected["found"])
                self.assertEqual(actual.kind, expected["kind"])
                self.assertEqual(actual.sources, expected["sources"])
                if expected["found"]:
                    self.assertEqual(plain(actual.data), expected["data"])
        self.assertEqual(self.kb, before, "Queries must not mutate the KB")

    def test_missing_week_is_not_found(self):
        result = QueryEngine(self.kb).execute(
            SemanticFrame("GET_SCHEDULE", "WEEK_99", {"week": "WEEK_99"})
        )
        self.assertFalse(result.found)
        self.assertEqual(result.kind, "SCHEDULE_WEEK")
        self.assertEqual(result.sources, [])

    def test_existing_section_without_outputs_is_not_found(self):
        result = QueryEngine(self.kb).execute(SemanticFrame(
            "GET_ASSIGNMENT", "PART_II",
            {"assignment": "BTL01", "section": "PART_II", "field": "OUTPUTS"},
        ))
        self.assertFalse(result.found)
        self.assertEqual(result.kind, "ASSIGNMENT_SECTION")
        self.assertEqual(result.sources, ["kb/assignments.txt"])

    def test_unresolved_context_is_not_answered(self):
        result = QueryEngine(self.kb).execute(SemanticFrame("CONTEXT_DEPENDENT"))
        self.assertFalse(result.found)
        self.assertEqual(result.kind, "UNRESOLVED_CONTEXT")

    def test_negative_relation_is_still_a_found_fact(self):
        result = QueryEngine(self.kb).execute(SemanticFrame(
            "GET_TOPIC", "CH01", {"chapter": "CH01", "relation": "PCFG"},
        ))
        self.assertTrue(result.found)
        self.assertFalse(result.data["related"])


if __name__ == "__main__":
    unittest.main()
