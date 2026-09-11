# Data templates

This directory mirrors every data input used by the complete sample while
containing only schemas, representative placeholders, and TODO guidance.

- `grammar.cfg`: one syntactic source of truth for parser and generator.
- `kb/`: course facts; replace placeholders with authoritative supplied data.
- `scaffolding/entities.txt`: aliases mapped to stable canonical IDs.
- `scaffolding/sample_queries.txt`: official/regression evaluation cases.
- `scaffolding/challenge_queries.txt`: author-created edge cases.
- `scaffolding/dialogues.txt`: ordered multi-turn context cases.
- `scaffolding/faq.txt`: optional examples for manual comparison, never the
  primary query engine.

Keep grammar, semantics, canonical IDs, and KB indexes synchronized. Do not put
course facts into the grammar and do not parse raw user text inside the KB.
