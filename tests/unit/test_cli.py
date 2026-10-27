"""CLI help-text and exit-code contracts."""

from pathlib import Path

from typer.testing import CliRunner

from grand_strategy_lab import __version__
from grand_strategy_lab.cli import EXIT_INVALID_INPUT, EXIT_NOT_IMPLEMENTED, app

runner = CliRunner()


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("version", "smoke", "ingest", "validate"):
        assert command in result.output


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_stub_commands_exit_not_implemented() -> None:
    for command in ("ingest", "validate"):
        result = runner.invoke(app, [command])
        assert result.exit_code == EXIT_NOT_IMPLEMENTED


def test_smoke_missing_fixture_is_invalid_input(tmp_path: Path) -> None:
    result = runner.invoke(app, ["smoke", "--fixture", str(tmp_path / "absent.json")])
    assert result.exit_code == EXIT_INVALID_INPUT


def test_smoke_malformed_json_is_invalid_input(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = runner.invoke(app, ["smoke", "--fixture", str(bad)])
    assert result.exit_code == EXIT_INVALID_INPUT
