# Status

Updated: 2026-10-27

## Current milestone

**Milestone 1 — Canonical schema** (implemented; Step 7 review fixes F1–F15 applied, re-review pending).

## Completed

- **Milestone 0**: repository foundation; CI green on Python 3.12/3.13 × Ubuntu/Windows
  ([run 40542874745](https://github.com/andrm101/grand-strategy-lab/actions/runs/40542874745)).
- **Milestone 1**: canonical schema v0.1.0, fixture adapter, bounded parsing, validation reports
  with 26 stable codes, canonical JSON, committed JSON Schema, CLI `ingest` / `validate` /
  `schema export`.
- Step 7 review fixes: raw-input scan (duplicate keys, NaN/Infinity, oversized integers), capped
  reads, no input overwrite, exit 3 on write errors, terminal escaping, future dates inside
  extensions, ASCII-only patterns, validated provenance re-stamp, `GSL-CON-002`.
- ADR-0001 to ADR-0006.

## Next

1. Step 7: Sentinel review (leakage, security, licensing, architecture boundaries).
2. Step 8: report and update this file.
3. Milestone 2: EU4 ingestion spike (parser ADR; local saves only).

## Open risks / unknowns

- Calendar validity (e.g. 30 February) is not checked in the domain; EU4 calendar rules arrive with the adapter.
- `FIXTURE_RELATION_KINDS` is a test vocabulary, not an EU4 mapping.
- Charter open decisions (parser strategy, pandas vs Polars, label definition, LLM provider, …) remain unresolved by design.
- The charter's Analyst role has no matching agent definition; not needed before Milestone 3.
