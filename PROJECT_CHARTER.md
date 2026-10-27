---
title: Grand Strategy Lab — Project Charter
aliases:
  - Grand Strategy Lab
  - GSL Charter
type: project-charter
status: proposed
version: 0.1.1
created: 2026-10-27
updated: 2026-10-27
owner: Project Maintainer
repository: grand-strategy-lab
tags:
  - project/grand-strategy-lab
  - domain/game-ai
  - domain/machine-learning
  - domain/agent-based-modelling
  - domain/game-theory
  - tool/claude-code
  - status/proposed
primary_game: EU4
license: MIT
---

# Grand Strategy Lab — Project Charter

> [!abstract] Mission
> Build an open-source, reproducible research platform that converts strategy-game states into forecasts, counterfactual simulations, and explainable recommendations using machine learning, agent-based modelling, game theory, and tool-using AI agents.

> [!important] Product framing
> The project does **not** claim to solve an entire commercial game or discover universally optimal play. It provides decision support for bounded scenarios under explicit objectives, assumptions, and uncertainty.

## Claude Code entry point

Claude Code can inspect a repository, edit files, execute commands, and support Git workflows from a terminal or IDE. Treat this document as the authoritative product specification, while keeping the root `CLAUDE.md` short because Claude loads that file into every session; detailed or path-specific rules should live in linked documentation or `.claude/rules/`.[^1][^2][^3]

Start development from the repository root with:

```bash
claude "Read PROJECT_CHARTER.md in full. Inspect the repository without modifying files. Then produce an implementation plan for Milestone 0 and Milestone 1, including proposed files, interfaces, tests, risks, and acceptance checks. Wait for approval before implementation. Do not invent game schemas or dependencies; record unknowns as decisions or research spikes."
```

After approving the plan:

```bash
claude "Implement the approved Milestone 0 and Milestone 1 plan from PROJECT_CHARTER.md. Work in small verifiable increments. Run formatting, linting, type checking, and tests after each coherent change. Update docs/DECISIONS.md and docs/STATUS.md when decisions or scope change. Stop and report if an acceptance criterion cannot be satisfied."
```

## Project identity

| Field | Definition |
|---|---|
| Working name | **Grand Strategy Lab** |
| Repository | `grand-strategy-lab` |
| Initial vertical slice | EU4 country-survival and strategic-risk advisor |
| Primary users | Players, game-AI researchers, data scientists, modders, and portfolio reviewers |
| Primary interface | Python CLI and reproducible notebooks |
| Later interface | Local dashboard/API and natural-language strategy advisor |
| Core languages | Python 3.12+; SQL where useful; optional Rust boundary for Paradox parsing |
| Data policy | Local-first; no copyrighted game assets or proprietary databases committed |
| Initial licence | MIT for original source code; third-party components retain their own licences |

## Vision

Grand Strategy Lab will provide a common experimental loop:

1. Ingest a game save, export, or synthetic test fixture.
2. Normalize it into a versioned, game-agnostic state representation.
3. Estimate relevant outcomes and calibrated uncertainty.
4. Generate bounded candidate actions.
5. compare those actions through simulation and strategic analysis.
6. Return ranked recommendations with assumptions, evidence, uncertainty, and failure modes.
7. Store experiment manifests so results can be reproduced.

The architecture must support additional adapters for Crusader Kings III and Football Manager without forcing all games into one universal ontology.

## Problem statement

Complex strategy and management games combine partial observability, stochastic events, interacting agents, changing rules, and multiple plausible objectives. A recommendation can therefore be useful without being globally optimal: it must be tied to a declared objective, a time horizon, a model version, a game version, and an uncertainty estimate.

The first bounded problem is:

> Given an EU4 save and a selected country, estimate strategic risk over a configurable horizon and compare a small set of candidate diplomatic, economic, and military actions using prediction and counterfactual simulation.

## Project principles

- **Bounded claims:** Say “forecast,” “rank,” “simulate,” or “recommend,” not “solve,” unless optimality is mathematically established for a reduced game.
- **Data before agents:** Build validated ingestion and deterministic baselines before reinforcement learning or LLM orchestration.
- **LLM as orchestrator:** Language models may select tools and explain outputs; they must not fabricate state, rules, probabilities, or model results.
- **Reproducibility by default:** Every experiment records configuration, seed, source hash, schema version, code revision, model version, and environment metadata.
- **Uncertainty is output:** Report calibration, confidence or credible intervals, scenario spread, and out-of-distribution warnings.
- **Leakage prevention:** Split campaigns and time windows so future state cannot leak into training features.
- **Version awareness:** Treat patches, DLC configuration, mods, and parser versions as first-class metadata.
- **Local-first safety:** Do not automate multiplayer clients, bypass anti-cheat, inject into running processes, or redistribute protected game content.
- **Thin vertical slices:** Complete ingestion-to-recommendation paths before broadening game coverage.
- **Tests are specifications:** Parsers, schemas, simulations, and metrics require explicit invariants and regression fixtures.

## Goals

### Product goals

- Parse a supported EU4 save or canonical fixture into validated entities and relations.
- Generate a country-level state vector and diplomacy graph.
- Predict at least one clearly labelled outcome over a declared horizon.
- Run deterministic and stochastic counterfactual scenarios from the same state.
- Rank candidate actions by expected utility and downside risk.
- Explain each recommendation using only recorded tool outputs.
- Reproduce an experiment from a single manifest and command.
- Expose extension interfaces for CK3 and Football Manager adapters.

### Research goals

- Compare heuristic, supervised-learning, simulation-based, and game-theoretic policies.
- Test whether graph features improve forecasts over tabular baselines.
- Measure simulation fidelity against held-out campaign trajectories.
- Evaluate recommendation quality using backtesting and structured human review.
- Document where cross-game abstractions transfer and where domain-specific models remain necessary.

### Portfolio goals

- Demonstrate data engineering, typed Python, ML evaluation, simulation design, graph modelling, MLOps, and agentic orchestration.
- Maintain a legible commit history, architecture decisions, model cards, data cards, and reproducible demonstrations.
- Provide one command that runs a small end-to-end demonstration without proprietary data.

## Non-goals

The first release will not:

- Control a live game or automate user input.
- Support multiplayer optimisation or anti-cheat circumvention.
- Model every EU4 mechanic, country, DLC, or mod.
- Train reinforcement-learning agents against the full commercial game.
- Promise optimal strategies or causal conclusions from observational saves.
- Use an LLM as the numerical simulator, rules engine, or source of truth.
- Commit personal saves, decoded token tables without redistribution rights, game binaries, or copyrighted assets.
- Support CK3 and Football Manager beyond stable adapter contracts and documented future designs.
- Require cloud infrastructure for the MVP.

## Success measures

| Dimension | MVP measure | Release gate |
|---|---|---|
| Ingestion | Supported fixtures parse into the canonical schema | 100% fixture pass rate and actionable errors for invalid input |
| Data quality | Required fields, types, ranges, and referential integrity validated | No silent coercion of invalid critical fields |
| Reproducibility | Repeated run with same manifest and seed | Identical deterministic outputs; stochastic summaries within test tolerance |
| Prediction | Baseline and candidate model evaluated out of campaign/time | Candidate must beat a naive baseline on a predeclared primary metric |
| Calibration | Probabilities evaluated with calibration diagnostics | Brier score and reliability output included in model report |
| Simulation | Core invariants hold across seeded property tests | No negative impossible resources or broken relation references |
| Recommendation | Every ranked action has utility, uncertainty, assumptions, and provenance | No free-form unsupported recommendation |
| Engineering | CI runs lint, type checks, unit tests, and integration tests | Green CI on supported Python versions |
| Usability | Demo runs from documented commands using included fixtures | Fresh-environment smoke test passes |

Exact numeric performance thresholds beyond baseline improvement must be selected after the first data audit. They must not be chosen after observing test-set results.

## Initial use case

### EU4 strategic-risk advisor

**Input**

- Save or canonical fixture.
- Player country tag.
- Objective profile.
- Forecast horizon.
- Candidate action set or action-generation constraints.
- Optional patch, DLC, and mod metadata.

**Output**

- Validated state summary.
- Outcome probabilities and calibration metadata.
- Top risks and influential features.
- Ranked candidate actions.
- Counterfactual scenario distributions.
- Strategic interaction notes.
- Assumptions, unsupported mechanics, and out-of-distribution warnings.
- Machine-readable run manifest.

**Initial objective profile**

```yaml
objective:
  name: survival_balanced
  horizon_years: 10
  utility_weights:
    survival: 0.45
    solvency: 0.20
    territorial_security: 0.20
    diplomatic_security: 0.15
  risk_aversion: 0.35
```

The weights above are defaults for software design and test fixtures, not empirical claims. Users must be able to override them.

## System architecture

```mermaid
flowchart LR
    A[Save / export / fixture] --> B[Game adapter]
    B --> C[Canonical state]
    C --> D[Validation]
    D --> E[Feature pipeline]
    E --> F[Predictive models]
    D --> G[Scenario simulator]
    D --> H[Strategic models]
    F --> I[Decision engine]
    G --> I
    H --> I
    I --> J[Advisor tools]
    J --> K[CLI / API / dashboard]
    I --> L[Experiment registry]
    F --> L
    G --> L
```

### Component boundaries

| Component | Responsibility | Must not do |
|---|---|---|
| Adapter | Read source format and map fields | Rank actions or infer missing critical values silently |
| Canonical schema | Represent shared concepts and game extensions | Erase game-specific semantics |
| Validator | Enforce contracts and produce quality reports | Mutate source data without provenance |
| Feature pipeline | Produce point-in-time-safe model features | Read future outcomes during inference |
| Predictor | Estimate labelled outcomes and uncertainty | Present association as causation |
| Simulator | Apply explicit transitions under seeded randomness | Use an LLM to calculate state transitions |
| Strategic model | Evaluate bargaining, coalitions, incentives, and responses | Claim a full-game equilibrium without a defined reduced game |
| Decision engine | Combine objective, forecasts, simulations, and constraints | Hide utility weights or uncertainty |
| Advisor | Call typed tools and explain returned evidence | Invent actions, mechanics, or numeric results |
| Registry | Persist manifests, metrics, and artifact lineage | Store unlicensed source content |

## Canonical domain model

The common model is intentionally small. Each adapter may attach a namespaced extension object.

```python
GameState
├── metadata: GameMetadata
├── clock: GameClock
├── actors: dict[ActorId, Actor]
├── territories: dict[TerritoryId, Territory]
├── relations: list[Relation]
├── conflicts: list[Conflict]
├── resources: list[ResourcePosition]
└── extensions: dict[str, JsonValue]
```

### Required metadata

```yaml
game_id: eu4
game_version: unknown-or-semver
schema_version: 0.1.0
source_kind: fixture|save|export
source_sha256: string
observed_at_game_time: string
parsed_at_utc: datetime
adapter_name: string
adapter_version: string
dlc: []
mods: []
```

### EU4 extension

The EU4 adapter may add country tags, monarch power, technology, ideas, manpower, force limits, autonomy, aggressive expansion, overextension, subjects, truces, institutions, and war participation. Every field must define type, unit, temporal meaning, missing-value policy, and source mapping in `docs/data-dictionary/eu4.md`.

An existing low-level parser, Jomini, supports files from multiple Paradox titles, including EU4 and CK3. The dedicated `eu4save` repository supports EU4 save analysis but was archived in September 2026, so parser adoption requires a maintenance-risk assessment rather than an uncritical dependency choice.[^4][^5]

## Data strategy

### Allowed sources

- User-owned local saves used privately.
- Small hand-authored or transformed fixtures that contain no protected assets.
- User-contributed derived datasets with explicit licence and provenance.
- Simulation outputs created by this project.
- Public documentation referenced by URL rather than copied wholesale.

### Data zones

```text
data/
├── fixtures/          # Tiny, reviewable, redistributable test inputs
├── raw/               # Git-ignored local inputs
├── interim/           # Git-ignored parsed snapshots
├── processed/         # Git-ignored modelling tables
└── manifests/         # Committed schemas and example manifests
```

### Dataset rules

- Never overwrite raw inputs.
- Hash every input before processing.
- Store transformations as code, not manual spreadsheet steps.
- Separate actor identifiers from display names where possible.
- Partition training, validation, and test data by campaign before any row-level split.
- Fit encoders and imputers on training data only.
- Record patch, DLC, mod, and parser metadata.
- Reject unknown critical fields or map them explicitly to `null` with a reason code.
- Publish data cards describing origin, rights, coverage, missingness, bias, and prohibited uses.

## Modelling strategy

### Baseline ladder

1. **Rules and naive priors:** majority class, historical base rate, and simple risk score.
2. **Interpretable tabular models:** logistic regression and regularized linear models.
3. **Tree models:** gradient-boosted trees for nonlinear tabular relationships.
4. **Temporal models:** only after reliable campaign snapshots exist.
5. **Graph models:** only after diplomacy graph construction and graph-free baselines are stable.
6. **Reinforcement learning:** only inside a validated reduced simulator with a defined action space and reward function.

### Initial prediction task

```yaml
task: strategic_distress
unit_of_analysis: country_snapshot
horizon_years: 10
candidate_label:
  any_of:
    - bankruptcy
    - forced_vassalization_or_annexation
    - severe_debt_threshold
    - major_war_loss
status: requires_label_audit
primary_metric: brier_score
secondary_metrics:
  - pr_auc
  - roc_auc
  - log_loss
  - calibration_error
validation:
  grouping: campaign_id
  ordering: observed_at_game_time
```

The label is provisional. Milestone 2 must test its observability, prevalence, ambiguity, and susceptibility to leakage before model training.

### Model governance

Every trained model must have:

- Immutable configuration.
- Dataset and feature schema hashes.
- Campaign-separated evaluation.
- Baseline comparison.
- Calibration analysis.
- Slice analysis by patch, campaign stage, and country-size band where data permits.
- Model card with intended use, exclusions, limitations, and retraining conditions.
- Serialization test and inference-contract test.
- A deterministic model version exposed to downstream tools.

## Simulation strategy

The simulator is a reduced decision environment, not an emulator of EU4.

### State

- Economy: treasury, income, expenses, debt burden.
- Military: manpower, force strength, readiness, war exhaustion.
- Diplomacy: allies, rivals, subjects, truces, threat and trust proxies.
- Territorial security: strategic provinces, exposure, defensibility proxy.
- Internal stability: stability, unrest proxy, legitimacy-equivalent fields.

### Action families

- Seek, retain, or abandon an alliance.
- Accumulate reserves or reduce debt.
- Build or consolidate military capacity.
- Enter, avoid, or exit a bounded conflict.
- Improve a selected diplomatic relation.
- Pursue a constrained territorial objective.
- Take a no-op/wait action.

### Transition requirements

- Pure transition functions where practical.
- Seeded random-number generator passed explicitly.
- No hidden global state.
- Units and bounds encoded in types or validators.
- Invariants tested with property-based tests.
- Unsupported mechanics declared in scenario metadata.
- Parameters calibrated only from documented data or marked as assumptions.

### Scenario output

```yaml
scenario_id: uuid
base_state_hash: sha256
policy_id: string
action_id: string
seed_set: [1, 2, 3]
rollouts: integer
horizon_steps: integer
utility_mean: number
utility_interval: [number, number]
downside_probability: number
assumptions: []
unsupported_mechanics: []
```

## Game-theory layer

Game theory will be applied to reduced, explicit strategic interactions.

### Initial models

- **Alliance reliability:** repeated game with cooperation, defection, reputation, and discounting.
- **Coalition response:** threshold or coalition-formation model over threat and expected utility.
- **Peace bargaining:** constrained bargaining model with outside options and asymmetric information proxies.
- **Deterrence:** attacker-defender game using expected payoff and credible-response assumptions.

### Required specification

Each strategic model must state:

- Players.
- Available actions.
- Information available to each player.
- Payoff function.
- Timing and repetition.
- Solution concept.
- Parameter source.
- Sensitivity analysis.
- Conditions under which the result is not valid.

No equilibrium claim may leave those elements implicit.

## Agentic layer

The agentic layer is a typed orchestration system around deterministic or statistically evaluated tools.

### Approved tools

```text
load_game_state(path) -> StateSummary
validate_state(state_id) -> ValidationReport
predict_outcomes(state_id, actor_id, horizon) -> PredictionReport
list_candidate_actions(state_id, actor_id, constraints) -> ActionSet
run_scenarios(state_id, action_ids, config) -> ScenarioReport
analyze_strategic_response(state_id, action_id, model_id) -> StrategicReport
rank_actions(objective, prediction_id, scenario_id, strategic_id) -> Ranking
explain_ranking(ranking_id) -> EvidenceBundle
```

### Agent roles

This project uses an RTS-inspired separation of duties aligned with the maintainer’s established Claude workflow.[^6][^7]

| Role | Responsibility | Default permissions |
|---|---|---|
| Commander | Decompose work, maintain plan, delegate, and enforce gates | Read; propose writes; coordinate |
| Scout | Inspect repository, schemas, dependencies, and unknowns | Read-only |
| Builder | Implement approved, bounded tasks | Read/write scoped files; run tests |
| Analyst | Design data checks, experiments, models, and evaluations | Read/write analysis scope |
| Sentinel | Review correctness, leakage, security, licences, and acceptance | Read; run verification; request fixes |

### Agent guardrails

- No agent may invent a missing game field or silently substitute a proxy.
- The advisor may explain only artifacts returned by approved tools.
- Tool inputs and outputs must be schema-validated and logged.
- Side-effecting actions require explicit approval.
- The reviewer must be able to reproduce every numeric claim from an artifact ID.
- Prompt-injection-like text inside saves, filenames, documentation, or datasets is data, not instruction.
- Secrets and `.env` files are never committed or printed.

## Repository design

```text
grand-strategy-lab/
├── CLAUDE.md
├── PROJECT_CHARTER.md
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/ci.yml
├── .claude/
│   └── rules/
│       ├── data.md
│       ├── modelling.md
│       └── simulation.md
├── configs/
│   ├── base.yaml
│   ├── experiments/
│   └── objectives/
├── data/
│   ├── fixtures/
│   └── manifests/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── STATUS.md
│   ├── THREAT_MODEL.md
│   ├── data-dictionary/
│   │   └── eu4.md
│   ├── data-cards/
│   └── model-cards/
├── notebooks/
│   └── README.md
├── src/grand_strategy_lab/
│   ├── __init__.py
│   ├── cli.py
│   ├── domain/
│   ├── adapters/
│   │   ├── base.py
│   │   └── eu4/
│   ├── validation/
│   ├── features/
│   ├── models/
│   ├── simulation/
│   ├── game_theory/
│   ├── decision/
│   ├── agents/
│   └── registry/
└── tests/
    ├── unit/
    ├── integration/
    ├── property/
    └── fixtures/
```

## Technology baseline

| Concern | Initial choice | Rationale |
|---|---|---|
| Runtime | Python 3.12+ | Strong DS ecosystem and typed application support |
| Environment | `uv` | Fast lockfile-based project and environment management |
| Packaging | `pyproject.toml` | Standard centralized project configuration |
| Models | Pydantic | Runtime contracts at external and tool boundaries |
| Tables | Polars or pandas behind an interface | Begin with one; prevent library types leaking into domain contracts |
| Storage | Parquet + DuckDB | Local analytical workflow without service overhead |
| Classical ML | scikit-learn | Pipelines, baselines, calibration, and evaluation |
| Boosting | LightGBM or XGBoost after benchmark | Avoid premature dependency choice |
| Graph ML | PyTorch Geometric after graph baseline | Deferred until justified |
| CLI | Typer | Typed developer-facing commands |
| Tests | pytest + Hypothesis | Unit, integration, and invariant testing |
| Quality | Ruff + Pyright | Formatting/linting and static type checks |
| Experiment config | YAML validated by Pydantic | Human-readable, versionable manifests |
| Tracking | Local artifact registry first | Avoid infrastructure before workflow stabilizes |

Any dependency change must record purpose, licence, maintenance status, alternatives considered, and removal cost in `docs/DECISIONS.md`.

## CLI contract

The target command surface is:

```bash
gsl --help
gsl ingest --game eu4 --input PATH --output data/interim/state.json
gsl validate --state data/interim/state.json
gsl features build --state data/interim/state.json --actor FRA
gsl train --config configs/experiments/distress-baseline.yaml
gsl evaluate --run RUN_ID
gsl simulate --state data/interim/state.json --actor FRA --config configs/scenarios/base.yaml
gsl advise --state data/interim/state.json --actor FRA --objective configs/objectives/survival-balanced.yaml
gsl reproduce --manifest artifacts/RUN_ID/manifest.yaml
```

Each command must support `--help`; commands that create artifacts must support `--seed`, `--output`, and a machine-readable error mode where relevant.

## Quality gates

A pull request is complete only when all applicable checks pass:

```bash
uv sync --all-extras --dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest -q
```

Additional gates:

- Public functions and classes have typed interfaces and concise docstrings.
- New behavior includes tests at the lowest sensible level.
- Parser changes include fixture-based regression tests.
- Model changes include leakage review, baseline comparison, and report updates.
- Simulation changes include invariant tests and seeded reproducibility checks.
- CLI changes include help-text and exit-code tests.
- User-facing changes update the README or relevant documentation.
- No generated datasets, secrets, personal saves, model binaries, or notebook output are committed.
- All acceptance criteria are verified, not merely asserted.

## Milestones

### Milestone 0 — Repository foundation

**Objective:** establish a reproducible, agent-ready Python repository.

**Deliverables**

- Repository structure and Python package.
- `pyproject.toml`, lockfile, development dependencies, and CLI stub.
- CI for formatting, linting, type checking, and tests.
- Root `CLAUDE.md` and path-scoped `.claude/rules/`.
- Architecture, decisions, status, threat-model, and contribution documents.
- Tiny redistributable canonical fixtures.
- One-command smoke test.

**Acceptance criteria**

- Fresh clone can install, run `gsl --help`, and execute all quality gates.
- CI passes on the documented platform matrix.
- `PROJECT_CHARTER.md` is linked from `README.md` and `CLAUDE.md`.
- No real save or protected game content is required.

### Milestone 1 — Canonical schema

**Objective:** define stable contracts before adopting a production parser.

**Deliverables**

- Typed `GameState`, actor, relation, conflict, resource, and metadata models.
- Adapter protocol and fixture adapter.
- Validation report with severity, path, code, and remediation fields.
- JSON serialization and schema versioning.
- EU4 data dictionary skeleton.

**Acceptance criteria**

- Valid fixtures round-trip without semantic loss.
- Invalid fixtures produce deterministic, actionable errors.
- Referential integrity and numeric invariants have property tests.
- Domain code does not depend on pandas, Polars, a parser vendor, or an LLM SDK.

### Milestone 2 — EU4 ingestion spike

**Objective:** select and prove an EU4 ingestion strategy.

**Deliverables**

- Architecture decision comparing maintained parser options, CLI conversion, and a narrow internal parser.
- Local-save ingestion path behind the adapter interface.
- Source hashing, patch metadata, and parser diagnostics.
- Mapping for the minimum viable country, diplomacy, economy, military, and war fields.
- Licence and redistribution assessment.

**Acceptance criteria**

- At least two legally usable local test cases map to the same canonical schema.
- Unknown tokens or unsupported fields are reported explicitly.
- Parser failure cannot produce a superficially valid state.
- Raw saves remain outside Git.

Rakaly CLI can melt several Paradox save formats and can watch files to create campaign snapshots, making it a candidate for a local preprocessing spike rather than a committed dependency decision.[^8]

### Milestone 3 — Dataset and baselines

**Objective:** establish trustworthy data and evaluation before advanced models.

**Deliverables**

- Snapshot extraction pipeline and feature registry.
- Label audit for strategic distress.
- Campaign-based train/validation/test split.
- Naive, logistic-regression, and tree-based baselines.
- Calibration, slice analysis, data card, and model card.

**Acceptance criteria**

- Feature timestamps satisfy point-in-time rules.
- The held-out test set remains untouched until model selection is complete.
- Metrics can be reproduced from a run manifest.
- Candidate model exceeds the declared naive baseline or the project records a valid negative result.

### Milestone 4 — Reduced simulator

**Objective:** evaluate actions under explicit simplified dynamics.

**Deliverables**

- State transition and policy interfaces.
- Seeded Monte Carlo runner.
- Heuristic opponent policies.
- Utility and risk aggregation.
- Invariant, reproducibility, and sensitivity tests.

**Acceptance criteria**

- Same state, action, configuration, and seed produce the same trajectory.
- Parameter assumptions are visible in output artifacts.
- Simulation results are distinguishable from predictive-model estimates.
- Unsupported mechanics are included in every report.

### Milestone 5 — Decision engine

**Objective:** combine forecasts, scenarios, and strategic responses into transparent action rankings.

**Deliverables**

- Objective profiles and constraint schema.
- Candidate-action generator.
- Multi-criteria utility and downside-risk ranking.
- Initial deterrence or alliance repeated-game model.
- Ranking evidence bundle.

**Acceptance criteria**

- Rankings change predictably under tested changes to objectives and risk aversion.
- Every score traces to model, scenario, or strategic-analysis artifacts.
- Missing evidence reduces confidence or blocks ranking; it is never fabricated.

### Milestone 6 — Agentic advisor

**Objective:** add natural-language orchestration without compromising numerical integrity.

**Deliverables**

- Typed tool interfaces.
- Planner/advisor flow with bounded retries.
- Evidence-linked recommendation template.
- Prompt-injection and malformed-tool-output tests.
- Optional local API or minimal dashboard.

**Acceptance criteria**

- All numeric statements in advisor output exist in referenced artifacts.
- The advisor refuses unsupported questions or clearly narrows them.
- Tool calls are auditable and schema-valid.
- A deterministic non-LLM report remains available.

### Milestone 7 — Cross-game adapters

**Objective:** test transferability without weakening the EU4 vertical slice.

**Deliverables**

- CK3 adapter design for characters, titles, dynasties, claims, and succession.
- Football Manager adapter design for clubs, players, contracts, matches, and transfers.
- Cross-game abstraction report.
- One small fixture per game.

**Acceptance criteria**

- Shared contracts remain minimal and stable.
- Game-specific semantics stay in namespaced extensions.
- No adapter is declared supported until it passes an end-to-end demo.

## Backlog priorities

### Must

- [ ] Repository and CI foundation.
- [ ] Canonical state schema and fixture adapter.
- [ ] EU4 parser decision record and narrow ingestion proof.
- [ ] Data-quality report and data dictionary.
- [ ] Campaign-safe baseline evaluation.
- [ ] Seeded reduced simulator.
- [ ] Objective-driven ranking.
- [ ] Reproducible CLI demonstration.

### Should

- [ ] Diplomacy graph features.
- [ ] Calibration dashboard.
- [ ] Strategic alliance or deterrence model.
- [ ] Model and data cards.
- [ ] Agentic advisor using typed tools.
- [ ] Obsidian dashboard note using links and queries.

### Could

- [ ] Graph neural network benchmark.
- [ ] Bayesian parameter calibration.
- [ ] CK3 character-network proof of concept.
- [ ] Football Manager transfer-market proof of concept.
- [ ] Streamlit or web dashboard.
- [ ] Plugin system for community adapters.

### Won’t yet

- [ ] Full-game RL.
- [ ] Live client control.
- [ ] Multiplayer automation.
- [ ] Universal cross-game ontology.
- [ ] Cloud-first production deployment.

## Risks

| Risk | Impact | Mitigation | Trigger |
|---|---|---|---|
| Save-format or patch drift | Parser and feature breakage | Adapter isolation, fixtures, version metadata, compatibility matrix | New patch fails regression fixtures |
| Archived or unmaintained parser | Security and maintenance burden | Time-boxed spike, wrapper boundary, fallback design | Critical issue lacks upstream resolution |
| Sparse campaign data | Weak generalization | Start with baselines, uncertainty, community data protocol, simulation separated from observation | Wide intervals or unstable slices |
| Data leakage | Inflated model performance | Campaign/time splits, feature timestamp contracts, Sentinel review | Suspicious metric jump or future-derived field |
| Simulator–game mismatch | Misleading recommendations | Declare unsupported mechanics, calibrate, compare distributions, sensitivity analysis | Poor held-out fidelity |
| LLM hallucination | Unsupported advice | Typed tools, evidence bundles, numerical claim verification | Claim absent from artifacts |
| Objective misspecification | Rankings conflict with user intent | Configurable weights, constraints, sensitivity output | Ranking unstable across small weight changes |
| Legal/licensing issue | Cannot distribute data or parser component | Local-first inputs, licence ADR, no game assets, takedown procedure | Unclear redistribution right |
| Scope expansion | No end-to-end release | EU4-only MVP and milestone gates | CK3/FM work begins before Milestone 5 |
| Compute cost | Experiment friction | Classical baselines, sampled scenarios, local-first design | Routine run exceeds agreed budget |

## Security and ethics

- Parse all external files as untrusted input.
- Enforce file-size, path, recursion, and decompression limits.
- Never execute content extracted from a save.
- Prevent path traversal and unsafe deserialization.
- Pin dependencies and run vulnerability checks in CI where practical.
- Keep secrets in environment variables or approved secret stores.
- Redact personal paths and usernames from published manifests.
- Require explicit licences for contributed datasets.
- Prohibit features designed for cheating, anti-cheat bypass, covert telemetry, or unauthorized multiplayer automation.
- Label generated recommendations as model-based decision support, not guaranteed strategies.

## Governance

### Decision records

Significant decisions use lightweight ADR entries in `docs/DECISIONS.md`:

```markdown
## ADR-0001: Decision title

- Status: proposed | accepted | superseded
- Date: YYYY-MM-DD
- Context:
- Decision:
- Alternatives:
- Consequences:
- Revisit when:
```

### Change control

A charter change requires:

1. Proposed edit with rationale.
2. Scope, compatibility, data, and evaluation impact.
3. Updated acceptance criteria if behavior changes.
4. Maintainer approval.
5. Version increment in frontmatter.

### Definition of ready

A development task is ready when it has:

- A user or research outcome.
- Explicit scope and exclusions.
- Inputs, outputs, and interfaces.
- Dependencies and unknowns.
- Test strategy.
- Acceptance criteria.
- Data/licence implications.

### Definition of done

A task is done when:

- Acceptance criteria pass.
- Code is formatted, linted, typed, and tested.
- Documentation and decision records are updated.
- Error paths and edge cases are covered.
- Outputs are reproducible from committed configuration.
- No secret, personal save, protected asset, or unnecessary generated artifact is committed.
- Sentinel review finds no unresolved critical issue.

## Claude Code operating contract

The root `CLAUDE.md` should be concise and point here for product scope. Anthropic’s guidance recommends keeping durable commands, non-obvious conventions, and recurring gotchas in `CLAUDE.md`, while moving path-specific guidance to `.claude/rules/`.[^1]

Create the following root file during Milestone 0:

```markdown
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
```

Personal preferences belong in `CLAUDE.local.md` and should be ignored by Git rather than added to the shared project file.[^1]

## First development order

Claude Code should execute these tasks in sequence and stop at each gate:

1. **Scout:** inspect the repository and report conflicts with this charter.
2. **Plan:** propose Milestone 0 file-by-file, including exact commands and acceptance tests.
3. **Scaffold:** create packaging, source layout, CLI stub, tests, CI, and documentation skeletons.
4. **Verify:** run all quality gates and repair failures without weakening checks.
5. **Schema:** propose the Milestone 1 domain model before writing implementation code.
6. **Implement:** add contracts, fixture adapter, validation, serialization, and tests.
7. **Review:** perform leakage, security, licensing, and architecture-boundary review.
8. **Report:** update `docs/STATUS.md` with completed work, decisions, risks, and the next approved task.

## Initial Claude prompt

Copy this prompt into Claude Code after placing the charter at the repository root:

```text
You are the Commander for Grand Strategy Lab.

Read PROJECT_CHARTER.md completely, then inspect the repository. Do not edit files yet.

Your task is to prepare an implementation-ready plan for Milestone 0 and Milestone 1 only.

Requirements:
- Treat PROJECT_CHARTER.md as the product and architecture authority.
- Identify inconsistencies between the charter and the current repository.
- Propose the smallest end-to-end foundation; do not begin EU4 production parsing, modelling, simulation, or LLM integration.
- List every file to create or change, its responsibility, and important interfaces.
- Define tests and exact commands that prove each acceptance criterion.
- Surface unknowns as explicit questions or time-boxed spikes; do not guess.
- Preserve domain independence from parser vendors, dataframe libraries, and LLM SDKs.
- Include security, licensing, reproducibility, and data-leakage checks.
- Divide work among Commander, Scout, Builder, Analyst, and Sentinel roles where parallel work is safe.
- End with a proposed sequence of small commits.

Wait for approval before modifying the repository.
```

## Obsidian use

Obsidian stores properties as YAML at the top of Markdown files and supports text, dates, checkboxes, numbers, and lists, so the charter’s frontmatter can be filtered and queried inside a vault. Keep this file as `PROJECT_CHARTER.md`; Obsidian can link to it as `[[PROJECT_CHARTER]]` while GitHub and Claude Code read it as normal Markdown.[^9]

Suggested companion notes:

```text
[[Grand Strategy Lab - Dashboard]]
[[Grand Strategy Lab - Architecture]]
[[Grand Strategy Lab - Decisions]]
[[Grand Strategy Lab - Experiment Log]]
[[Grand Strategy Lab - Data Dictionary]]
```

Suggested dashboard query if the Dataview community plugin is installed:

```dataview
TABLE status, version, updated
FROM #project/grand-strategy-lab
SORT updated DESC
```

## Open decisions

The following decisions must be resolved through ADRs rather than assumed:

- Production EU4 parsing strategy and maintenance ownership.
- pandas versus Polars inside feature implementations.
- LightGBM versus XGBoost after a controlled benchmark.
- Exact strategic-distress label and horizon.
- Minimum dataset size and release threshold.
- Local artifact registry versus MLflow after the baseline workflow exists.
- LLM provider and whether an offline/no-LLM mode is mandatory for every interface.
- Public dataset contribution and anonymization protocol.
- Whether a dashboard adds value before the CLI vertical slice is stable.

## Release definition

Version `0.1.0` is releasable when a fresh clone can use redistributable fixtures to:

1. Ingest and validate a canonical EU4-like state.
2. Build leakage-safe features.
3. Run and evaluate at least one calibrated baseline model.
4. Execute seeded counterfactual scenarios for a bounded action set.
5. Rank actions under a configurable objective.
6. Produce an evidence-linked deterministic report.
7. Reproduce the run from a manifest.
8. Pass all engineering, security, documentation, and licence gates.

The agentic natural-language advisor may be included in `0.1.0` only if the deterministic pipeline is complete and all advisor claims remain traceable to validated artifacts. Otherwise, it belongs in `0.2.0`.

---

## References

1. [Best practices for Claude Code - Claude Code Docs](https://code.claude.com/docs/en/best-practices) - Claude Code loads `CLAUDE.md` into every session, which means every line in it takes a little of Cla...

2. [Claude Code by Anthropic | AI Coding Agent, Terminal, IDE](https://claude.com/product/claude-code) - Anthropic's agentic coding tool for developers. Claude Code understands your codebase, edits files, ...

3. [README.md - anthropics/claude-code - GitHub](https://github.com/anthropics/claude-code/blob/main/README.md) - Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and he...

4. [rakaly/eu4save: Library to ergonomically work with EU4 saves ...](https://github.com/rakaly/eu4save) - GitHub - rakaly/eu4save: EU4 Save is a library to ergonomically work with EU4 saves (ironman + mp). ...

5. [rakaly/jomini: Low level, performance oriented parser for save and ...](https://github.com/rakaly/jomini) - A low level, performance oriented parser for save and game files from Paradox Development Studio tit...

6. [Yes, please generate the .md file version](https://www.perplexity.ai/search/c1a8561a-9cd0-4e16-a29f-3821a07c9515) - This document defines an operating system for using Claude in VS Code with maximum efficiency by tre...

7. [Based on the Operating Manual help me create the agents using Claude](https://www.perplexity.ai/search/a994a4cd-7384-4fdb-bce5-12fb83dbcfe5) - Here’s a concrete set of agent definitions you can paste into Claude Code’s “Describe what this agen...

8. [rakaly/cli: Run PDX.Tools commands locally - GitHub](https://github.com/rakaly/cli) - Supports converting (melting) EU4, Rakaly CLI can convert binary encoded saves to their plaintext eq...

9. [Properties - Obsidian Help](https://obsidian.md/help/properties) - Properties allow you to organize information about a note. Properties contain structured data such a...

