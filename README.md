# Grand Strategy Lab

Open-source, reproducible research platform that turns strategy-game states into forecasts,
counterfactual simulations, and explainable recommendations. Initial vertical slice: an EU4
country-survival and strategic-risk advisor.

> Decision support for bounded scenarios under explicit objectives and uncertainty — not a
> claim to solve the game. See [PROJECT_CHARTER.md](PROJECT_CHARTER.md) for scope, architecture,
> and milestones.

**Status:** Milestone 0 (repository foundation). See [docs/STATUS.md](docs/STATUS.md).

## Quick start

Requires [uv](https://docs.astral.sh/uv/). No game install or save files are needed.

```bash
uv sync --all-extras --dev
uv run gsl --help
uv run gsl smoke          # loads the bundled synthetic fixture and prints its SHA-256
```

## Quality gates

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest -q
```

## Documentation

- [PROJECT_CHARTER.md](PROJECT_CHARTER.md) — product and architecture authority
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/DECISIONS.md](docs/DECISIONS.md) ·
  [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) · [CONTRIBUTING.md](CONTRIBUTING.md)

## Data policy

Local-first. Personal saves, game binaries, and protected assets are never committed;
`data/raw/`, `data/interim/`, `data/processed/`, and `artifacts/` are git-ignored.

## Licence

MIT for original source code; third-party components retain their own licences.
