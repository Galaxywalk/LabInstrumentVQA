# Data Layout

## Benchmark Data

Benchmark VQA task files live under:

```text
data/benchmark/
```

Current starter file:

```text
data/benchmark/sample_tasks.jsonl
```

Image paths in task JSONL are resolved relative to the JSONL file. For example:

```text
data/benchmark/sample_tasks.jsonl
data/benchmark/images/oscilloscope_demo.svg
```

## Literature Metadata

Legal literature metadata lives under:

```text
data/literature/
```

Curated source files:

- `paper_metadata.schema.json`
- `source_rules.yaml`
- `seed_queries.yaml`
- `papers.seed.jsonl`

Generated files from collection runs should use explicit names such as:

- `papers.raw.jsonl`
- `papers.dedup.jsonl`
- `papers.ranked.jsonl`

Do not commit generated literature outputs unless they have been reviewed and promoted to curated data.

## Generated Outputs

Model outputs, temporary reports, and run artifacts should go under:

```text
outputs/
```

This directory is ignored by git.
