"""Print a reproducible demo from real pipeline results, including failures."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hcmut.iaslab.nlp.app.paths import PATHS
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant

FOLLOW_UP = "Nó có liên quan đến parsing không?"
SCENES = {
    "credits": ("Môn NLP có bao nhiêu tín chỉ?",),
    "dialogue": ("Tuần 3 học gì?", FOLLOW_UP),
    "missing-context": (FOLLOW_UP,),
    "missing-kb": ("Ai dạy NLP?",),
    "out-of-scope": ("Hôm nay trời có mưa không?",),
    "grammar-gap": ("Tuần thứ ba tụi mình học bài gì vậy?",),
}

# The automatic video uses this original sequence for its captions and timings.
QUESTIONS = (
    *SCENES["credits"],
    *SCENES["dialogue"],
    "BTL có phần parse tree không?",
    "Có được dùng thư viện có sẵn không?",
    *SCENES["missing-kb"],
    *SCENES["out-of-scope"],
)


def transcript(questions: tuple[str, ...] = QUESTIONS) -> str:
    assistant = CourseAssistant.from_paths(PATHS)
    lines = ["COURSE ASSISTANT | DEMO THỰC THI", ""]
    for number, question in enumerate(questions, 1):
        result = assistant.process(question)
        lines.extend([f"[{number}] INPUT: {question}",
                      f"TOKENS: {' / '.join(result.parse.tokens)}",
                      f"PARSE: {result.parse.output()}",
                      f"SEMANTIC: {result.raw_semantic.predicate}"])
        if result.context_used:
            lines.append(f"CONTEXT: {result.context_used}")
            lines.append(f"RESOLVED: {result.semantic.predicate}")
        status = "FOUND" if result.query.found else "NOT_FOUND"
        if result.query.query == "NO_QUERY":
            status = "SKIPPED"
        lines.extend([f"QUERY: {result.query.query}",
                      f"STATUS: {status}",
                      f"SOURCE: {', '.join(result.query.sources) or '-'}",
                      f"ANSWER: {result.answer}", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", nargs="?", choices=SCENES,
                        help="run one recording scene with fresh dialogue context")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    print(transcript(SCENES[args.scene] if args.scene else QUESTIONS))
