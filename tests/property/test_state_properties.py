"""Property tests: round-trip, referential integrity, and numeric invariants."""

from datetime import UTC, datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from grand_strategy_lab.domain import (
    Actor,
    GameDate,
    GameMetadata,
    GameState,
    Relation,
    ResourcePosition,
    from_json,
    to_json,
)
from grand_strategy_lab.validation import parse_state, validate_state

pytestmark = pytest.mark.property

game_dates = st.builds(
    GameDate,
    year=st.integers(1, 9999),
    month=st.integers(1, 12),
    day=st.integers(1, 31),
)
finite = st.floats(allow_nan=False, allow_infinity=False, width=64)


@st.composite
def valid_states(draw: st.DrawFn) -> GameState:
    clock = draw(st.builds(GameDate, st.integers(2, 9999), st.integers(1, 12), st.integers(1, 31)))
    ids = [f"A{i}" for i in range(draw(st.integers(2, 6)))]
    actors = {i: Actor(id=i, name=f"Actor {i}", kind="country") for i in ids}
    pairs = draw(
        st.lists(
            st.tuples(st.sampled_from(ids), st.sampled_from(ids)).filter(lambda p: p[0] != p[1]),
            max_size=8,
            unique_by=lambda p: tuple(sorted(p)),
        )
    )
    relations = tuple(
        Relation(
            kind=draw(st.sampled_from(["alliance", "rivalry", "truce"])),
            source=a,
            target=b,
            directed=False,
            since=draw(st.none() | st.just(GameDate(clock.year - 1, 1, 1))),
        )
        for a, b in pairs
    )
    resources = tuple(
        ResourcePosition(actor_id=i, resource="treasury", amount=draw(finite), unit="gold")
        for i in draw(st.lists(st.sampled_from(ids), unique=True))
    )
    metadata = GameMetadata(
        game_id="prop",
        game_version="1",
        schema_version="0.1.0",
        source_kind="fixture",
        source_sha256="a" * 64,
        observed_at_game_time=clock,
        parsed_at_utc=datetime(2026, 1, 1, tzinfo=UTC),
        adapter_name="fixture",
        adapter_version="0.1.0",
    )
    return GameState(
        metadata=metadata, clock=clock, actors=actors, relations=relations, resources=resources
    )


@given(valid_states())
def test_valid_states_validate_and_round_trip(state: GameState) -> None:
    assert validate_state(state).ok
    text = to_json(state)
    assert from_json(text) == state
    assert to_json(from_json(text)) == text
    assert parse_state(text.encode()).state == state


@given(valid_states())
def test_dangling_relation_reference_always_detected(state: GameState) -> None:
    relation = Relation(
        kind="alliance", source=next(iter(state.actors)), target="ZZZ", directed=True
    )
    broken = state.model_copy(update={"relations": (*state.relations, relation)})
    index = len(broken.relations) - 1
    issues = [(i.code, i.path) for i in validate_state(broken).issues]
    assert ("GSL-REF-001", f"/relations/{index}/target") in issues


@given(game_dates, game_dates)
def test_relation_date_order_invariant(a: GameDate, b: GameDate) -> None:
    if a <= b:
        Relation(kind="truce", source="X", target="Y", directed=False, since=a, until=b)
    else:
        with pytest.raises(ValidationError) as info:
            Relation(kind="truce", source="X", target="Y", directed=False, since=a, until=b)
        assert [d["type"] for d in info.value.errors()] == ["GSL-DATE-001"]


@given(game_dates, game_dates)
def test_date_order_matches_iso_string_order(a: GameDate, b: GameDate) -> None:
    assert (a < b) == (a.isoformat() < b.isoformat())
    assert GameDate.parse(a.isoformat()) == a


@given(st.sampled_from(["NaN", "Infinity", "-Infinity"]))
def test_non_finite_json_numbers_rejected(token: str) -> None:
    raw = f'{{"actor_id":"A","resource":"gold","amount":{token},"unit":"g"}}'
    with pytest.raises(ValidationError):
        ResourcePosition.model_validate_json(raw)


@given(st.floats(allow_nan=False, allow_infinity=False), finite)
def test_lower_bound_invariant(amount: float, bound: float) -> None:
    def build() -> ResourcePosition:
        return ResourcePosition(
            actor_id="A", resource="gold", amount=amount, unit="g", lower_bound=bound
        )

    if amount >= bound:
        assert build().amount == amount
    else:
        with pytest.raises(ValidationError):
            build()
