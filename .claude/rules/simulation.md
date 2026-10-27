---
paths:
  - "src/grand_strategy_lab/simulation/**"
  - "src/grand_strategy_lab/game_theory/**"
  - "src/grand_strategy_lab/decision/**"
  - "configs/scenarios/**"
---
# Simulation rules (PROJECT_CHARTER.md § Simulation strategy, § Game-theory layer)

- The simulator is a reduced decision environment, not an EU4 emulator.
- Transitions are pure where practical; pass a seeded RNG explicitly; no hidden global state.
- Encode units and bounds in types/validators; test invariants with Hypothesis.
- Declare unsupported mechanics and parameter assumptions in every scenario output.
- Strategic models must state players, actions, information, payoffs, timing, solution concept, parameter source, sensitivity, and validity limits.
- Never use an LLM to compute state transitions or numeric results.
