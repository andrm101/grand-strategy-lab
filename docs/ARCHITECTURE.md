# Architecture

Source of truth: [PROJECT_CHARTER.md § System architecture](../PROJECT_CHARTER.md#system-architecture). This file tracks what is *implemented*; the charter states what is *intended*.


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

## Implementation status

| Component | Package | Status |
|---|---|---|
| CLI | `grand_strategy_lab.cli` | `version`, `smoke`, `ingest`, `validate`, `schema export`; `--game eu4` exits 2 |
| Canonical schema | `grand_strategy_lab.domain` | v0.1.0: `GameState`, `GameMetadata`, `Actor`, `Territory`, `Relation`, `Conflict`, `ResourcePosition`, `GameDate`; canonical JSON (ADR-0004, ADR-0005) |
| Adapters | `grand_strategy_lab.adapters` | `GameAdapter` protocol; `FixtureAdapter`. EU4 in Milestone 2 |
| Validation | `grand_strategy_lab.validation` | Bounded parsing (`InputLimits`), structural and cross-object checks, `ValidationReport` with stable codes ([catalogue](validation-codes.md)) |
| Features, models, simulation, game theory, decision, agents, registry | respective packages | Empty placeholders |

## Ingestion flow

```text
file ─read_bounded (size)─▶ bytes ─json (depth)─▶ schema-version gate
     ─▶ Pydantic (structure, per-object invariants)
     ─▶ validate_state (references, duplicates, clock, future dates, vocabulary)
     ─▶ state only if no error ─▶ adapter re-stamps provenance
```

## Dependency rule

`domain/` must not import pandas, Polars, any parser vendor, or any LLM SDK (charter, Milestone 1).
