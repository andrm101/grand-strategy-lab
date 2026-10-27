"""End-to-end smoke check on the bundled fixture."""

import hashlib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from grand_strategy_lab.cli import app

FIXTURE = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "minimal_state.json"


@pytest.mark.smoke
def test_smoke_reports_fixture_hash() -> None:
    expected = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    result = CliRunner().invoke(app, ["smoke", "--fixture", str(FIXTURE)])
    assert result.exit_code == 0
    assert f"sha256={expected}" in result.output
