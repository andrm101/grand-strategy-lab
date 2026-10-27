"""Canonical, game-agnostic state model (PROJECT_CHARTER.md § Canonical domain model).

Per-object invariants raise ``PydanticCustomError`` whose type is a stable
``GSL-*`` issue code. Cross-object checks (referential integrity, duplicates,
clock consistency) live in ``grand_strategy_lab.validation``.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue, model_validator
from pydantic_core import PydanticCustomError

from grand_strategy_lab.domain.dates import GameDate
from grand_strategy_lab.domain.primitives import (
    ActorId,
    ConflictId,
    Namespace,
    NonEmptyStr,
    SemVer,
    Sha256Hex,
    Slug,
    TerritoryId,
)

Extensions = dict[Namespace, JsonValue]
SourceKind = Literal["fixture", "save", "export"]


class DomainModel(BaseModel):
    """Base for all canonical models: immutable, strict, closed, finite."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True, allow_inf_nan=False)


class GameMetadata(DomainModel):
    """Provenance and version metadata required on every state."""

    game_id: Slug
    game_version: NonEmptyStr
    schema_version: SemVer
    source_kind: SourceKind
    source_sha256: Sha256Hex
    observed_at_game_time: GameDate
    parsed_at_utc: AwareDatetime
    adapter_name: Slug
    adapter_version: SemVer
    dlc: tuple[NonEmptyStr, ...] = ()
    mods: tuple[NonEmptyStr, ...] = ()


class Actor(DomainModel):
    """A decision-making entity (country, character, club, ...)."""

    id: ActorId
    name: NonEmptyStr
    kind: Slug
    extensions: Extensions = Field(default_factory=dict)


class Territory(DomainModel):
    """A spatial unit with optional owner and controller."""

    id: TerritoryId
    name: NonEmptyStr
    owner: ActorId | None = None
    controller: ActorId | None = None
    extensions: Extensions = Field(default_factory=dict)


class Relation(DomainModel):
    """A typed link between two actors; ``kind`` comes from the adapter vocabulary."""

    kind: Slug
    source: ActorId
    target: ActorId
    directed: bool
    since: GameDate | None = None
    until: GameDate | None = None
    extensions: Extensions = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_invariants(self) -> Relation:
        if self.source == self.target:
            raise PydanticCustomError(
                "GSL-REL-001",
                "relation source and target are the same actor ({actor})",
                {"actor": self.source},
            )
        if self.since is not None and self.until is not None and self.since > self.until:
            raise PydanticCustomError(
                "GSL-DATE-001",
                "start date {start} is after end date {end}",
                {"start": str(self.since), "end": str(self.until)},
            )
        return self


class Conflict(DomainModel):
    """An armed or political conflict between two non-overlapping sides."""

    id: ConflictId
    name: NonEmptyStr
    attackers: Annotated[tuple[ActorId, ...], Field(min_length=1)]
    defenders: Annotated[tuple[ActorId, ...], Field(min_length=1)]
    started: GameDate
    ended: GameDate | None = None
    extensions: Extensions = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_invariants(self) -> Conflict:
        overlap = sorted(set(self.attackers) & set(self.defenders))
        if overlap:
            raise PydanticCustomError(
                "GSL-CON-001",
                "actors appear on both sides of the conflict: {actors}",
                {"actors": ", ".join(overlap)},
            )
        if self.ended is not None and self.started > self.ended:
            raise PydanticCustomError(
                "GSL-DATE-001",
                "start date {start} is after end date {end}",
                {"start": str(self.started), "end": str(self.ended)},
            )
        return self


class ResourcePosition(DomainModel):
    """An actor's holding of one resource, with an explicit unit and optional floor."""

    actor_id: ActorId
    resource: Slug
    amount: float
    unit: NonEmptyStr
    lower_bound: float | None = None

    @model_validator(mode="after")
    def _check_invariants(self) -> ResourcePosition:
        if self.lower_bound is not None and self.amount < self.lower_bound:
            raise PydanticCustomError(
                "GSL-NUM-002",
                "amount {amount} is below lower_bound {lower_bound}",
                {"amount": self.amount, "lower_bound": self.lower_bound},
            )
        return self


class GameState(DomainModel):
    """Snapshot of a game at one in-game instant."""

    metadata: GameMetadata
    clock: GameDate
    actors: dict[ActorId, Actor]
    territories: dict[TerritoryId, Territory] = Field(default_factory=dict)
    relations: tuple[Relation, ...] = ()
    conflicts: tuple[Conflict, ...] = ()
    resources: tuple[ResourcePosition, ...] = ()
    extensions: Extensions = Field(default_factory=dict)


__all__ = [
    "Actor",
    "Conflict",
    "DomainModel",
    "Extensions",
    "GameMetadata",
    "GameState",
    "Relation",
    "ResourcePosition",
    "SourceKind",
    "Territory",
]
