"""Cross-object checks on a structurally valid ``GameState``."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterator

from pydantic import JsonValue

from grand_strategy_lab.domain.dates import GAME_DATE_PATTERN, GameDate
from grand_strategy_lab.domain.models import Extensions, GameState, Relation
from grand_strategy_lab.domain.serialization import is_supported_schema_version
from grand_strategy_lab.validation.report import ValidationIssue, ValidationReport, json_pointer

_GAME_DATE_RE = re.compile(GAME_DATE_PATTERN)


def _relation_key(relation: Relation) -> tuple[str, str, str, bool]:
    source, target = relation.source, relation.target
    if not relation.directed:
        source, target = sorted((source, target))
    return relation.kind, source, target, relation.directed


def _future_dates(
    state: GameState, dates: list[tuple[str, GameDate | None]], base: tuple[str | int, ...]
) -> Iterator[ValidationIssue]:
    for field, value in dates:
        if value is not None and value > state.clock:
            yield ValidationIssue.from_code(
                "GSL-DATE-002",
                json_pointer((*base, field)),
                f"{field} {value} is after clock {state.clock}",
            )


def _extension_dates(
    state: GameState, value: JsonValue, path: tuple[str | int, ...]
) -> Iterator[ValidationIssue]:
    """Flag canonical ``YYYY-MM-DD`` strings in extensions that lie after the clock."""
    if isinstance(value, str):
        if _GAME_DATE_RE.fullmatch(value):
            try:
                date = GameDate.parse(value)
            except ValueError:
                return
            if date > state.clock:
                yield ValidationIssue.from_code(
                    "GSL-DATE-002",
                    json_pointer(path),
                    f"extension date {date} is after clock {state.clock}",
                )
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _extension_dates(state, child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _extension_dates(state, child, (*path, index))


def _all_extension_dates(state: GameState) -> Iterator[ValidationIssue]:
    owners: list[tuple[tuple[str | int, ...], Extensions]] = [(("extensions",), state.extensions)]
    owners += [(("actors", key, "extensions"), a.extensions) for key, a in state.actors.items()]
    owners += [
        (("territories", key, "extensions"), t.extensions) for key, t in state.territories.items()
    ]
    owners += [
        (("relations", i, "extensions"), r.extensions) for i, r in enumerate(state.relations)
    ]
    owners += [
        (("conflicts", i, "extensions"), c.extensions) for i, c in enumerate(state.conflicts)
    ]
    for base, extensions in owners:
        for namespace, value in extensions.items():
            yield from _extension_dates(state, value, (*base, namespace))


def _iter_issues(
    state: GameState, relation_kinds: frozenset[str] | None
) -> Iterator[ValidationIssue]:
    yield from _all_extension_dates(state)
    meta = state.metadata
    if not is_supported_schema_version(meta.schema_version):
        yield ValidationIssue.from_code(
            "GSL-SCH-001",
            "/metadata/schema_version",
            f"schema version {meta.schema_version} is not supported",
        )
    if meta.observed_at_game_time != state.clock:
        yield ValidationIssue.from_code(
            "GSL-CLK-001",
            "/metadata/observed_at_game_time",
            f"observed_at_game_time {meta.observed_at_game_time} != clock {state.clock}",
        )

    for key, actor in state.actors.items():
        if key != actor.id:
            yield ValidationIssue.from_code(
                "GSL-KEY-001", json_pointer(("actors", key)), f"key {key!r} != id {actor.id!r}"
            )
    for key, territory in state.territories.items():
        if key != territory.id:
            yield ValidationIssue.from_code(
                "GSL-KEY-001",
                json_pointer(("territories", key)),
                f"key {key!r} != id {territory.id!r}",
            )
        for field in ("owner", "controller"):
            ref = getattr(territory, field)
            if ref is not None and ref not in state.actors:
                yield ValidationIssue.from_code(
                    "GSL-REF-003",
                    json_pointer(("territories", key, field)),
                    f"unknown actor {ref!r}",
                )

    relation_counts = Counter(_relation_key(relation) for relation in state.relations)
    for index, relation in enumerate(state.relations):
        for field in ("source", "target"):
            ref = getattr(relation, field)
            if ref not in state.actors:
                yield ValidationIssue.from_code(
                    "GSL-REF-001",
                    json_pointer(("relations", index, field)),
                    f"unknown actor {ref!r}",
                )
        if relation_counts[_relation_key(relation)] > 1:
            yield ValidationIssue.from_code(
                "GSL-DUP-001",
                json_pointer(("relations", index)),
                f"duplicate {relation.kind} relation {relation.source}-{relation.target}",
            )
        if relation_kinds is not None and relation.kind not in relation_kinds:
            yield ValidationIssue.from_code(
                "GSL-VOC-001",
                json_pointer(("relations", index, "kind")),
                f"relation kind {relation.kind!r} is not in the adapter vocabulary",
            )
        yield from _future_dates(state, [("since", relation.since)], ("relations", index))

    conflict_counts = Counter(conflict.id for conflict in state.conflicts)
    for index, conflict in enumerate(state.conflicts):
        if conflict_counts[conflict.id] > 1:
            yield ValidationIssue.from_code(
                "GSL-DUP-002",
                json_pointer(("conflicts", index, "id")),
                f"duplicate conflict id {conflict.id!r}",
            )
        for side in ("attackers", "defenders"):
            for position, ref in enumerate(getattr(conflict, side)):
                if ref not in state.actors:
                    yield ValidationIssue.from_code(
                        "GSL-REF-002",
                        json_pointer(("conflicts", index, side, position)),
                        f"unknown actor {ref!r}",
                    )
        yield from _future_dates(
            state, [("started", conflict.started), ("ended", conflict.ended)], ("conflicts", index)
        )

    resource_counts = Counter((item.actor_id, item.resource) for item in state.resources)
    for index, item in enumerate(state.resources):
        if item.actor_id not in state.actors:
            yield ValidationIssue.from_code(
                "GSL-REF-004",
                json_pointer(("resources", index, "actor_id")),
                f"unknown actor {item.actor_id!r}",
            )
        if resource_counts[(item.actor_id, item.resource)] > 1:
            yield ValidationIssue.from_code(
                "GSL-DUP-003",
                json_pointer(("resources", index)),
                f"duplicate position {item.actor_id}/{item.resource}",
            )


def validate_state(
    state: GameState, *, relation_kinds: frozenset[str] | None = None
) -> ValidationReport:
    """Run all cross-object checks.

    ``relation_kinds`` is the adapter's declared vocabulary; ``None`` skips the
    vocabulary check. ``Relation.until`` is not checked against the clock because
    a snapshot may record scheduled expiries (e.g. truces); every other date
    after the clock is future information and is rejected (GSL-DATE-002). That
    includes canonical ``YYYY-MM-DD`` strings anywhere inside ``extensions``;
    adapters must model scheduled future dates as typed fields, not extensions.
    """
    return ValidationReport.from_issues(_iter_issues(state, relation_kinds))
