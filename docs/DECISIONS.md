# Architecture Decision Records

Format: PROJECT_CHARTER.md § Governance → Decision records.

## ADR-0001: Standalone repository; charter overrides Sandbox conventions

- Status: accepted
- Date: 2026-10-27
- Context: The charter was drafted inside `Sandbox/Grand Strategy Lab/`, a subfolder of a multi-project Sandbox git repository whose root `CLAUDE.md` prescribes conda `environment.yml`, committed raw data under `data/raw/`, and R Markdown reports. The charter requires a standalone `grand-strategy-lab` repository with root-level CI, `uv`, and git-ignored raw inputs (saves must never be committed).
- Decision: Create `Sandbox/grand-strategy-lab/` as its own git repository (excluded from the Sandbox repo via `.git/info/exclude`). Rename the charter to `PROJECT_CHARTER.md` and fix its frontmatter delimiter (charter v0.1.1). Where the Sandbox `CLAUDE.md` conflicts with `PROJECT_CHARTER.md`, the charter governs this project.
- Alternatives: Keep as Sandbox subfolder (CI must live at Sandbox root with path filters; history mixes with unrelated projects).
- Consequences: Clean history and working CI; Sandbox-level academic conventions (Rmd, conda) do not apply unless re-adopted by ADR.
- Revisit when: The project is merged into a larger monorepo.

## ADR-0002: Milestone 0 toolchain

- Status: accepted
- Date: 2026-10-27
- Context: Charter § Technology baseline proposes uv, pyproject, Typer, pytest + Hypothesis, Ruff + Pyright. Each dependency must record purpose, licence, maintenance, alternatives, and removal cost.
- Decision:

| Package | Scope | Purpose | Licence | Maintenance | Alternatives | Removal cost |
|---|---|---|---|---|---|---|
| uv | tool | Env + lockfile | MIT/Apache-2.0 | Active (Astral) | pip-tools, Poetry | Low — standard `pyproject.toml` |
| hatchling | build | Build backend | MIT | Active (PyPA) | setuptools, uv_build | Low — swap `[build-system]` |
| typer | runtime | CLI | MIT | Active | click, argparse | Medium — rewrite `cli.py` |
| ruff | dev | Format + lint | MIT | Active (Astral) | black + flake8 | Low |
| pyright | dev | Type check | MIT | Active (Microsoft) | mypy | Low |
| pytest | dev | Tests | MIT | Active | unittest | High — test suite idioms |
| hypothesis | dev | Property tests | MPL-2.0 | Active | none comparable | Medium |
| pre-commit | dev | Local hooks | MIT | Active | lefthook | Low — optional |

- Alternatives: see table.
- Consequences: Pydantic is deferred to Milestone 1 (domain contracts) and recorded then. MPL-2.0 (Hypothesis) is dev-only and not redistributed.
- Revisit when: A tool becomes unmaintained or blocks a supported Python version.

## ADR-0003: Python and CI platform matrix

- Status: accepted
- Date: 2026-10-27
- Context: Charter requires Python 3.12+ and CI on a "documented platform matrix". The maintainer develops on Windows (local Python 3.14).
- Decision: Pin 3.12 locally via `.python-version`; CI runs Python 3.12 and 3.13 on `ubuntu-latest` and `windows-latest` with `uv sync --locked`.
- Alternatives: 3.12 only on Ubuntu (cheaper; misses Windows path issues); include 3.14 (scientific wheels may lag).
- Consequences: Four CI jobs per push; Windows path handling is tested.
- Revisit when: Milestone 3 adds compiled ML dependencies, or 3.14 wheels are universally available.
