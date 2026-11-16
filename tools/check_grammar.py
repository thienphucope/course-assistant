"""Check CFG structure, regression cases, ambiguity and generated QA traces.

Run from any directory: python tools/check_grammar.py --samples 1000.
Missing KB facts and isolated context references are reported, not treated as
grammar failures. --strict-kb additionally requires every generated query to
find data (intentionally unsuitable for the supplied negative examples).
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from hcmut.iaslab.nlp.app.answer import NOT_FOUND, NOT_UNDERSTOOD, MISSING_CONTEXT
from hcmut.iaslab.nlp.app.evaluate import evaluate_cases, load_evaluation_cases, load_dialogue_cases
from hcmut.iaslab.nlp.app.generator import SentenceGenerator
from hcmut.iaslab.nlp.app.grammar import Grammar, GrammarError
from hcmut.iaslab.nlp.app.parser import EarleyParser
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
from hcmut.iaslab.nlp.app.semantic import BRANCH_INTENTS
from hcmut.iaslab.nlp.app.tokenizer import tokenize


def structural_errors(grammar: Grammar) -> list[str]:
    errors = []
    definitions = Counter()
    for number, raw in enumerate(grammar.source_text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith(("#", "%")):
            continue
        lhs = raw.split("->", 1)[0].strip()
        definitions[lhs] += 1
        for literal in re.findall(r'"(?:[^"\\]|\\.)*"', raw):
            terminal = json.loads(literal)
            if terminal != terminal.lower():
                errors.append(f"line {number}: uppercase terminal {terminal!r}")
            if tokenize(terminal) != [terminal]:
                errors.append(f"line {number}: terminal/tokenizer mismatch {terminal!r}")
    errors.extend(f"duplicate definition: {lhs}" for lhs, count in definitions.items() if count > 1)
    duplicate_rules = [rule.display() for rule, count in Counter(grammar.rules).items() if count > 1]
    errors.extend(f"duplicate rule: {rule}" for rule in duplicate_rules)
    reachable = {grammar.start}
    pending = [grammar.start]
    while pending:
        for rule in grammar.rules_for(pending.pop()):
            for symbol in rule.rhs:
                if grammar.is_nonterminal(symbol) and symbol not in reachable:
                    reachable.add(symbol)
                    pending.append(symbol)
    errors.extend(f"unreachable non-terminal: {nt}" for nt in sorted(grammar.nonterminals - reachable))
    branches = [rule.rhs[0] for rule in grammar.rules_for("QUESTION") if len(rule.rhs) == 1]
    if len(branches) != 26 or set(branches) != set(BRANCH_INTENTS):
        errors.append("QUESTION must contain exactly the 26 supported Q_* branches")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / "src")
    parser.add_argument("--grammar", type=Path)
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--strict-kb", action="store_true")
    parser.add_argument("--json", type=Path, help="write machine-readable results")
    args = parser.parse_args(argv)
    if not 26 <= args.samples <= 10000:
        parser.error("--samples must be between 26 and 10000 for branch coverage")
    root = args.root.resolve()
    errors = []
    try:
        grammar = Grammar.from_file(args.grammar or root / "data/grammar.cfg")
        errors.extend(structural_errors(grammar))
    except (GrammarError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if errors:
        print("\n".join(f"FAIL: {error}" for error in errors))
        return 1
    assistant = CourseAssistant.from_root(root)
    assistant.components = replace(assistant.components, parser=EarleyParser(grammar))
    report = {"rules": len(grammar.rules), "branches": 26, "suites": {}}
    ambiguity = []
    checked = set()

    def check_ambiguity(question):
        if question not in checked:
            checked.add(question)
            if len(assistant.parser.parse_trees(question, limit=2)) > 1:
                ambiguity.append(question)

    for suite, filename in (("official", "sample_queries.txt"), ("challenge", "challenge_queries.txt")):
        cases = load_evaluation_cases(root / "data/scaffolding" / filename)
        summary = evaluate_cases(assistant, cases)
        failures = []
        for record in summary.records:
            check_ambiguity(record.case.query)
            if not record.correct:
                failures.append({"id": record.case.case_id, "question": record.case.query,
                                 "branch": record.result.raw_semantic.source_branch,
                                 "reason": record.diagnosis})
        report["suites"][suite] = {"passed": summary.joint_correct, "total": summary.total, "failures": failures}
        # Challenges are an error-analysis set, not a promise of grammar coverage.
        if suite == "official" and failures:
            errors.append(f"official regressions: {len(failures)}")
    dialogues = load_dialogue_cases(root / "data/scaffolding/dialogues.txt")
    dialogue_passed = 0
    for case in dialogues:
        assistant.reset_context()
        for question in case.questions:
            check_ambiguity(question)
            result = assistant.process(question)
        expected = case.expected_reference.replace("PART_I_GRAMMAR_PARSER", "PART_I")
        if result.detected_entity == expected and result.query.found:
            dialogue_passed += 1
        else:
            errors.append(f"dialogue {case.dialogue_id}: expected {expected}, got {result.detected_entity}")
    report["dialogues"] = {"passed": dialogue_passed, "total": len(dialogues)}

    samples, stats = SentenceGenerator(grammar).generate(args.samples)
    branches = Counter()
    statuses = Counter()
    missing = []
    for question in samples:
        check_ambiguity(question)
        assistant.reset_context()
        result = assistant.process(question)
        frame = result.raw_semantic
        branches[frame.source_branch or "UNKNOWN"] += 1
        if not result.parse.accepted or frame.intent == "UNKNOWN":
            errors.append(f"generated sentence rejected/UNKNOWN: {question}")
        if frame.entity is None and frame.intent != "CONTEXT_DEPENDENT":
            errors.append(f"generated sentence has unresolved entity: {question}")
        status = "FOUND" if result.query.found else result.query.kind
        statuses[status] += 1
        fallback = result.answer in {NOT_FOUND, NOT_UNDERSTOOD, MISSING_CONTEXT}
        if result.query.found == fallback:
            errors.append(f"found/fallback contradiction: {question}")
        if not result.query.found:
            missing.append({"question": question, "branch": frame.source_branch,
                            "kind": result.query.kind, "reason": result.query.reason})
            if args.strict_kb:
                errors.append(f"generated query not found: {question}")
    if set(branches) != set(BRANCH_INTENTS):
        errors.append(f"generated branch coverage incomplete: {len(branches)}/26")
    if not 0 < len(samples) <= args.samples:
        errors.append(f"generator count outside requested bound: {len(samples)}/{args.samples}")
    if ambiguity:
        errors.append(f"ambiguous sentences (at least 2 trees): {len(ambiguity)}")
    report.update({"generated": stats.__dict__, "coverage": dict(sorted(branches.items())),
                   "query_statuses": dict(statuses), "missing_facts_or_context": missing,
                   "ambiguity_checked": len(checked), "ambiguous": ambiguity, "errors": errors})
    for suite, result in report["suites"].items():
        print(f"{suite}: {result['passed']}/{result['total']}")
        for failure in result["failures"]:
            print(f"  {failure['id']} [{failure['branch'] or 'no branch'}]: {failure['question']} | {failure['reason']}")
    print(f"dialogues: {dialogue_passed}/{len(dialogues)}")
    print(f"generated: {len(samples)}/{args.samples}; branches: {len(branches)}/26")
    print(f"ambiguity: {len(ambiguity)}/{len(checked)} checked sentences (bounded at 2 trees)")
    print(f"generated query statuses: {dict(statuses)}")
    print("Missing facts/context remain explicit fallbacks; see --json for individual traces.")
    for error in errors:
        print(f"FAIL: {error}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FAIL" if errors else "PASS")
    return int(bool(errors))


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
