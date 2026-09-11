# Course Assistant implementation template

This directory is a self-contained implementation skeleton derived from the
complete reference project on branch `sample` at `docs/sample-src/`. It mirrors
the reference project's code, data, input, output, tests, packaging, Docker, and
visual-documentation files. Assignment algorithms remain explicit
`NotImplementedError` tasks; data files contain schemas and TODO placeholders.

## Call flow

```text
question
  -> tokenizer.py
  -> grammar.py + parser.py
  -> tree.py
  -> entities.py + semantic.py
  -> dialogue.py (optional)
  -> query.py -> kb.py
  -> answer.py
  -> PipelineResult -> output.py / evaluate.py
```

## File map

| File | Responsibility |
| --- | --- |
| `tokenizer.py` | Normalize input into terminals shared by CFG and generator. |
| `grammar.py` | Load and validate the single CFG source of truth. |
| `parser.py` | Recognize complete sentences and build constituency trees. |
| `tree.py` | Stable parse-tree data contract. |
| `generator.py` | Safely generate bounded, diverse sentences from the CFG. |
| `entities.py` | Map aliases to canonical entity IDs. |
| `semantic.py` | Compose intent/entity/slots from labeled parse branches. |
| `dialogue.py` | Resolve typed local references between turns. |
| `kb.py` | Load, normalize, index, and validate supplied course facts. |
| `query.py` | Execute semantic frames without re-reading the raw question. |
| `answer.py` | Render grounded Vietnamese answer templates. |
| `pipeline.py` | Wire stages and expose every intermediate artifact. |
| `output.py` | Serialize assignment deliverables deterministically. |
| `evaluate.py` | Score official, challenge, and dialogue behavior by stage. |
| `paths.py` | Resolve all project locations independently of current cwd. |
| `cli.py` | Provide scriptable `ask`, `generate`, and `evaluate` commands. |
| `utils.py` | Preserve the original JSON-launcher compatibility hook. |

## Complete project tree

```text
src/
├── data/
│   ├── grammar.cfg              # valid seed CFG + every semantic Q_* branch
│   ├── kb/                      # six authoritative-data schemas
│   └── scaffolding/             # entities, tests, challenges, dialogues, FAQ
├── hcmut/iaslab/nlp/app/        # replaceable pipeline stages
├── input/sentences.txt          # batch-input template
├── models/README.md             # optional model policy
├── output/                      # all nine required deliverable placeholders
├── tests/                       # KB, parser/generator, and pipeline test skeletons
├── visually-explained-documentation.html
├── Dockerfile
├── pyproject.toml
├── setup.py
├── requirements.txt
└── run.py
```

The placeholder files are intentional: they show the required schema and output
format without copying the completed answers from the `sample` branch.

Every Python file starts with a module docstring describing its boundary,
invariants, and intended extension points. Read those docstrings before filling
in a TODO.

## Recommended implementation order

1. Implement `paths`, `tokenizer`, and the CFG loader.
2. Implement and test the parser/tree output against accepted and rejected text.
3. Implement entity canonicalization and semantic frames for every CFG branch.
4. Implement KB loading/validation, then query handlers and answer templates.
5. Assemble `CourseAssistant.from_paths`, then implement output and evaluation.
6. Add bounded generation and finally optional dialogue context.

Run a syntax/import check with `./util.sh check` (or the equivalent Python
commands on Windows). The CLI will intentionally fail at the first unimplemented
stage until that stage is completed.
