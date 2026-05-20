"""Command-line interface for OpenRouter VQA evaluation."""

from __future__ import annotations

import argparse

from .evaluator import load_jsonl, run_evaluation, write_jsonl
from .openrouter import OpenRouterClient, OpenRouterConfig


DEFAULT_MODELS = [
    "~openai/gpt-latest",
    "~google/gemini-pro-latest",
    "~anthropic/claude-sonnet-latest",
    "x-ai/grok-4.3",
    "mistralai/mistral-medium-3-5",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate OpenRouter vision models on LabInstrumentVQA samples."
    )
    parser.add_argument("--input", required=True, help="Input JSONL sample file.")
    parser.add_argument("--output", required=True, help="Output JSONL result file.")
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated OpenRouter model IDs.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    models = [model.strip() for model in args.models.split(",") if model.strip()]

    config = OpenRouterConfig.from_env()
    client = OpenRouterClient(config)
    samples = load_jsonl(args.input)
    results = run_evaluation(
        client=client,
        samples=samples,
        models=models,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    write_jsonl(args.output, [result.to_json() for result in results])


if __name__ == "__main__":
    main()
