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
- Decision: Domain models are Pydantic v2 `BaseModel`s with `frozen=True`, `extra="forbid"`, `strict=True`, and `allow_inf_nan=False`. Per-object invariants raise `PydanticCustomError` whose type is the stable `GSL-*` issue code. `pydantic` and its core package `pydantic_core` are the only third-party imports permitted in `domain/` (enforced by `tests/unit/test_architecture.py`).
  - `frozen` blocks attribute assignment only: `dict` fields (actors, territories, extensions) remain mutable containers and models are unhashable. States are read-only by convention, not deeply immutable.
  - `allow_inf_nan=False` does not reach free-form `JsonValue` extensions; non-finite numbers anywhere in the input are rejected by the raw-document scan in `validation/parse.py` (`GSL-NUM-001`).
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
  - **Point-in-time safety.** Any date after `clock` is future information and fails with `GSL-DATE-002`. This covers typed fields and every canonical `YYYY-MM-DD` string inside `extensions` (adapters must model scheduled future dates as typed fields, and dates in other formats inside extensions are not detected). The single exemption is `Relation.until`, for every relation kind: an alliance, guarantee, or truce may carry a known scheduled expiry. `Conflict.ended` is not exempt: an end date is an observed event, not a schedule.
  - **Raw-input integrity.** Before structural parsing, the raw document is scanned for nesting depth, duplicate object keys (`GSL-IO-005`; JSON parsers silently keep the last value), and non-finite numbers (`GSL-NUM-001`), each reported with its JSON pointer. Integer literals beyond the interpreter's digit limit are `GSL-IO-003`.
  - **Missing metadata.** The schema-version gate (`GSL-SCH-001`) fires only for a declared but unsupported version string; a missing `metadata` object or version is a structural error (`GSL-STR-001`).
  - **ASCII patterns.** All schema patterns use `[0-9]`, not the backslash-d class, so Python, Pydantic, and external JSON Schema validators agree (non-ASCII digits are rejected).
  - **Provenance.** Ingestion re-stamps `source_sha256`, `parsed_at_utc`, `adapter_name`, and `adapter_version`; adapters take an injectable clock so tests are deterministic.
  - **Input limits.** 10 MiB and JSON depth 64 by default (`InputLimits`), checked before model validation.
- Alternatives: closed relation enum (rejected: forces EU4/CK3/FM semantics into shared buckets); plain-string dates (rejected: weakens ordering and time-split checks); permissive reading of unknown versions with warnings (rejected: risks silently misread states).
- Consequences: Adding a field is a minor bump (breaking pre-1.0) and requires regenerating the committed JSON Schema and fixtures. Calendar validity (e.g. 30 February) is not caught in the domain.
- Revisit when: Milestone 2 maps real EU4 fields; CK3/FM adapters need non-day-granular clocks; the schema reaches 1.0.
- Amended 2026-10-27 after Step 7 review: raw-input integrity, extension dates, missing-metadata handling, ASCII patterns; codes `GSL-IO-005` and `GSL-CON-002` added; `GSL-IO-001` widened to "missing or unreadable" (no release had shipped).

## ADR-0006: Runtime dependency inventory

- Status: accepted
- Date: 2026-10-27
- Context: Charter § Technology baseline requires recording purpose, licence, maintenance, and removal cost for dependencies; ADR-0002/0004 covered direct dependencies only. Inventory from `uv tree --no-dev` and installed package metadata at `uv.lock` as of this date.
- Decision: Accept the transitive runtime set below. All licences are permissive; none is copyleft.

| Package | Version | Pulled in by | Licence |
|---|---|---|---|
| pydantic | 2.14.1 | direct | MIT |
| pydantic-core | 2.50.1 | pydantic | MIT |
| annotated-types | 0.8.0 | pydantic | MIT |
| typing-inspection | 0.4.4 | pydantic | MIT |
| typing-extensions | 4.16.0 | pydantic, pydantic-core | PSF-2.0 |
| typer | 0.27.3 | direct | MIT |
| rich | 15.0.0 | typer | MIT |
| markdown-it-py | 4.2.0 | rich | MIT |
| mdurl | 0.1.2 | markdown-it-py | MIT |
| pygments | 2.21.0 | rich | BSD-2-Clause |
| shellingham | 1.5.4 | typer | ISC |
| colorama | 0.4.6 | typer | BSD-3-Clause |
| annotated-doc | 0.0.5 | typer | MIT |

- Alternatives: `typer-slim` or `argparse` to drop rich/shellingham/colorama (reconsider if install size matters).
- Consequences: Any lockfile change that adds a runtime package must extend this table.
- Revisit when: a dependency changes licence, or the runtime set grows.
