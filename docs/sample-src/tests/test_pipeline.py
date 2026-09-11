from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hcmut.iaslab.nlp.app.answer import NOT_FOUND, NOT_UNDERSTOOD
from hcmut.iaslab.nlp.app.evaluate import EvaluationCase, evaluate_cases, load_evaluation_cases
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = CourseAssistant.from_root(ROOT)

    def test_supplied_evaluation_set_is_fully_covered(self) -> None:
        cases = load_evaluation_cases(ROOT / "data" / "scaffolding" / "sample_queries.txt")
        summary = evaluate_cases(self.assistant, cases)
        self.assertEqual(summary.total, 42)
        self.assertEqual(summary.intent_correct, 42)
        self.assertEqual(summary.entity_correct, 42)
        self.assertEqual(summary.query_correct, 42)
        self.assertEqual(summary.answer_correct, 42)
        self.assertEqual(summary.joint_correct, 42)

    def test_semantic_predicate_and_grounded_answer(self) -> None:
        result = self.assistant.process("Môn NLP có bao nhiêu tín chỉ?")
        self.assertEqual(result.raw_semantic.intent, "GET_COURSE_INFO")
        self.assertEqual(result.raw_semantic.entity, "CO3085")
        self.assertIn("field=CREDITS", result.raw_semantic.predicate)
        self.assertEqual(result.answer, "Môn Xử lý Ngôn ngữ Tự nhiên (CO3085) có 3 tín chỉ.")
        self.assertEqual(result.query.sources, ["kb/course_info.txt"])

    def test_grammar_valid_but_kb_missing(self) -> None:
        result = self.assistant.process("Tuần 99 học gì?")
        self.assertTrue(result.parse.accepted)
        self.assertEqual(result.detected_entity, "WEEK_99")
        self.assertFalse(result.query.found)
        self.assertEqual(result.answer, NOT_FOUND)

    def test_known_intent_with_missing_kb_field(self) -> None:
        result = self.assistant.process("Giáo viên môn NLP là ai?")
        self.assertTrue(result.parse.accepted)
        self.assertEqual(result.detected_intent, "GET_INSTRUCTOR")
        self.assertFalse(result.query.found)
        self.assertEqual(result.answer, NOT_FOUND)

    def test_out_of_scope_does_not_query_kb(self) -> None:
        result = self.assistant.process("Ai là tổng thống của Pháp?")
        self.assertEqual(result.detected_intent, "UNKNOWN")
        self.assertEqual(result.query.query, "NO_QUERY")
        self.assertEqual(result.answer, NOT_UNDERSTOOD)

    def test_local_dialogue_context(self) -> None:
        first = self.assistant.process("Chương 11 có hỏi đáp không?")
        second = self.assistant.process("Còn chương sau?")
        self.assertEqual(first.detected_entity, "CH11")
        self.assertEqual(second.raw_semantic.intent, "CONTEXT_DEPENDENT")
        self.assertEqual(second.semantic.intent, "GET_TOPIC")
        self.assertEqual(second.detected_entity, "CH12")
        self.assertIn("CH11", second.context_used)

    def test_literal_pdf_examples_are_supported(self) -> None:
        cases = [
            ("Môn NLP có bao nhiêu tín chỉ?", "GET_COURSE_INFO", "CO3085", True, "3 tín chỉ"),
            ("Tuần 5 học những nội dung gì?", "GET_SCHEDULE", "WEEK_05", True, "Tuần 5"),
            ("Phần CFG và Parsing nằm ở tuần nào?", "GET_SCHEDULE", "CFG", True, "tuần 3"),
            ("Bài tập lớn có những yêu cầu gì?", "GET_ASSIGNMENT", "BTL01", True, "Intelligent Course Assistant"),
            ("Deadline của bài tập lớn là khi nào?", "GET_DEADLINE", "BTL01", True, "tuần 15"),
            ("Tài liệu nào nói về CFG?", "GET_RESOURCE", "CFG", True, "Tài liệu phù hợp"),
            ("Bài tập lớn có được sử dụng công cụ AI không?", "GET_RULE", "AI_USAGE", True, "AI"),
            ("Tôi cần hoàn thành những bài tập nào?", "GET_ASSIGNMENT", "BTL01", True, "Các phần gồm"),
        ]
        for question, intent, entity, found, answer_term in cases:
            with self.subTest(question=question):
                result = self.assistant.process(question)
                self.assertTrue(result.parse.accepted)
                self.assertEqual(result.detected_intent, intent)
                self.assertEqual(result.detected_entity, entity)
                self.assertEqual(result.query.found, found)
                self.assertIn(answer_term, result.answer)

    def test_challenge_paraphrases_have_safe_semantics(self) -> None:
        credits = self.assistant.process("Môn này nặng mấy tín?")
        self.assertEqual((credits.detected_intent, credits.detected_entity), ("GET_COURSE_INFO", "CO3085"))
        self.assertTrue(credits.query.found)
        self.assertIn("3 tín chỉ", credits.answer)

        exam_time = self.assistant.process("Khi nào tụi mình thi giữa kỳ?")
        self.assertEqual((exam_time.detected_intent, exam_time.detected_entity), ("GET_COURSE_INFO", "MIDTERM"))
        self.assertFalse(exam_time.query.found)
        self.assertEqual(exam_time.answer, NOT_FOUND)

    def test_literal_pdf_dialogue_uses_previous_week(self) -> None:
        first = self.assistant.process("Tuần 5 học những gì?")
        second = self.assistant.process("Tài liệu của phần này ở đâu?")
        self.assertTrue(first.query.found)
        self.assertEqual(first.detected_entity, "WEEK_05")
        self.assertEqual(second.raw_semantic.intent, "CONTEXT_DEPENDENT")
        self.assertEqual(second.semantic.intent, "GET_RESOURCE")
        self.assertEqual(second.detected_entity, "CH04")
        self.assertTrue(second.query.found)
        self.assertIn("CH04", second.context_used)

    def test_evaluation_checks_query_status_and_answer_facts(self) -> None:
        case = EvaluationCase(
            "T001",
            "Môn NLP có bao nhiêu tín chỉ?",
            "GET_COURSE_INFO",
            "CO3085",
            "FOUND",
            ("999 tín chỉ",),
        )
        record = evaluate_cases(self.assistant, [case]).records[0]
        self.assertTrue(record.intent_correct)
        self.assertTrue(record.entity_correct)
        self.assertTrue(record.query_correct)
        self.assertFalse(record.answer_correct)
        self.assertFalse(record.correct)


if __name__ == "__main__":
    unittest.main()
