"""Per-object invariants and strictness of the canonical models."""

import json
from typing import Any

import pytest
from pydantic import ValidationError

from grand_strategy_lab.domain import Conflict, GameDate, Relation, ResourcePosition


def _error_types(exc: ValidationError) -> list[str]:
    return [detail["type"] for detail in exc.errors()]


def test_self_relation_rejected() -> None:
    with pytest.raises(ValidationError) as info:
        Relation(kind="alliance", source="AAA", target="AAA", directed=False)
    assert _error_types(info.value) == ["GSL-REL-001"]


def test_relation_dates_must_be_ordered() -> None:
    with pytest.raises(ValidationError) as info:
        Relation(
            kind="truce",
            source="AAA",
            target="BBB",
            directed=False,
            since=GameDate(1444, 1, 2),
            until=GameDate(1444, 1, 1),
        )
    assert _error_types(info.value) == ["GSL-DATE-001"]


def test_conflict_sides_must_be_disjoint() -> None:
    with pytest.raises(ValidationError) as info:
        Conflict(
            id="W1",
            name="War",
            attackers=("AAA", "BBB"),
            defenders=("BBB",),
            started=GameDate(1444, 1, 1),
        )
    assert _error_types(info.value) == ["GSL-CON-001"]


def test_conflict_sides_must_be_non_empty() -> None:
    with pytest.raises(ValidationError):
        Conflict(id="W1", name="War", attackers=(), defenders=("BBB",), started=GameDate(1, 1, 1))


def test_resource_lower_bound_enforced_but_negative_allowed_without_bound() -> None:
    assert (
        ResourcePosition(actor_id="A", resource="treasury", amount=-5.0, unit="gold").amount == -5
    )
    with pytest.raises(ValidationError) as info:
        ResourcePosition(actor_id="A", resource="men", amount=-1.0, unit="men", lower_bound=0.0)
    assert _error_types(info.value) == ["GSL-NUM-002"]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_amount_rejected(value: float) -> None:
    with pytest.raises(ValidationError) as info:
        ResourcePosition(actor_id="A", resource="treasury", amount=value, unit="gold")
    assert _error_types(info.value) == ["finite_number"]


@pytest.mark.parametrize(
    ("field", "value"),
    [("amount", "120.5"), ("unit", 5), ("actor_id", "has space"), ("resource", "Treasury")],
)
def test_no_silent_coercion_from_json(field: str, value: Any) -> None:
    doc: dict[str, Any] = {"actor_id": "A", "resource": "treasury", "amount": 1.0, "unit": "gold"}
    doc[field] = value
    with pytest.raises(ValidationError):
        ResourcePosition.model_validate_json(json.dumps(doc))


def test_models_are_immutable() -> None:
    relation = Relation(kind="alliance", source="AAA", target="BBB", directed=False)
    with pytest.raises(ValidationError):
        relation.kind = "rivalry"  # type: ignore[misc]


def test_unknown_fields_rejected() -> None:
    with pytest.raises(ValidationError) as info:
        Relation.model_validate(
            {"kind": "alliance", "source": "A", "target": "B", "directed": False, "x": 1}
        )
    assert _error_types(info.value) == ["extra_forbidden"]


def test_actor_listed_twice_on_one_side_rejected() -> None:
    with pytest.raises(ValidationError) as info:
        Conflict(
            id="W1",
            name="War",
            attackers=("CCC", "CCC"),
            defenders=("AAA",),
            started=GameDate(1444, 1, 1),
        )
    assert _error_types(info.value) == ["GSL-CON-002"]


@pytest.mark.parametrize("text", ["１４４４-01-01", "1444-٠١-01"])
def test_non_ascii_digits_rejected_in_dates(text: str) -> None:
    with pytest.raises(ValueError):
        GameDate.parse(text)
    with pytest.raises(ValidationError):
        Relation.model_validate_json(
            json.dumps(
                {"kind": "truce", "source": "A", "target": "B", "directed": False, "since": text}
            )
        )
