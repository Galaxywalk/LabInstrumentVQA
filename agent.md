# Agent Notes

This repo is focused on building LabInstrumentVQA: a benchmark for multimodal understanding of lab-instrument displays.

Use these docs as the source of project intent:

- `docs/research_brief.md`: motivation, related-work gap, and paper direction.
- `docs/benchmark_design.md`: task taxonomy and expected model failure modes.
- `docs/data_layout.md`: where benchmark data, literature metadata, and generated outputs belong.
- `docs/development.md`: commit style and `uv` workflow.

Core rules:

- Use legal metadata and open-access links only for literature collection.
- Do not use Sci-Hub or unauthorized full-text sources.
- Keep one Python environment at `.venv` managed by `uv`.
- Keep generated model outputs out of source data unless they are manually curated.
