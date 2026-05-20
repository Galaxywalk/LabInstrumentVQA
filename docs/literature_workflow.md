# Literature Workflow

The literature workspace supports a legal metadata-only survey of recent ISSCC and JSSC papers relevant to LabInstrumentVQA.

## Policy

- Collect metadata, DOI landing pages, and legal open-access links only.
- Allowed examples include arXiv, IEEE Open Access pages, author pages, institutional repositories, DOI landing pages, OpenAlex metadata, and Semantic Scholar metadata.
- Do not use Sci-Hub, Library Genesis, or unauthorized full-text sources.

## Commands

Collect raw metadata:

```sh
uv run literature-search \
  --rules data/literature/source_rules.yaml \
  --out data/literature/papers.raw.jsonl
```

Deduplicate:

```sh
uv run literature-dedupe \
  --input data/literature/papers.raw.jsonl \
  --out data/literature/papers.dedup.jsonl
```

Rank for LabInstrumentVQA relevance:

```sh
uv run literature-rank \
  --input data/literature/papers.dedup.jsonl \
  --out data/literature/papers.ranked.jsonl
```

IEEE Xplore is optional. Set `IEEE_XPLORE_API_KEY` to include it; otherwise public metadata APIs are used.

## Review Flow

1. Run a small source-client smoke test with `--query-limit` and `--limit-per-query`.
2. Deduplicate raw records.
3. Rank by relevance score.
4. Manually review likely candidates.
5. Promote selected metadata into a curated JSONL file.
