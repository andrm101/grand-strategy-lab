"""Cross-object validation checks on structurally valid states."""

from datetime import UTC, datetime

from grand_strategy_lab.domain import (
    Actor,
    Conflict,
    GameDate,
    GameMetadata,
    GameState,
    Relation,
    ResourcePosition,
    Territory,
)
from grand_strategy_lab.validation import validate_state

CLOCK = GameDate(1444, 11, 11)


def _state(**overrides: object) -> GameState:
    metadata = GameMetadata(
        game_id="test",
        game_version="1",
        schema_version="0.1.0",
        source_kind="fixture",
        source_sha256="0" * 64,
        observed_at_game_time=CLOCK,
        parsed_at_utc=datetime(2026, 1, 1, tzinfo=UTC),
        adapter_name="fixture",
        adapter_version="0.1.0",
    )
    fields: dict[str, object] = {
        "metadata": metadata,
        "clock": CLOCK,
        "actors": {
            "A": Actor(id="A", name="Alpha", kind="country"),
            "B": Actor(id="B", name="Beta", kind="country"),
        },
    }
    fields.update(overrides)
    return GameState.model_validate(fields)


def _codes(state: GameState, kinds: frozenset[str] | None = None) -> list[tuple[str, str]]:
    return [(i.code, i.path) for i in validate_state(state, relation_kinds=kinds).issues]


def test_minimal_state_is_valid() -> None:
    assert validate_state(_state()).ok


def test_dangling_references_reported_with_paths() -> None:
    state = _state(
        relations=(Relation(kind="alliance", source="A", target="Z", directed=False),),
        conflicts=(
            Conflict(id="W", name="War", attackers=("Y",), defenders=("A",), started=CLOCK),
        ),
        territories={"T": Territory(id="T", name="Tee", owner="X")},
        resources=(ResourcePosition(actor_id="Q", resource="gold", amount=1.0, unit="g"),),
    )
    assert _codes(state) == [
        ("GSL-REF-002", "/conflicts/0/attackers/0"),
        ("GSL-REF-001", "/relations/0/target"),
        ("GSL-REF-004", "/resources/0/actor_id"),
        ("GSL-REF-003", "/territories/T/owner"),
    ]


def test_undirected_duplicate_detected_regardless_of_endpoint_order() -> None:
    state = _state(
        relations=(
            Relation(kind="alliance", source="A", target="B", directed=False),
            Relation(kind="alliance", source="B", target="A", directed=False),
        )
    )
    assert _codes(state) == [("GSL-DUP-001", "/relations/0"), ("GSL-DUP-001", "/relations/1")]


def test_directed_reverse_is_not_a_duplicate() -> None:
    state = _state(
        relations=(
            Relation(kind="rivalry", source="A", target="B", directed=True),
            Relation(kind="rivalry", source="B", target="A", directed=True),
        )
    )
    assert validate_state(state).ok


def test_future_information_rejected_but_scheduled_expiry_allowed() -> None:
    future = GameDate(1450, 1, 1)
    state = _state(
        relations=(
            Relation(kind="truce", source="A", target="B", directed=False, until=future),
            Relation(kind="alliance", source="A", target="B", directed=False, since=future),
        ),
        conflicts=(
            Conflict(
                id="W",
                name="War",
                attackers=("A",),
                defenders=("B",),
                started=CLOCK,
                ended=future,
            ),
        ),
    )
    assert _codes(state) == [
        ("GSL-DATE-002", "/conflicts/0/ended"),
        ("GSL-DATE-002", "/relations/1/since"),
    ]


def test_key_id_mismatch_and_clock_mismatch() -> None:
    state = _state(actors={"A": Actor(id="B", name="Beta", kind="country")})
    state = state.model_copy(
        update={
            "metadata": state.metadata.model_copy(
                update={"observed_at_game_time": GameDate(1, 1, 1)}
            )
        }
    )
    assert _codes(state) == [
        ("GSL-KEY-001", "/actors/A"),
        ("GSL-CLK-001", "/metadata/observed_at_game_time"),
    ]


def test_vocabulary_check_is_warning_and_optional() -> None:
    state = _state(relations=(Relation(kind="eu4.march", source="A", target="B", directed=True),))
    report = validate_state(state, relation_kinds=frozenset({"alliance"}))
    assert report.ok
    assert [(i.code, i.severity) for i in report.issues] == [("GSL-VOC-001", "warning")]
    assert validate_state(state).issues == ()


def test_unsupported_schema_version_on_constructed_state() -> None:
    state = _state()
    state = state.model_copy(
        update={"metadata": state.metadata.model_copy(update={"schema_version": "9.0.0"})}
    )
    assert _codes(state) == [("GSL-SCH-001", "/metadata/schema_version")]
