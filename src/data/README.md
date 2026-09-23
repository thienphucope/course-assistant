# Runtime data for the Course Assistant

This is the data directory used when `src/` is the project root. The six `kb/`
files, `sample_queries.txt`, `dialogues.txt`, and `faq.txt` were copied from the
supplied sample dataset in the repository's top-level `data/` directory. That
top-level directory remains an unchanged reference; update this runtime copy
when adding facts or tests. See `00_README.txt` for provenance and the warning
that the schedule, assignment milestones, and policies are sample data.

- `grammar.cfg`: the team's CFG, shared by parser and generator; it covers all
  seven required question groups and the current regression suite.
- `kb/`: course facts used for runtime lookup, not evaluation questions.
- `scaffolding/entities_reference.txt`: unmodified descriptive source lexicon.
- `scaffolding/entities.txt`: derived aliases mapped to canonical IDs, with
  separate entity families for course parts and assignment parts.
- `scaffolding/sample_queries.txt`: 34 supplied sample questions. Four columns
  are required; query status and answer terms may be added as optional columns.
- `scaffolding/challenge_queries.txt`: team-authored edge cases.
- `scaffolding/dialogues.txt`: ordered multi-turn examples for optional context;
  one assignment-part reference is normalized from `PART_I_GRAMMAR_PARSER` to
  the canonical `PART_I` used by `sample_queries.txt`.
- `scaffolding/faq.txt`: optional examples, not the primary query engine.

Keep grammar, semantic IDs, and KB indexes synchronized. Do not put course
facts into the grammar or parse raw user text inside the KB.
