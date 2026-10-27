# Threat model

Scope: local-first CLI processing user-supplied game files. Source: PROJECT_CHARTER.md § Security and ethics.

| Asset / boundary | Threat | Mitigation | Status |
|---|---|---|---|
| Input files (saves, exports, fixtures) | Malformed or oversized inputs; deep nesting; growth after a size check | Regular-file check; read capped at `InputLimits.max_bytes` (10 MiB); depth limit 64; invalid UTF-8/JSON and oversized integer literals → `GSL-IO-003` | Done (Milestone 1) |
| Input files | Ambiguous JSON: duplicate keys, NaN/Infinity | Raw-document scan rejects both with JSON pointers (`GSL-IO-005`, `GSL-NUM-001`) before model validation | Done (Milestone 1) |
| Input files | Decompression bombs in compressed saves | Decompression limits | Milestone 2 (no compressed formats yet) |
| File paths | Path traversal | **Not confined by design**: a local CLI acts on paths the user chooses. Inputs are read-only; `ingest` refuses an output path that is the same file as the input | Accepted risk; revisit if paths ever come from untrusted sources (API, advisor) |
| Raw inputs | Accidental overwrite | `ingest --output` must differ from `--input` (`samefile` check); write errors exit 3 without partial tracebacks | Done (Milestone 1) |
| Terminal | Escape-sequence injection via untrusted keys or values in reports | Text reports escape non-printable characters; JSON reports are escaped by the encoder | Done (Milestone 1) |
| Parsed content | Embedded text read as instructions by LLM tools (prompt injection) | Content is data; advisor explains only typed tool outputs | Milestone 6 |
| Deserialization | Arbitrary code execution | JSON/Pydantic only; never pickle untrusted input; never execute save content | Enforced by convention |
| Manifests / artifacts | Leaking personal paths, usernames | Redact before publishing; artifacts git-ignored | Milestone 3+ |
| Secrets | Committed `.env` or tokens | `.env` git-ignored; `.env.example` only | Done |
| Dependencies | Supply-chain compromise | Lockfile, `uv sync --locked` in CI; runtime inventory in ADR-0006; `setup-uv` pinned to an exact tag (`checkout` on its major tag); vulnerability scan planned | Partial |
| Repository content | Committing saves or protected assets | `.gitignore` for data zones and save extensions | Done |

Out of scope / prohibited: live-client control, process injection, anti-cheat bypass, multiplayer automation.
