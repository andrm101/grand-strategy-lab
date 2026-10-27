"""CLI help-text and exit-code contracts."""

import hashlib
import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from grand_strategy_lab import __version__
from grand_strategy_lab.cli import (
    EXIT_INVALID_INPUT,
    EXIT_NOT_IMPLEMENTED,
    EXIT_OK,
    EXIT_VALIDATION_FAILED,
    app,
)
from grand_strategy_lab.domain import from_json
from support import SCHEMA_PATH, VALID_FIXTURE

runner = CliRunner()


def _write(tmp_path: Path, doc: dict[str, Any]) -> Path:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == EXIT_OK
    for command in ("version", "smoke", "ingest", "validate", "schema"):
        assert command in result.output


def test_every_command_has_help() -> None:
    for args in (["ingest"], ["validate"], ["schema"], ["schema", "export"], ["smoke"]):
        assert runner.invoke(app, [*args, "--help"]).exit_code == EXIT_OK


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == EXIT_OK
    assert result.output.strip() == __version__


def test_ingest_fixture_writes_restamped_canonical_state(tmp_path: Path) -> None:
    out = tmp_path / "interim" / "state.json"
    args = ["ingest", "--game", "fixture", "--input", str(VALID_FIXTURE), "--output", str(out)]
    result = runner.invoke(app, args)
    assert result.exit_code == EXIT_OK, result.output
    state = from_json(out.read_bytes())
    assert state.metadata.source_sha256 == hashlib.sha256(VALID_FIXTURE.read_bytes()).hexdigest()
    assert b"\r\n" not in out.read_bytes()


def test_ingest_invalid_state_writes_nothing(tmp_path: Path, valid_doc: dict[str, Any]) -> None:
    valid_doc["relations"][0]["target"] = "AAA"
    out = tmp_path / "out.json"
    args = ["ingest", "--game", "fixture", "--input", str(_write(tmp_path, valid_doc))]
    result = runner.invoke(app, [*args, "--output", str(out)])
    assert result.exit_code == EXIT_VALIDATION_FAILED
    assert "GSL-REL-001" in result.output
    assert not out.exists()


def test_ingest_game_routing(tmp_path: Path) -> None:
    base = ["ingest", "--input", str(VALID_FIXTURE), "--output", str(tmp_path / "o.json")]
    assert runner.invoke(app, [*base, "--game", "eu4"]).exit_code == EXIT_NOT_IMPLEMENTED
    assert runner.invoke(app, [*base, "--game", "chess"]).exit_code == EXIT_INVALID_INPUT


def test_ingest_missing_input_is_invalid_input(tmp_path: Path) -> None:
    args = ["ingest", "--game", "fixture", "--input", str(tmp_path / "nope.json")]
    result = runner.invoke(app, [*args, "--output", str(tmp_path / "o.json")])
    assert result.exit_code == EXIT_INVALID_INPUT


def test_validate_valid_fixture_json_report() -> None:
    args = ["validate", "--state", str(VALID_FIXTURE), "--game", "fixture", "--format", "json"]
    result = runner.invoke(app, args)
    assert result.exit_code == EXIT_OK
    assert json.loads(result.output) == {"schema_version": "0.1.0", "issues": [], "ok": True}


def test_validate_reports_future_information(tmp_path: Path, valid_doc: dict[str, Any]) -> None:
    valid_doc["relations"][0]["since"] = "1500-01-01"
    result = runner.invoke(app, ["validate", "--state", str(_write(tmp_path, valid_doc))])
    assert result.exit_code == EXIT_VALIDATION_FAILED
    assert "GSL-DATE-002 /relations/0/since" in result.output


def test_validate_malformed_json_is_invalid_input(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert runner.invoke(app, ["validate", "--state", str(bad)]).exit_code == EXIT_INVALID_INPUT


def test_schema_export_matches_committed_schema(tmp_path: Path) -> None:
    out = tmp_path / "schema.json"
    result = runner.invoke(app, ["schema", "export", "--output", str(out)])
    assert result.exit_code == EXIT_OK
    assert out.read_bytes() == SCHEMA_PATH.read_bytes(), "run `uv run gsl schema export`"


def test_smoke_missing_fixture_is_invalid_input(tmp_path: Path) -> None:
    result = runner.invoke(app, ["smoke", "--fixture", str(tmp_path / "absent.json")])
    assert result.exit_code == EXIT_INVALID_INPUT


def test_smoke_malformed_json_is_invalid_input(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = runner.invoke(app, ["smoke", "--fixture", str(bad)])
    assert result.exit_code == EXIT_INVALID_INPUT


def test_ingest_refuses_to_overwrite_input(tmp_path: Path) -> None:
    source = tmp_path / "raw.json"
    source.write_bytes(VALID_FIXTURE.read_bytes())
    before = source.read_bytes()
    args = ["ingest", "--game", "fixture", "--input", str(source), "--output", str(source)]
    result = runner.invoke(app, args)
    assert result.exit_code == EXIT_INVALID_INPUT
    assert source.read_bytes() == before


def test_unwritable_output_is_invalid_input(tmp_path: Path) -> None:
    directory = tmp_path / "out"
    directory.mkdir()
    args = ["ingest", "--game", "fixture", "--input", str(VALID_FIXTURE)]
    assert runner.invoke(app, [*args, "--output", str(directory)]).exit_code == EXIT_INVALID_INPUT
    schema_args = ["schema", "export", "--output", str(directory)]
    assert runner.invoke(app, schema_args).exit_code == EXIT_INVALID_INPUT


def test_missing_state_reports_io_001(tmp_path: Path) -> None:
    args = ["validate", "--state", str(tmp_path / "nope.json"), "--format", "json"]
    result = runner.invoke(app, args)
    assert result.exit_code == EXIT_INVALID_INPUT
    assert [i["code"] for i in json.loads(result.output)["issues"]] == ["GSL-IO-001"]


def test_text_report_escapes_control_characters(tmp_path: Path, valid_doc: dict[str, Any]) -> None:
    valid_doc["actors"]["AAA"]["\x1b[31mevil"] = 1
    result = runner.invoke(app, ["validate", "--state", str(_write(tmp_path, valid_doc))])
    assert result.exit_code == EXIT_VALIDATION_FAILED
    assert "\x1b" not in result.output
    assert r"\x1b[31mevil" in result.output
