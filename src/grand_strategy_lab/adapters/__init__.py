"""Game adapters: source formats → canonical ``GameState``."""

from collections.abc import Callable

from grand_strategy_lab.adapters.base import AdapterResult, GameAdapter
from grand_strategy_lab.adapters.fixture import FIXTURE_RELATION_KINDS, FixtureAdapter

ADAPTERS: dict[str, Callable[[], GameAdapter]] = {"fixture": FixtureAdapter}
"""Registered adapters by ``--game`` name. EU4 is added in Milestone 2."""

__all__ = [
    "ADAPTERS",
    "FIXTURE_RELATION_KINDS",
    "AdapterResult",
    "FixtureAdapter",
    "GameAdapter",
]
