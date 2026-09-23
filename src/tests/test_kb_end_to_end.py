"""Ground answers in the six supplied KB files across all required groups."""

import shutil
import tempfile
import unittest
from pathlib import Path

from hcmut.iaslab.nlp.app.kb import KnowledgeBase
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant


ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "kb"


class GroundedQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assistant = CourseAssistant.from_root(ROOT)

    def test_all_25_core_questions_have_sourced_answers(self) -> None:
        expected_terms = {
            "Q001": ("3 tín chỉ",), "Q002": ("3 tín chỉ",),
            "Q003": ("Part I", "Part II", "Part III"),
            "Q004": ("Tuần 3", "Chương 3", "context-free grammar"),
            "Q005": ("tuần 4", "tuần 5"),
            "Q006": ("Chương 3",),
            "Q007": ("Chương 3", "Chương 6", "tuần 3", "tuần 7"),
            "Q008": ("Chương 10",),
            "Q009": ("LO2.5", "xác suất"),
            "Q010": ("LO4.2", "Ngữ cảnh"),
            "Q011": ("question answering",),
            "Q012": ("PART I", "Grammar and Parser"),
            "Q013": ("Có.", "PART II", "QA"),
            "Q014": ("LLM/RAG", "mở rộng"),
            "Q015": ("sử dụng AI", "khai báo"),
            "Q016": ("MIDTERM", "60 minutes"),
            "Q017": ("FINAL", "90 minutes"),
            "Q018": ("Jacob Eisenstein", "Christopher D. Manning"),
            "Q019": ("Natural Language Processing with Python",),
            "Q020": ("Chương 12", "discourse context"),
            "Q021": ("Chương 12",),
            "Q022": ("Chương 11",),
            "Q023": ("Chương 9",),
            "Q024": ("Chương 10", "Template matching"),
            "Q025": ("Có.", "11.5", "question answering"),
        }
        fixture = (ROOT / "data" / "scaffolding" / "sample_queries.txt").read_text(
            encoding="utf-8-sig"
        )
        observed = set()
        for line in fixture.splitlines():
            case_id = line.split("|", 1)[0].strip()
            if case_id not in expected_terms:
                continue
            question = line.split("|")[1].strip()
            with self.subTest(case=case_id):
                result = self.assistant.process(question, use_context=False)
                self.assertTrue(result.parse.accepted)
                self.assertTrue(result.query.found, result.query.reason)
                self.assertTrue(result.query.sources)
                self.assertNotIn("Xin lỗi", result.answer)
                for term in expected_terms[case_id]:
                    self.assertIn(term.casefold(), result.answer.casefold())
            observed.add(case_id)
        self.assertEqual(observed, set(expected_terms))

    def test_multirecord_lookups_preserve_all_matching_sources(self) -> None:
        chapter = self.assistant.process("Chương 4 học vào tuần nào?", use_context=False)
        self.assertEqual(chapter.query.sources,
                         ["schedule.txt:WEEK 04", "schedule.txt:WEEK 05"])
        pcfg = self.assistant.process("PCFG được học ở đâu?", use_context=False)
        self.assertEqual(pcfg.query.sources,
                         ["topics.txt:CH03", "topics.txt:CH06",
                          "schedule.txt:WEEK 03", "schedule.txt:WEEK 07"])
        resources = self.assistant.process(
            "Tài liệu tham khảo về statistical NLP là gì?", use_context=False
        )
        self.assertEqual(resources.query.sources,
                         ["resources.txt:TEXTBOOK_2", "resources.txt:REFERENCE_1"])

    def test_missing_fact_and_out_of_scope_are_distinct(self) -> None:
        deadline = self.assistant.process("Deadline của bài tập lớn là khi nào?",
                                          use_context=False)
        self.assertEqual((deadline.semantic.intent, deadline.query.kind,
                          deadline.query.found), ("GET_DEADLINE", "DEADLINE", False))
        self.assertEqual(deadline.query.status, "NOT_FOUND")
        self.assertIn("không tìm thấy ngày nộp cụ thể", deadline.answer)
        self.assertEqual(deadline.query.sources, [])

        instructor = self.assistant.process("Ai dạy môn NLP?", use_context=False)
        self.assertEqual(instructor.semantic.intent, "GET_COURSE_INFO")
        self.assertFalse(instructor.query.found)
        self.assertIn("không tìm thấy", instructor.answer)

        exam_time = self.assistant.process("Midterm thi khi nào?", use_context=False)
        self.assertEqual(exam_time.query.kind, "EXAM_TIME")
        self.assertFalse(exam_time.query.found)

        outside = self.assistant.process("Hôm nay ở TP.HCM có mưa không?",
                                         use_context=False)
        self.assertEqual(outside.query.kind, "OUT_OF_SCOPE")
        self.assertEqual(outside.query.status, "OUT_OF_SCOPE")
        self.assertNotEqual(outside.answer, deadline.answer)


class CompleteKnowledgeBaseTests(unittest.TestCase):
    def test_all_six_collections_are_loaded_with_multiline_content(self) -> None:
        kb = KnowledgeBase.load(KB_DIR)
        self.assertEqual(kb.course["credits"], 3)
        self.assertIn("ngữ cảnh diễn ngôn", kb.course["detailed_learning_outcomes"]["LO4.2"].casefold())
        self.assertEqual(len(kb.weeks), 15)
        self.assertEqual(len(kb.topics), 12)
        self.assertIn("probabilistic CFG", kb.topics["CH03"]["summary"])
        self.assertEqual(len(kb.assignment["parts"]), 4)
        self.assertIn("QA", kb.assignment["parts"]["PART_II"]["title"])
        self.assertEqual(len(kb.resources), 8)
        self.assertIn("giáo trình", kb.resource_note)
        self.assertIn("khai báo", kb.regulations["AI_USAGE"])
        self.assertEqual(kb.validate(), [])

    def test_malformed_or_duplicate_source_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kb"
            shutil.copytree(KB_DIR, target)
            course = target / "course_info.txt"
            course.write_text(course.read_text(encoding="utf-8").replace("credits: 3", "credits: unknown"),
                              encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "credits must be an integer"):
                KnowledgeBase.load(target)

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kb"
            shutil.copytree(KB_DIR, target)
            resources = target / "resources.txt"
            resources.write_text(resources.read_text(encoding="utf-8")
                                 + "\nREFERENCE 1\ntitle: duplicate\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate REFERENCE_1"):
                KnowledgeBase.load(target)


if __name__ == "__main__":
    unittest.main()
