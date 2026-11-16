"""Template tests for semantics, context, query, answer, and full orchestration.

Assert each intermediate artifact in ``PipelineResult`` so failures identify the
responsible stage. Add one case for every intent, explicit missing-KB behavior,
out-of-domain behavior, and ordered dialogue fixtures with reset boundaries.
"""

import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
from hcmut.iaslab.nlp.app.evaluate import evaluate_cases, load_evaluation_cases
from hcmut.iaslab.nlp.app.answer import MISSING_CONTEXT, NOT_FOUND
from hcmut.iaslab.nlp.app.parser import ParseResult
from hcmut.iaslab.nlp.app.pipeline import PipelineResult
from hcmut.iaslab.nlp.app.query import QueryResult
from hcmut.iaslab.nlp.app.semantic import SemanticFrame


class PipelineTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

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
        assistant = CourseAssistant.from_root(self.root)
        cases = load_evaluation_cases(self.root / "data/scaffolding/sample_queries.txt")
        summary = evaluate_cases(assistant, cases)
        self.assertEqual(summary.joint_correct, len(cases),
                         [r.case.case_id for r in summary.records if not r.correct])

    def test_dialogue_state_is_scoped_and_resettable(self) -> None:
        assistant = CourseAssistant.from_root(self.root)
        assistant.process("Chương 3 nói về gì?")
        assistant.process("BTL phần I yêu cầu gì?")
        result = assistant.process("Nó có liên quan đến parsing không?")
        self.assertEqual(result.semantic.entity, "CH03")
        assistant.process("Tuần 99 học gì?")
        self.assertEqual(assistant.components.context.last_chapter, "CH03")
        assistant.reset_context()
        self.assertEqual(assistant.process("Nó có liên quan đến parsing không?").answer, MISSING_CONTEXT)

    def test_feature_labels_and_new_aliases(self):
        assistant = CourseAssistant.from_root(self.root)
        for feature, part in [("grammar", "PART_I"), ("parse tree", "PART_I"),
                              ("intent", "PART_II"), ("entity", "PART_II"), ("kb", "PART_II"),
                              ("hội thoại", "PART_III"), ("test set", "PART_IV"), ("metric", "PART_IV")]:
            with self.subTest(feature=feature):
                result = assistant.process(f"BTL có phần {feature} không?")
                self.assertEqual(result.semantic.entity, part)
                self.assertEqual(result.semantic.slots["feature"], feature)
                self.assertTrue(result.query.found)
        for question, entity in [("Tài liệu nào về dịch máy?", "MACHINE_TRANSLATION"),
                                 ("Có được dùng thư viện có sẵn không?", "EXTERNAL_LIBRARIES")]:
            result = assistant.process(question)
            self.assertEqual(result.semantic.entity, entity)
            self.assertTrue(result.query.found)

    def test_missing_facts_use_fallback(self):
        assistant = CourseAssistant.from_root(self.root)
        for question in ("Ai dạy NLP?", "Khi nào thi final?", "Phần II có output gì?"):
            result = assistant.process(question)
            self.assertTrue(result.parse.accepted, question)
            self.assertFalse(result.query.found)
            self.assertEqual(result.answer, NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
