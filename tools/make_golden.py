"""Regenerate src/tests/golden/ from the frozen reference implementation.

The reference code on branch ``sample`` (``docs/sample-src``) is run against the
grammar and data in ``src/data`` and every stage boundary is recorded as JSON
lines.  ``src/tests/test_contract_*.py`` replay these records against the team's
implementation, so the hard contracts in ``docs/contracts.md`` are checked by
machine while each stage's internals stay free.

Run from the repository root after changing ``src/data/`` or the contracts:

    python tools/make_golden.py

Known reference bugs are corrected here, never in the tests: a result whose
answer is a fallback message must have ``found = False``.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import fields
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
GOLDEN = SRC / "tests" / "golden"
GENERATED_LIMIT = 2000         # sentences stored for tokenizer/parser/semantic
FRAME_SENTENCE_LIMIT = 10000   # sentences mined for distinct query/answer frames

# Normalization edge cases the tokenizer contract must cover explicitly.
EDGE_SENTENCES = [
    "",
    "   Tuần   3   học gì   ?",
    "TUẦN 3 HỌC GÌ?",
    "Tuần 3 học gì?!",
    "L.O.2.5 là gì?",
    "l.o.4.2 liên quan đến nội dung nào?",
    "Context-Free Grammar được học ở đâu?",
    "Có được dùng LLM/RAG không?",
    "Chương 3, chương 4 nói về gì?",
    "“NLP” có mấy tín chỉ?",
    "Hôm nay trời có mưa không?",
    "Cho mình hỏi deadline BTL là khi nào ạ?",
    # T18 extensions: explicit coverage independent of generator ordering.
    *[f"BTL có phần {feature} không?" for feature in (
        "parser", "grammar", "parse tree", "văn phạm", "phân tích cú pháp",
        "hỏi đáp", "semantic", "intent", "entity", "kb", "ngữ nghĩa",
        "ngữ cảnh", "hội thoại", "tham chiếu", "đánh giá", "test set", "metric", "kiểm thử",
    )],
    "Tài liệu nào về dịch máy?",
    "Có được dùng thư viện có sẵn không?",
]


def extend_reference() -> None:
    """Apply the documented T18 contract extensions to the frozen oracle only.

    Do not import the team's implementation here. The mapping follows §3:
    labeled feature groups determine the assignment section, preserving the
    surface feature string. Existing reference handlers remain unchanged.
    """
    from hcmut.iaslab.nlp.app import entities, semantic

    entities.RESOURCE_IDS["dịch máy"] = "MACHINE_TRANSLATION"
    entities.RULE_IDS["thư viện có sẵn"] = "EXTERNAL_LIBRARIES"

    def assignment_feature(self, branch):
        node = branch.first("ASSIGNMENT_FEATURE")
        phrase = self._phrase(node)
        labels = {"FEAT_PARSING": "PART_I", "FEAT_SEMANTIC": "PART_II",
                  "FEAT_CONTEXT": "PART_III", "FEAT_EVAL": "PART_IV"}
        part = next((labels[child.label] for child in node.walk() if child.label in labels), None)
        return semantic.SemanticFrame("GET_ASSIGNMENT", part,
                                      {"assignment": "BTL01", "section": part, "feature": phrase})

    semantic.SemanticInterpreter._handle_q_assignment_feature = assignment_feature


def extract_reference(target: Path) -> Path:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", "sample",
         "docs/sample-src/src", "docs/sample-src/pyproject.toml"],
        cwd=REPO, check=True, capture_output=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(target)
    project = target / "docs" / "sample-src"
    # paths.py discovers its root (pyproject.toml + data/) at import time.
    (project / "data").mkdir(exist_ok=True)
    return project / "src"


def plain(value: Any) -> Any:
    """JSON-normalize tuples, nested records and other containers."""
    return json.loads(json.dumps(value, ensure_ascii=False, default=list))


def tree_json(tree: Any) -> Any:
    if tree is None:
        return None
    return [tree.label, *(tree_json(c) if hasattr(c, "label") else c for c in tree.children)]


def frame_json(frame: Any) -> dict[str, Any]:
    return {
        "intent": frame.intent,
        "entity": frame.entity,
        "slots": plain(frame.slots),
        "source_branch": frame.source_branch,
    }


def result_json(result: Any) -> dict[str, Any]:
    return {
        "query": result.query,
        "found": result.found,
        "kind": result.kind,
        "data": plain(result.data),
        "sources": list(result.sources),
        "reason": getattr(result, "reason", None),
    }


def key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_jsonl(name: str, records: list[dict[str, Any]]) -> None:
    path = GOLDEN / name
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"  {name}: {len(records)} records")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        sys.path.insert(0, str(extract_reference(Path(tmp))))
        extend_reference()
        from hcmut.iaslab.nlp.app import answer as ref_answer
        from hcmut.iaslab.nlp.app.dialogue import DialogueContext
        from hcmut.iaslab.nlp.app.evaluate import (
            evaluate_cases, load_dialogue_cases, load_evaluation_cases,
        )
        from hcmut.iaslab.nlp.app.generator import SentenceGenerator
        from hcmut.iaslab.nlp.app.kb import KnowledgeBase
        from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
        from hcmut.iaslab.nlp.app.tokenizer import tokenize

        assistant = CourseAssistant.from_root(SRC)
        scaffolding = SRC / "data" / "scaffolding"
        cases = [
            (suite, case)
            for suite, name in (("official", "sample_queries.txt"), ("challenge", "challenge_queries.txt"))
            for case in load_evaluation_cases(scaffolding / name)
        ]
        dialogues = load_dialogue_cases(scaffolding / "dialogues.txt")
        generated, _ = SentenceGenerator(assistant.grammar).generate(limit=GENERATED_LIMIT)

        sentences = list(dict.fromkeys(
            EDGE_SENTENCES
            + [case.query for _, case in cases]
            + [q for d in dialogues for q in d.questions]
            + generated
        ))

        fallbacks = {
            ref_answer.NOT_FOUND: "NOT_FOUND",
            ref_answer.NOT_UNDERSTOOD: "NOT_UNDERSTOOD",
            ref_answer.MISSING_CONTEXT: "MISSING_CONTEXT",
        }

        def category(text: str) -> str:
            return fallbacks.get(text, "FOUND")

        corrected: list[str] = []

        def run_query(frame: Any) -> tuple[dict[str, Any], str, str]:
            result = assistant.query_engine.execute(frame)
            text = assistant.answer_generator.generate(frame, result)
            record = result_json(result)
            if record["found"] and category(text) != "FOUND":
                record["found"] = False
                record["reason"] = "reference bug corrected: answer is a fallback"
                corrected.append(frame.predicate)
            return record, text, category(text)

        tokens_out, parse_out = [], []
        semantic_out: dict[str, dict[str, Any]] = {}
        query_out: dict[str, dict[str, Any]] = {}

        def add_query(frame: Any, terms: tuple[str, ...] = ()) -> dict[str, Any]:
            fkey = key(frame_json(frame))
            if fkey not in query_out:
                result, text, cat = run_query(frame)
                query_out[fkey] = {
                    "frame": frame_json(frame), "result": result,
                    "category": cat, "reference_answer": text, "must_contain": [],
                }
            entry = query_out[fkey]
            entry["must_contain"] = sorted(set(entry["must_contain"]) | set(terms))
            return entry

        for sentence in sentences:
            tokens_out.append({"text": sentence, "tokens": tokenize(sentence)})
            parse = assistant.parser.parse(sentence)
            tree = tree_json(parse.tree)
            parse_out.append({"sentence": sentence, "tokens": list(parse.tokens), "tree": tree})
            tkey = key(tree)
            if tkey not in semantic_out:
                raw = assistant.interpreter.interpret(parse.tree)
                semantic_out[tkey] = {"tree": tree, "frame": frame_json(raw)}
                add_query(raw)

        # More sentences reach every entity value, including not-found ones,
        # while the query golden stays small because frames repeat.
        many, _ = SentenceGenerator(assistant.grammar).generate(limit=FRAME_SENTENCE_LIMIT)
        for sentence in many:
            add_query(assistant.interpreter.interpret(assistant.parser.parse(sentence).tree))

        # Like the graded evaluation, each suite starts from a fresh context and
        # runs in file order: some cases refer to the case just before them.
        case_out = []
        for suite in ("official", "challenge"):
            suite_cases = [case for name, case in cases if name == suite]
            for record in evaluate_cases(assistant, suite_cases, reset_context=True).records:
                case = record.case
                if record.correct:
                    add_query(record.result.semantic, case.expected_answer_terms)
                case_out.append({
                    "id": case.case_id, "suite": suite, "query": case.query,
                    "expected_intent": case.expected_intent, "expected_entity": case.expected_entity,
                    "expected_query_status": case.expected_query_status,
                    "expected_answer_terms": list(case.expected_answer_terms),
                    "reference_pass": record.correct,
                })

        dialogue_out = []
        for case in dialogues:
            context = DialogueContext()
            turns = []
            for question in case.questions:
                raw = assistant.interpreter.interpret(assistant.parser.parse(question).tree)
                resolved, _ = context.resolve(raw)
                entry = add_query(resolved)
                turns.append({
                    "sentence": question, "raw": frame_json(raw),
                    "resolved": frame_json(resolved), "result": entry["result"],
                })
                result = assistant.query_engine.execute(resolved)
                result.found = entry["result"]["found"]
                context.update(resolved, result)
            dialogue_out.append({
                "id": case.dialogue_id, "expected_reference": case.expected_reference, "turns": turns,
            })

        kb = KnowledgeBase.load(SRC / "data" / "kb")
        kb_out = {f.name: plain(getattr(kb, f.name)) for f in fields(kb) if f.name != "source_dir"}

        GOLDEN.mkdir(parents=True, exist_ok=True)
        print(f"golden → {GOLDEN.relative_to(REPO)}")
        write_jsonl("tokenizer.jsonl", tokens_out)
        write_jsonl("parser.jsonl", parse_out)
        write_jsonl("semantic.jsonl", list(semantic_out.values()))
        write_jsonl("query.jsonl", [{k: v[k] for k in ("frame", "result")} for v in query_out.values()])
        write_jsonl("answer.jsonl", [
            {k: v[k] for k in ("frame", "result", "category", "must_contain", "reference_answer")}
            for v in query_out.values()
        ])
        write_jsonl("dialogue.jsonl", dialogue_out)
        write_jsonl("cases.jsonl", case_out)
        (GOLDEN / "kb.json").write_text(
            json.dumps(kb_out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
        print("  kb.json")
        if corrected:
            print(f"corrected {len(corrected)} reference results (found → False):")
            for predicate in sorted(set(corrected)):
                print(f"   {predicate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
