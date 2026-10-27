"""Regenerate golden invalid fixtures from the canonical valid fixture.

Each case is (mutation, expected issues). Expectations are authored here by hand
from the specification, never captured from implementation output.

Run: ``uv run python tests/fixtures/make_invalid.py``
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "data" / "fixtures" / "minimal_state.json"
OUT = ROOT / "tests" / "fixtures" / "invalid"

Doc = dict[str, Any]
Expected = list[tuple[str, str]]


def _set(path: list[str | int], value: Any) -> Callable[[Doc], Doc]:
    def mutate(doc: Doc) -> Doc:
        node: Any = doc
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        return doc

    return mutate


def _delete(path: list[str | int]) -> Callable[[Doc], Doc]:
    def mutate(doc: Doc) -> Doc:
        node: Any = doc
        for key in path[:-1]:
            node = node[key]
        del node[path[-1]]
        return doc

    return mutate


def _duplicate_reversed_alliance(doc: Doc) -> Doc:
    first = copy.deepcopy(doc["relations"][0])
    first["source"], first["target"] = first["target"], first["source"]
    doc["relations"].append(first)
    return doc


def _duplicate(path: list[str | int], index: int) -> Callable[[Doc], Doc]:
    def mutate(doc: Doc) -> Doc:
        node: Any = doc
        for key in path:
            node = node[key]
        node.append(copy.deepcopy(node[index]))
        return doc

    return mutate


@dataclass(frozen=True)
class RawText:
    """A mutation of the valid fixture's text (for inputs ``json.dumps`` cannot emit)."""

    transform: Callable[[str], str]


Mutation = Callable[[Doc], Doc] | RawText | str

CASES: dict[str, tuple[Mutation, bool, Expected]] = {
    "missing_metadata_field": (
        _delete(["metadata", "game_id"]),
        False,
        [("GSL-STR-001", "/metadata/game_id")],
    ),
    "unknown_field": (
        _set(["actors", "AAA", "population"], 1),
        False,
        [("GSL-STR-002", "/actors/AAA/population")],
    ),
    "string_number": (
        _set(["resources", 0, "amount"], "120.5"),
        False,
        [("GSL-STR-003", "/resources/0/amount")],
    ),
    "nan_amount": (
        _set(["resources", 0, "amount"], float("nan")),
        False,
        [("GSL-NUM-001", "/resources/0/amount")],
    ),
    "below_lower_bound": (
        _set(["resources", 1, "amount"], -1.0),
        False,
        [("GSL-NUM-002", "/resources/1")],
    ),
    "invalid_month": (_set(["clock"], "1444-13-01"), False, [("GSL-STR-003", "/clock")]),
    "self_relation": (
        _set(["relations", 0, "target"], "AAA"),
        False,
        [("GSL-REL-001", "/relations/0")],
    ),
    "reversed_relation_dates": (
        _set(["relations", 0, "until"], "1430-01-01"),
        False,
        [("GSL-DATE-001", "/relations/0")],
    ),
    "conflict_sides_overlap": (
        _set(["conflicts", 0, "defenders"], ["BBB", "CCC"]),
        False,
        [("GSL-CON-001", "/conflicts/0")],
    ),
    "dangling_relation_source": (
        _set(["relations", 1, "source"], "ZZZ"),
        False,
        [("GSL-REF-001", "/relations/1/source")],
    ),
    "dangling_territory_owner": (
        _set(["territories", "T001", "owner"], "ZZZ"),
        False,
        [("GSL-REF-003", "/territories/T001/owner")],
    ),
    "clock_mismatch": (
        _set(["metadata", "observed_at_game_time"], "1445-01-01"),
        False,
        [("GSL-CLK-001", "/metadata/observed_at_game_time")],
    ),
    "future_relation_start": (
        _set(["relations", 0, "since"], "1450-01-01"),
        False,
        [("GSL-DATE-002", "/relations/0/since")],
    ),
    "actor_key_mismatch": (
        _set(["actors", "AAA", "id"], "AAX"),
        False,
        [("GSL-KEY-001", "/actors/AAA")],
    ),
    "duplicate_undirected_relation": (
        _duplicate_reversed_alliance,
        False,
        [("GSL-DUP-001", "/relations/0"), ("GSL-DUP-001", "/relations/2")],
    ),
    "unsupported_schema_version": (
        _set(["metadata", "schema_version"], "0.2.0"),
        False,
        [("GSL-SCH-001", "/metadata/schema_version")],
    ),
    "unknown_relation_kind_warning": (
        _set(["relations", 0, "kind"], "personal_union"),
        True,
        [("GSL-VOC-001", "/relations/0/kind")],
    ),
    "not_json": ("{not json\n", False, [("GSL-IO-003", "")]),
    "missing_metadata": (_delete(["metadata"]), False, [("GSL-STR-001", "/metadata")]),
    "nan_in_extensions": (
        _set(["extensions", "fixture", "weight"], float("nan")),
        False,
        [("GSL-NUM-001", "/extensions/fixture/weight")],
    ),
    "duplicate_json_key": (
        RawText(lambda text: text.replace('"name": "Avaria"', '"name": "Avaria", "name": "X"', 1)),
        False,
        [("GSL-IO-005", "/actors/AAA/name")],
    ),
    "duplicate_actor_on_conflict_side": (
        _set(["conflicts", 0, "attackers"], ["CCC", "CCC"]),
        False,
        [("GSL-CON-002", "/conflicts/0")],
    ),
    "future_extension_date": (
        _set(["actors", "BBB", "extensions"], {"eu4": {"next_election": "1450-01-01"}}),
        False,
        [("GSL-DATE-002", "/actors/BBB/extensions/eu4/next_election")],
    ),
    "duplicate_conflict_id": (
        _duplicate(["conflicts"], 0),
        False,
        [("GSL-DUP-002", "/conflicts/0/id"), ("GSL-DUP-002", "/conflicts/1/id")],
    ),
    "duplicate_resource_position": (
        _duplicate(["resources"], 0),
        False,
        [("GSL-DUP-003", "/resources/0"), ("GSL-DUP-003", "/resources/3")],
    ),
}


def main() -> None:
    """Write ``<case>.json`` and ``<case>.expected.json`` for every case."""
    OUT.mkdir(parents=True, exist_ok=True)
    valid: Doc = json.loads(VALID.read_text(encoding="utf-8"))
    for name, (mutation, ok, expected) in CASES.items():
        if isinstance(mutation, str):
            text = mutation
        elif isinstance(mutation, RawText):
            text = mutation.transform(VALID.read_text(encoding="utf-8"))
        else:
            text = json.dumps(mutation(copy.deepcopy(valid)), indent=2, sort_keys=True) + "\n"
        (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
        golden = {"ok": ok, "issues": [{"code": c, "path": p} for c, p in expected]}
        (OUT / f"{name}.expected.json").write_text(
            json.dumps(golden, indent=2) + "\n", encoding="utf-8", newline="\n"
        )


if __name__ == "__main__":
    main()
