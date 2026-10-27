"""Fixture adapter: hashing, provenance re-stamping, limits, protocol conformance."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from grand_strategy_lab.adapters import FixtureAdapter, GameAdapter
from grand_strategy_lab.domain import from_json
from grand_strategy_lab.validation import InputLimits
from support import VALID_FIXTURE

FIXED_NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
PROVENANCE_FIELDS = {"source_sha256", "parsed_at_utc", "adapter_name", "adapter_version"}


def test_conforms_to_protocol() -> None:
    adapter: GameAdapter = FixtureAdapter()
    assert adapter.name == "fixture"


def test_restamps_provenance_and_preserves_content() -> None:
    result = FixtureAdapter(now=lambda: FIXED_NOW).load(VALID_FIXTURE)
    assert result.state is not None
    meta = result.state.metadata
    assert meta.source_sha256 == hashlib.sha256(VALID_FIXTURE.read_bytes()).hexdigest()
    assert meta.parsed_at_utc == FIXED_NOW
    original = from_json(VALID_FIXTURE.read_bytes())
    assert result.state.model_dump(exclude={"metadata"}) == original.model_dump(
        exclude={"metadata"}
    )
    assert meta.model_dump(exclude=PROVENANCE_FIELDS) == original.metadata.model_dump(
        exclude=PROVENANCE_FIELDS
    )


def test_deterministic_with_injected_clock() -> None:
    adapter = FixtureAdapter(now=lambda: FIXED_NOW)
    assert adapter.load(VALID_FIXTURE) == adapter.load(VALID_FIXTURE)


def test_missing_file(tmp_path: Path) -> None:
    result = FixtureAdapter().load(tmp_path / "absent.json")
    assert result.state is None
    assert [i.code for i in result.report.issues] == ["GSL-IO-001"]


def test_directory_is_not_a_file(tmp_path: Path) -> None:
    assert [i.code for i in FixtureAdapter().load(tmp_path).report.issues] == ["GSL-IO-001"]


def test_size_limit_enforced_before_read() -> None:
    result = FixtureAdapter().load(VALID_FIXTURE, limits=InputLimits(max_bytes=100))
    assert result.state is None
    assert [i.code for i in result.report.issues] == ["GSL-IO-002"]
