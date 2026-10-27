"""Bounded parsing of untrusted input."""

import json
from pathlib import Path
from typing import Any

from grand_strategy_lab.validation import (
    InputLimits,
    ParseResult,
    json_pointer,
    parse_state,
    read_bounded,
)


def _codes(raw: bytes, **kwargs: Any) -> list[str]:
    return [issue.code for issue in parse_state(raw, **kwargs).report.issues]


def test_valid_document_returns_state(valid_doc: dict[str, Any]) -> None:
    result = parse_state(json.dumps(valid_doc).encode())
    assert result.state is not None
    assert result.report.ok


def test_size_limit_checked_before_parsing() -> None:
    assert _codes(b"{}" * 10, limits=InputLimits(max_bytes=5)) == ["GSL-IO-002"]


def test_invalid_utf8_and_json() -> None:
    assert _codes(b"\xff\xfe") == ["GSL-IO-003"]
    assert _codes(b"{not json") == ["GSL-IO-003"]


def test_depth_limit(valid_doc: dict[str, Any]) -> None:
    assert _codes(json.dumps(valid_doc).encode(), limits=InputLimits(max_depth=3)) == ["GSL-IO-004"]
    deep = b"[" * 5000 + b"]" * 5000
    assert _codes(deep) == ["GSL-IO-004"]


def test_schema_version_checked_before_structure(valid_doc: dict[str, Any]) -> None:
    valid_doc["metadata"]["schema_version"] = "0.2.0"
    valid_doc["unexpected"] = True
    assert _codes(json.dumps(valid_doc).encode()) == ["GSL-SCH-001"]


def test_missing_metadata_is_structural_not_version_error(valid_doc: dict[str, Any]) -> None:
    del valid_doc["metadata"]
    result = parse_state(json.dumps(valid_doc).encode())
    assert [(i.code, i.path) for i in result.report.issues] == [("GSL-STR-001", "/metadata")]
    assert _codes(b"[]") == ["GSL-STR-003"]


def test_non_finite_numbers_rejected_anywhere_with_path(valid_doc: dict[str, Any]) -> None:
    valid_doc["extensions"]["fixture"]["weights"] = [1.0, float("inf")]
    valid_doc["actors"]["AAA"]["extensions"]["eu4"] = {"x": float("nan")}
    result = parse_state(json.dumps(valid_doc).encode())
    assert result.state is None
    assert [(i.code, i.path) for i in result.report.issues] == [
        ("GSL-NUM-001", "/actors/AAA/extensions/eu4/x"),
        ("GSL-NUM-001", "/extensions/fixture/weights/1"),
    ]


def test_duplicate_keys_rejected_with_path() -> None:
    raw = b'{"a": {"k": 1, "k": 2}, "metadata": 1, "metadata": 2}'
    assert [(i.code, i.path) for i in parse_state(raw).report.issues] == [
        ("GSL-IO-005", "/a/k"),
        ("GSL-IO-005", "/metadata"),
    ]


def test_oversized_integer_literal_is_invalid_input() -> None:
    assert _codes(b'{"n": ' + b"9" * 5000 + b"}") == ["GSL-IO-003"]


def test_read_is_capped_at_limit(tmp_path: Path) -> None:
    path = tmp_path / "big.json"
    path.write_bytes(b" " * 50)
    assert read_bounded(path, InputLimits(max_bytes=50)) == b" " * 50
    result = read_bounded(path, InputLimits(max_bytes=49))
    assert isinstance(result, ParseResult)
    assert [i.code for i in result.report.issues] == ["GSL-IO-002"]


def test_errors_never_return_state(valid_doc: dict[str, Any]) -> None:
    valid_doc["relations"][0]["target"] = "ZZZ"
    result = parse_state(json.dumps(valid_doc).encode())
    assert result.state is None
    assert not result.report.ok


def test_json_pointer_escaping() -> None:
    assert json_pointer(()) == ""
    assert json_pointer(("a/b", "c~d", 0)) == "/a~1b/c~0d/0"
