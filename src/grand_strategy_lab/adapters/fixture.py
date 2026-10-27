"""Adapter for hand-authored canonical-JSON fixtures."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from grand_strategy_lab.adapters.base import AdapterResult
from grand_strategy_lab.domain.models import GameMetadata
from grand_strategy_lab.validation.parse import InputLimits, ParseResult, parse_state, read_bounded

FIXTURE_RELATION_KINDS = frozenset({"alliance", "guarantee", "rivalry", "subject", "truce"})
"""Vocabulary for synthetic fixtures only; real games declare their own (Milestone 2+)."""


def _utc_now() -> datetime:
    return datetime.now(UTC)


class FixtureAdapter:
    """Load a canonical ``GameState`` JSON file and re-stamp its provenance.

    The fixture file is the new source, so ``source_sha256``, ``parsed_at_utc``,
    ``adapter_name``, and ``adapter_version`` are overwritten; all other content
    is preserved exactly.
    """

    name = "fixture"
    version = "0.1.0"
    relation_kinds: frozenset[str] | None = FIXTURE_RELATION_KINDS

    def __init__(self, now: Callable[[], datetime] = _utc_now) -> None:
        self._now = now

    def load(self, source: Path, *, limits: InputLimits | None = None) -> AdapterResult:
        """Read, hash, parse, validate, and re-stamp a fixture file."""
        limits = limits or InputLimits()
        raw = read_bounded(source, limits)
        if isinstance(raw, ParseResult):
            return raw
        result = parse_state(raw, limits=limits, relation_kinds=self.relation_kinds)
        if result.state is None:
            return result
        # Re-validate rather than model_copy: an injected clock returning a naive
        # datetime must fail here, not produce a state that cannot be re-read.
        metadata = GameMetadata.model_validate(
            {
                **dict(result.state.metadata),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "parsed_at_utc": self._now(),
                "adapter_name": self.name,
                "adapter_version": self.version,
            }
        )
        return ParseResult(
            state=result.state.model_copy(update={"metadata": metadata}), report=result.report
        )
