"""Print a reproducible demo from real pipeline results, including failures."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant

QUESTIONS = (
    "Môn NLP có bao nhiêu tín chỉ?",
    "Tuần 3 học gì?",
    "Nó có liên quan đến parsing không?",
    "BTL có phần parse tree không?",
    "Có được dùng thư viện có sẵn không?",
    "Ai dạy NLP?",
    "Hôm nay trời có mưa không?",
)


def transcript() -> str:
    assistant = CourseAssistant.from_root(Path(__file__).resolve().parents[1] / "src")
    lines = ["COURSE ASSISTANT | DEMO THỰC THI", ""]
    for number, question in enumerate(QUESTIONS, 1):
        result = assistant.process(question)
        lines.extend([f"[{number}] INPUT: {question}",
                      f"TOKENS: {' / '.join(result.parse.tokens)}",
                      f"PARSE: {result.parse.output()}",
                      f"SEMANTIC: {result.raw_semantic.predicate}"])
        if result.context_used:
            lines.append(f"CONTEXT: {result.context_used}")
            lines.append(f"RESOLVED: {result.semantic.predicate}")
        lines.extend([f"QUERY: {result.query.query}",
                      f"STATUS: {'FOUND' if result.query.found else 'NOT_FOUND'}",
                      f"SOURCE: {', '.join(result.query.sources) or '-'}",
                      f"ANSWER: {result.answer}", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(transcript())
