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

## ADR-0004: Pydantic v2 for domain contracts

- Status: accepted
- Date: 2026-10-27
- Context: Milestone 1 needs typed, immutable domain models with runtime validation, deterministic JSON serialization, and an exportable JSON Schema. The charter lists Pydantic for runtime contracts and forbids domain dependencies on dataframe libraries, parser vendors, and LLM SDKs (Pydantic is none of these).
- Decision: Domain models are Pydantic v2 `BaseModel`s with `frozen=True`, `extra="forbid"`, `strict=True`, and `allow_inf_nan=False`. Per-object invariants raise `PydanticCustomError` whose type is the stable `GSL-*` issue code. `pydantic` is the only third-party import permitted in `domain/` (enforced by `tests/unit/test_architecture.py`).
  - Purpose: contracts, validation, serialization, JSON Schema. Licence: MIT. Maintenance: active (Pydantic Services; pydantic-core in Rust). Version: `>=2.9`.
- Alternatives: stdlib dataclasses in `domain/` with Pydantic DTOs at IO boundaries (more decoupled, ~2× model code plus a mapping layer); attrs + cattrs (no built-in JSON Schema).
- Consequences: One model set serves contract, validation, and schema export. Strict mode means JSON `"1"` is never coerced to an integer and `"true"` never to a boolean.
- Revisit when: Pydantic v3 changes core semantics, or validation cost dominates ingestion of large saves (Milestone 2 benchmark).

## ADR-0005: Canonical schema 0.1.0 — versioning, dates, relation vocabulary

- Status: accepted
- Date: 2026-10-27
- Context: Milestone 1 fixes the canonical contract before any production parser. Three choices were approved at the Step 5 gate: Pydantic in `domain/` (ADR-0004), open relation kinds, and structured game dates.
- Decision:
  - **Versioning.** `SCHEMA_VERSION = "0.1.0"` (semver). Pre-1.0, readers accept only the same `MAJOR.MINOR` (minor bumps are breaking); from 1.0, only the same `MAJOR`. Patch changes never break readers. Unsupported versions fail with `GSL-SCH-001` *before* structural parsing. No automatic migrations yet. The JSON Schema is committed at `data/manifests/game_state.schema.json`; a test fails on drift (`uv run gsl schema export` regenerates it).
  - **Dates.** `GameDate(year, month, day)`: totally ordered, serialized as zero-padded `YYYY-MM-DD`, bounded only to month 1–12 and day 1–31. No Gregorian leap-year assumption (EU4 has none); per-game calendar rules belong to adapters.
  - **Relation kinds.** `Relation.kind` is a lower-case dotted slug (`alliance`, `eu4.march`). Each adapter declares a `relation_kinds` vocabulary; kinds outside it produce warning `GSL-VOC-001`, not an error. No universal cross-game relation ontology (charter non-goal).
  - **Point-in-time safety.** Any date after `clock` is future information and fails with `GSL-DATE-002`, except `Relation.until` (scheduled expiries such as truces).
  - **Provenance.** Ingestion re-stamps `source_sha256`, `parsed_at_utc`, `adapter_name`, and `adapter_version`; adapters take an injectable clock so tests are deterministic.
  - **Input limits.** 10 MiB and JSON depth 64 by default (`InputLimits`), checked before model validation.
- Alternatives: closed relation enum (rejected: forces EU4/CK3/FM semantics into shared buckets); plain-string dates (rejected: weakens ordering and time-split checks); permissive reading of unknown versions with warnings (rejected: risks silently misread states).
- Consequences: Adding a field is a minor bump (breaking pre-1.0) and requires regenerating the committed JSON Schema and fixtures. Calendar validity (e.g. 30 February) is not caught in the domain.
- Revisit when: Milestone 2 maps real EU4 fields; CK3/FM adapters need non-day-granular clocks; the schema reaches 1.0.
