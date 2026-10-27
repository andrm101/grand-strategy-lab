"""Bounded parsing of untrusted input."""

import json
from typing import Any

from grand_strategy_lab.validation import InputLimits, json_pointer, parse_state


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
    assert _codes(b"[]") == ["GSL-SCH-001"]


def test_errors_never_return_state(valid_doc: dict[str, Any]) -> None:
    valid_doc["relations"][0]["target"] = "ZZZ"
    result = parse_state(json.dumps(valid_doc).encode())
    assert result.state is None
    assert not result.report.ok


def test_json_pointer_escaping() -> None:
    assert json_pointer(()) == ""
    assert json_pointer(("a/b", "c~d", 0)) == "/a~1b/c~0d/0"
