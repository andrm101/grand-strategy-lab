# Grand Strategy Lab

Read `PROJECT_CHARTER.md` before planning substantial work.

## Commands

- Install: `uv sync --all-extras --dev`
- CLI: `uv run gsl --help`
- Format check: `uv run ruff format --check .`
- Lint: `uv run ruff check .`
- Type check: `uv run pyright`
- Tests: `uv run pytest -q`
- Single test: `uv run pytest path/to/test.py -q`

## Workflow

1. Inspect before editing.
2. For non-trivial work, propose a file-level plan and acceptance checks.
3. Implement the smallest coherent vertical slice.
4. Run focused tests, then all quality gates.
5. Update `docs/DECISIONS.md` and `docs/STATUS.md` when applicable.
6. Report changed files, commands run, results, assumptions, and remaining risks.

## Guardrails

- Never commit saves, secrets, `.env`, generated datasets, or protected game assets.
- Do not invent game fields, schemas, mechanics, metrics, or research results.
- Keep domain contracts independent of data-frame, parser-vendor, and LLM SDK types.
- Require explicit seeds and manifests for stochastic experiments.
- Use campaign/time-aware validation; never fit transforms on validation or test data.
- LLM output may explain tool evidence but may not replace numerical computation.
- Ask before adding production dependencies, changing public schemas, deleting files, or performing networked/side-effecting operations.

## Source of truth

- Scope and milestones: `PROJECT_CHARTER.md`
- Architecture: `docs/ARCHITECTURE.md`
- Decisions: `docs/DECISIONS.md`
- Current work: `docs/STATUS.md`
- Domain rules: `.claude/rules/`
