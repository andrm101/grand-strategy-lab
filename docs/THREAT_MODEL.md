# Threat model

Scope: local-first CLI processing user-supplied game files. Source: PROJECT_CHARTER.md § Security and ethics.

| Asset / boundary | Threat | Mitigation | Status |
|---|---|---|---|
| Input files (saves, exports, fixtures) | Malformed, oversized, or decompression-bomb inputs; path traversal | Treat as untrusted; size/recursion/decompression limits; resolve and confine paths | `smoke` validates JSON only; limits due Milestone 2 |
| Parsed content | Embedded text read as instructions by LLM tools (prompt injection) | Content is data; advisor explains only typed tool outputs | Milestone 6 |
| Deserialization | Arbitrary code execution | JSON/Pydantic only; never pickle untrusted input; never execute save content | Enforced by convention |
| Manifests / artifacts | Leaking personal paths, usernames | Redact before publishing; artifacts git-ignored | Milestone 3+ |
| Secrets | Committed `.env` or tokens | `.env` git-ignored; `.env.example` only | Done |
| Dependencies | Supply-chain compromise | Lockfile, `uv sync --locked` in CI; vulnerability scan planned | Partial |
| Repository content | Committing saves or protected assets | `.gitignore` for data zones and save extensions | Done |

Out of scope / prohibited: live-client control, process injection, anti-cheat bypass, multiplayer automation.
