# Fixtures

Tiny, hand-authored, redistributable inputs. No game assets, real saves, or decoded token tables.

| File | Purpose |
|---|---|
| `minimal_state.json` | Canonical `GameState` v0.1.0: 3 fictional actors, 3 territories, 2 relations, 1 conflict, 3 resource positions. Stored in canonical form (`to_json` output), so it round-trips byte-identically. |

`metadata.source_sha256` (zeros) and `metadata.parsed_at_utc` (epoch) are placeholders: the
fixture adapter re-stamps them on ingest because the fixture file itself is the source.

Invalid golden cases live in `tests/fixtures/invalid/` and are regenerated with
`uv run python tests/fixtures/make_invalid.py`.
