# LabInstrumentVQA

LabInstrumentVQA evaluates multimodal models on visual questions about electronic lab-instrument displays, such as oscilloscopes, spectrum analyzers, VNAs, logic analyzers, power supplies, and multimeters.

## OpenRouter Evaluation

This repo uses `uv` for Python dependency and environment management. Use the single project environment at `.venv`.

Create or update the environment:

```sh
uv sync
```

Set your OpenRouter API key:

```sh
export OPENROUTER_API_KEY="..."
```

Prepare a JSONL file with one sample per line:

```json
{"id":"scope_001","image":"images/scope_001.png","instrument":"oscilloscope","question":"What is the peak-to-peak voltage of channel 1?","answer":"2.0 Vpp"}
```

Run evaluation:

```sh
uv run lab-instrument-vqa \
  --input examples/sample_tasks.jsonl \
  --output outputs/openrouter_results.jsonl \
  --models '~openai/gpt-latest,~google/gemini-pro-latest,~anthropic/claude-sonnet-latest'
```

The output is JSONL with one row per `(sample, model)` pair, including the model prediction, optional ground-truth answer, and raw OpenRouter response.

The default model list uses current OpenRouter vision aliases:

- `~openai/gpt-latest`
- `~google/gemini-pro-latest`
- `~anthropic/claude-sonnet-latest`
- `x-ai/grok-4.3`
- `mistralai/mistral-medium-3-5`

## Data Format

Required fields:

- `id`: sample identifier
- `image`: local image path, relative to the JSONL file
- `question`: VQA prompt

Optional fields:

- `answer`: ground-truth answer
- `instrument`: instrument type
- `metadata`: structured metadata such as vendor, model, SCPI settings, or trace file paths

## Development

Always run Python commands through the same `uv` environment:

```sh
uv run python -m compileall src
uv run lab-instrument-vqa --help
```
