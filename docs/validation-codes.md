# Validation issue codes

Stable, append-only catalogue (source: `src/grand_strategy_lab/validation/codes.py`).
A published code never changes meaning; retired codes are marked, not reused.

Every issue carries `severity`, `code`, `path` (RFC 6901 JSON pointer; empty = whole document),
`message`, and `remediation`. Reports sort issues by `(path, code, message)`.

CLI exit codes: `0` valid · `1` validation errors · `2` not implemented · `3` unreadable/invalid input (`GSL-IO-*`, unknown game).

| Code | Severity | Meaning | Remediation |
|---|---|---|---|
| `GSL-IO-001` | error | Input file missing or unreadable | Check the path and permissions; inputs must be readable regular files. |
| `GSL-IO-002` | error | Input file exceeds size limit | Use a smaller input or raise InputLimits.max_bytes deliberately. |
| `GSL-IO-003` | error | Input is not valid UTF-8 JSON | Fix the JSON syntax or encoding. |
| `GSL-IO-004` | error | JSON nesting exceeds depth limit | Flatten the document or raise InputLimits.max_depth deliberately. |
| `GSL-IO-005` | error | Duplicate JSON object key | Remove the repeated key; duplicates would silently overwrite earlier values. |
| `GSL-SCH-001` | error | Unsupported or missing schema version | Re-export the state with this release's schema version (see ADR-0005). |
| `GSL-STR-001` | error | Required field missing | Add the field. |
| `GSL-STR-002` | error | Unknown field | Remove the field or move game-specific data under an extensions namespace. |
| `GSL-STR-003` | error | Invalid value or type | Provide a value of the documented type and format; values are never coerced. |
| `GSL-NUM-001` | error | Non-finite number | Replace NaN/Infinity with a finite value. |
| `GSL-NUM-002` | error | Amount below declared lower bound | Correct the amount or its lower_bound. |
| `GSL-REL-001` | error | Self-relation | A relation must connect two different actors. |
| `GSL-CON-001` | error | Actor on both sides of a conflict | Place each actor on exactly one side. |
| `GSL-CON-002` | error | Actor listed twice on one side of a conflict | List each participant once per side. |
| `GSL-DATE-001` | error | Start date after end date | Swap or correct the dates. |
| `GSL-DATE-002` | error | Date after the state's clock | A snapshot cannot contain future events; correct the date or the clock. |
| `GSL-CLK-001` | error | Metadata time differs from clock | Set metadata.observed_at_game_time equal to clock. |
| `GSL-KEY-001` | error | Mapping key differs from object id | Key each object by its own id. |
| `GSL-REF-001` | error | Relation references unknown actor | Add the actor or fix the reference. |
| `GSL-REF-002` | error | Conflict references unknown actor | Add the actor or fix the reference. |
| `GSL-REF-003` | error | Territory references unknown actor | Add the actor or fix the reference. |
| `GSL-REF-004` | error | Resource references unknown actor | Add the actor or fix the reference. |
| `GSL-DUP-001` | error | Duplicate relation | Keep one relation per (kind, endpoints, direction). |
| `GSL-DUP-002` | error | Duplicate conflict id | Give each conflict a unique id. |
| `GSL-DUP-003` | error | Duplicate resource position | Keep one position per (actor, resource). |
| `GSL-VOC-001` | warning | Relation kind not in adapter vocabulary | Use a declared kind, or extend the adapter vocabulary via an ADR. |

Pydantic error types map to: `missing` → `GSL-STR-001`, `extra_forbidden` → `GSL-STR-002`,
`finite_number` → `GSL-NUM-001`, any other → `GSL-STR-003`. Domain invariants raise their `GSL-*` code directly.
