"""Adapter contract: map a source format into a validated canonical ``GameState``."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from grand_strategy_lab.validation.parse import InputLimits, ParseResult

AdapterResult = ParseResult
"""``state`` is ``None`` whenever ``report`` contains an error."""


class GameAdapter(Protocol):
    """A source-format reader for one game.

    Adapters must never rank actions, never infer missing critical values
    silently, and never return a state when any error-level issue exists.
    """

    @property
    def name(self) -> str:
        """Adapter slug recorded in ``GameMetadata.adapter_name``."""
        ...

    @property
    def version(self) -> str:
        """Adapter semantic version recorded in ``GameMetadata.adapter_version``."""
        ...

    @property
    def relation_kinds(self) -> frozenset[str] | None:
        """Declared relation vocabulary; ``None`` disables the vocabulary check."""
        ...

    def load(self, source: Path, *, limits: InputLimits | None = None) -> AdapterResult:
        """Read ``source`` and return a validated state or a failing report."""
        ...
