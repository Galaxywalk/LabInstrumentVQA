# Literature Data

This directory contains the legal metadata-only literature workspace.

Curated source files:

- `paper_metadata.schema.json`: JSON schema for one paper metadata record.
- `source_rules.yaml`: source priority, legal OA policy, relevance keywords, and deduplication rules.
- `seed_queries.yaml`: ISSCC/JSSC query templates for 2006-2026.
- `papers.seed.jsonl`: starter placeholders for long-running metadata expansion.

Generated files such as `papers.raw.jsonl`, `papers.dedup.jsonl`, and `papers.ranked.jsonl` should be reviewed before being committed as curated data.
