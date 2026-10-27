"""Canonical JSON round-trip and schema-version policy."""

import pytest

from grand_strategy_lab.domain import (
    SCHEMA_VERSION,
    from_json,
    is_supported_schema_version,
    to_json,
)
from support import VALID_FIXTURE


def test_fixture_is_canonical_and_round_trips_byte_identically() -> None:
    text = VALID_FIXTURE.read_text(encoding="utf-8")
    state = from_json(text)
    assert to_json(state) == text
    assert from_json(to_json(state)) == state


def test_to_json_is_lf_terminated_and_sorted() -> None:
    text = to_json(from_json(VALID_FIXTURE.read_bytes()))
    assert text.endswith("}\n")
    assert "\r" not in text
    assert text.index('"actors"') < text.index('"clock"') < text.index('"metadata"')


@pytest.mark.parametrize(
    ("version", "supported"),
    [
        (SCHEMA_VERSION, True),
        ("0.1.7", True),
        ("0.2.0", False),
        ("1.1.0", False),
        ("0.1", False),
        ("v0.1.0", False),
    ],
)
def test_schema_version_policy(version: str, supported: bool) -> None:
    assert is_supported_schema_version(version) is supported
