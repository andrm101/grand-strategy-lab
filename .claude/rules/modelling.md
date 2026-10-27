---
paths:
  - "src/grand_strategy_lab/models/**"
  - "src/grand_strategy_lab/features/**"
  - "configs/experiments/**"
---
# Modelling rules (PROJECT_CHARTER.md § Modelling strategy)

- Climb the baseline ladder in order: naive priors → linear → trees → temporal → graph → RL (reduced simulator only).
- Split by `campaign_id` first, then order by `observed_at_game_time`; fit encoders/imputers on training data only.
- Features must be point-in-time safe; no future-derived fields at inference.
- Primary metric is predeclared (Brier score for `strategic_distress`); thresholds are never chosen after viewing test results.
- Every model ships with config + data/feature hashes, baseline comparison, calibration, slice analysis, and a model card.
- Report associations as associations; no causal claims from observational saves.
