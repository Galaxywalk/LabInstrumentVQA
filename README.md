# LabInstrumentVQA

LabInstrumentVQA is a benchmark scaffold for evaluating multimodal models on electronic lab-instrument displays: oscilloscopes, spectrum analyzers, vector network analyzers, logic analyzers, power supplies, and multimeters.

The target problem is not OCR alone. Models need to parse dense instrument UIs, ground traces to calibrated axes, extract numeric measurements, recognize instrument state, and make domain-specific diagnoses.

## Repository Map

```text
data/
  benchmark/      VQA task files and future image/annotation assets.
  literature/     Legal metadata-only ISSCC/JSSC literature survey workspace.
docs/             Research brief, benchmark design, and workflow notes.
src/              Python package and CLI implementations.
tests/            Unit tests for tooling and data contracts.
```

## Quick Start

Use one `uv` environment at the repo root:

```sh
uv sync
```

Run the OpenRouter evaluation CLI:

```sh
export OPENROUTER_API_KEY="..."

uv run lab-instrument-vqa \
  --input data/benchmark/sample_tasks.jsonl \
  --output outputs/openrouter_results.jsonl
```

Run literature metadata tools:

```sh
uv run literature-search \
  --rules data/literature/source_rules.yaml \
  --out data/literature/papers.raw.jsonl

uv run literature-dedupe \
  --input data/literature/papers.raw.jsonl \
  --out data/literature/papers.dedup.jsonl

uv run literature-rank \
  --input data/literature/papers.dedup.jsonl \
  --out data/literature/papers.ranked.jsonl
```

## Documentation

- [Research Brief](docs/research_brief.md)
- [Benchmark Design](docs/benchmark_design.md)
- [Data Layout](docs/data_layout.md)
- [Literature Workflow](docs/literature_workflow.md)
- [Development Notes](docs/development.md)

## Development

Run checks through `uv`:

```sh
uv run pytest
uv run python -m compileall src
```

Generated outputs belong under `outputs/` or explicit generated JSONL paths and should not be committed unless they are curated source data.
