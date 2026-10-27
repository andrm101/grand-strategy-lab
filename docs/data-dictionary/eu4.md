# EU4 data dictionary

Maps EU4 save fields to the canonical schema (v0.1.0) and the `eu4` extension namespace.

**No field is listed until verified against a real local save in Milestone 2.** The sections below
follow the charter's minimum viable scope; they are placeholders, not claims about the save format.

Column definitions:

- **Canonical path**: JSON pointer in `GameState`, or `/…/extensions/eu4/<field>`.
- **Type / unit**: Python type and game or physical unit.
- **Temporal meaning**: stock at `clock`, flow per month, event date, etc.
- **Missing-value policy**: reject (`GSL-*` code), `null` with reason code, or documented default.
- **Source mapping**: save-file key path and parser (ADR reference).
- **Verified**: save and patch on which the mapping was checked.

## Country (actors)

| Canonical path | Type / unit | Temporal meaning | Missing-value policy | Source mapping | Verified |
|---|---|---|---|---|---|

## Diplomacy (relations)

| Canonical path | Type / unit | Temporal meaning | Missing-value policy | Source mapping | Verified |
|---|---|---|---|---|---|

## Economy (resources)

| Canonical path | Type / unit | Temporal meaning | Missing-value policy | Source mapping | Verified |
|---|---|---|---|---|---|

## Military (resources and extensions)

| Canonical path | Type / unit | Temporal meaning | Missing-value policy | Source mapping | Verified |
|---|---|---|---|---|---|

## Wars (conflicts)

| Canonical path | Type / unit | Temporal meaning | Missing-value policy | Source mapping | Verified |
|---|---|---|---|---|---|
