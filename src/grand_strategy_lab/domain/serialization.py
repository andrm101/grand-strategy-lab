"""Canonical JSON serialization and schema-version policy (ADR-0005)."""

from __future__ import annotations

import json
import re
from typing import Any

from grand_strategy_lab.domain.models import GameState
from grand_strategy_lab.domain.primitives import SEMVER_PATTERN

SCHEMA_VERSION = "0.1.0"
_SEMVER_RE = re.compile(SEMVER_PATTERN)


def _parse_semver(version: str) -> tuple[int, int, int] | None:
    match = _SEMVER_RE.fullmatch(version)
    if match is None:
        return None
    major, minor, patch = (int(group) for group in match.groups())
    return major, minor, patch


def is_supported_schema_version(version: str) -> bool:
    """Return whether ``version`` can be read by this release.

    Pre-1.0, a minor bump is breaking, so ``MAJOR.MINOR`` must match exactly;
    from 1.0, only ``MAJOR`` must match. Patch versions never break readers.
    """
    parsed = _parse_semver(version)
    current = _parse_semver(SCHEMA_VERSION)
    if parsed is None or current is None:
        return False
    if current[0] == 0:
        return parsed[:2] == current[:2]
    return parsed[0] == current[0]


def to_canonical_json(data: Any) -> str:
    """Serialize JSON-compatible ``data`` deterministically (sorted keys, LF, trailing newline)."""
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def to_json(state: GameState) -> str:
    """Serialize a state to canonical JSON text."""
    return to_canonical_json(state.model_dump(mode="json"))


def from_json(text: str | bytes) -> GameState:
    """Parse canonical JSON text into a state; raises ``pydantic.ValidationError`` on failure."""
    return GameState.model_validate_json(text)


def game_state_json_schema() -> dict[str, Any]:
    """Return the JSON Schema of ``GameState`` (validation mode)."""
    return GameState.model_json_schema()
