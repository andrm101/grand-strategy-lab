# Contributing

Read [PROJECT_CHARTER.md](PROJECT_CHARTER.md) before substantial work.

## Quality gates

Every change must pass:

```bash
uv sync --all-extras --dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest -q
```

Optional: `uv run pre-commit install` to run Ruff on commit.

## Definition of ready

A task has: a user or research outcome; explicit scope and exclusions; inputs, outputs, and
interfaces; dependencies and unknowns; a test strategy; acceptance criteria; data/licence
implications.

## Definition of done

Acceptance criteria pass; code is formatted, linted, typed, and tested; docs and decision
records are updated; error paths are covered; outputs reproduce from committed config; no
secret, personal save, protected asset, or unnecessary generated artifact is committed;
Sentinel review finds no unresolved critical issue.

## Decisions and dependencies

Significant decisions are recorded as ADRs in [docs/DECISIONS.md](docs/DECISIONS.md). Any
dependency change records purpose, licence, maintenance status, alternatives, and removal cost.

## Prohibited contributions

Features for cheating, anti-cheat bypass, covert telemetry, live-client control, or
unauthorised multiplayer automation; unlicensed datasets; game assets.
