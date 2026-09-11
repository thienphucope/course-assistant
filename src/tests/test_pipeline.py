"""Template tests for semantics, context, query, answer, and full orchestration.

Assert each intermediate artifact in ``PipelineResult`` so failures identify the
responsible stage. Add one case for every intent, explicit missing-KB behavior,
out-of-domain behavior, and ordered dialogue fixtures with reset boundaries.
"""

import unittest

from hcmut.iaslab.nlp.app.parser import ParseResult
from hcmut.iaslab.nlp.app.pipeline import PipelineResult
from hcmut.iaslab.nlp.app.query import QueryResult
from hcmut.iaslab.nlp.app.semantic import SemanticFrame


class PipelineTests(unittest.TestCase):
    def test_pipeline_result_exposes_semantic_contract(self) -> None:
        raw = SemanticFrame("GET_SCHEDULE", "WEEK_03", {"week": "WEEK_03"})
        result = PipelineResult(
            sentence="TODO",
            parse=ParseResult("TODO", ("todo",), None),
            raw_semantic=raw,
            semantic=raw,
            query=QueryResult("KB.weeks[WEEK_03]", False, "SCHEDULE_WEEK"),
            answer="TODO",
        )
        self.assertEqual(result.detected_intent, "GET_SCHEDULE")
        self.assertEqual(result.detected_entity, "WEEK_03")

    def test_all_intents_are_grounded_end_to_end(self) -> None:
        self.skipTest("TODO: implement stages and load sample_queries.txt")

    def test_dialogue_state_is_scoped_and_resettable(self) -> None:
        self.skipTest("TODO: implement and evaluate typed context resolution")


if __name__ == "__main__":
    unittest.main()
