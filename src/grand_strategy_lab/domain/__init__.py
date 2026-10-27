"""Canonical, game-agnostic domain model.

Depends only on the standard library and ``pydantic`` (ADR-0004); never on
dataframe libraries, parser vendors, or LLM SDKs.
"""

from grand_strategy_lab.domain.dates import GameDate
from grand_strategy_lab.domain.models import (
    Actor,
    Conflict,
    GameMetadata,
    GameState,
    Relation,
    ResourcePosition,
    Territory,
)
from grand_strategy_lab.domain.serialization import (
    SCHEMA_VERSION,
    from_json,
    game_state_json_schema,
    is_supported_schema_version,
    to_json,
)

__all__ = [
    "SCHEMA_VERSION",
    "Actor",
    "Conflict",
    "GameDate",
    "GameMetadata",
    "GameState",
    "Relation",
    "ResourcePosition",
    "Territory",
    "from_json",
    "game_state_json_schema",
    "is_supported_schema_version",
    "to_json",
]
