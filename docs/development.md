# Development Notes

## Python Environment

Use `uv` for Python dependency and command management.

- Keep one project environment: `.venv` at the repo root.
- Add or remove dependencies through `pyproject.toml` with `uv add` or `uv remove`.
- Commit `uv.lock` when dependencies change.
- Run Python commands through `uv run`.

Common checks:

```sh
uv run pytest
uv run python -m compileall src
uv run lab-instrument-vqa --help
uv run literature-search --help
```

## Commit Message Rules

Use simplified Conventional Commits:

```text
<type>(<scope>): <subject>
```

Allowed types:

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation
- `style`: formatting only, no behavior change
- `refactor`: code restructuring
- `test`: tests
- `chore`: build, tooling, maintenance

Examples:

```text
feat(literature): add metadata pipeline scaffold
docs: clarify benchmark data layout
refactor(cli): split evaluation commands
```

Rules:

- Keep `subject` under 50 characters.
- Start `subject` with lowercase when using English.
- Do not end `subject` with a period.
- Add a body only when necessary.
