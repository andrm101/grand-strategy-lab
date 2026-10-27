"""Command-line entry point for Grand Strategy Lab (``gsl``).

Exit codes: 0 success; 1 validation errors; 2 not implemented; 3 unreadable or
invalid input or unusable output (missing file, size/depth limit, malformed JSON,
unknown game, output equal to input, filesystem write error).
"""

from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from grand_strategy_lab import __version__
from grand_strategy_lab.adapters import ADAPTERS, FIXTURE_RELATION_KINDS
from grand_strategy_lab.domain import game_state_json_schema, to_json
from grand_strategy_lab.domain.serialization import to_canonical_json
from grand_strategy_lab.validation import InputLimits, ParseResult, parse_state, read_bounded
from grand_strategy_lab.validation.report import ValidationReport

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_NOT_IMPLEMENTED = 2
EXIT_INVALID_INPUT = 3

PLANNED_GAMES = {"eu4": "Milestone 2"}

DEFAULT_FIXTURE = Path("data/fixtures/minimal_state.json")
DEFAULT_SCHEMA_PATH = Path("data/manifests/game_state.schema.json")


class OutputFormat(StrEnum):
    """Report rendering for ``ingest`` and ``validate``."""

    text = "text"
    json = "json"


app = typer.Typer(
    name="gsl",
    help="Grand Strategy Lab: forecasts, simulations, and explainable recommendations.",
    no_args_is_help=True,
    add_completion=False,
)
schema_app = typer.Typer(help="Canonical schema utilities.", no_args_is_help=True)
app.add_typer(schema_app, name="schema")

FormatOption = Annotated[
    OutputFormat, typer.Option("--format", help="Report format: text or json.")
]


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def _printable(text: str) -> str:
    """Escape non-printable characters so untrusted text cannot drive the terminal."""
    return "".join(
        char if char.isprintable() else char.encode("unicode_escape").decode("ascii")
        for char in text
    )


def _fail_output(message: str) -> NoReturn:
    typer.echo(f"error: {_printable(message)}", err=True)
    raise typer.Exit(code=EXIT_INVALID_INPUT)


def _write_text(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    except OSError as exc:
        _fail_output(f"cannot write {path.as_posix()}: {exc.strerror or exc}")


def _render(report: ValidationReport, fmt: OutputFormat) -> None:
    if fmt is OutputFormat.json:
        typer.echo(report.model_dump_json(indent=2))
        return
    status = "ok" if report.ok else "invalid"
    typer.echo(f"{status}: {len(report.issues)} issue(s)")
    for issue in report.issues:
        location = _printable(issue.path or "/")
        message = _printable(issue.message)
        typer.echo(f"  {issue.severity.upper()} {issue.code} {location}: {message}")
        typer.echo(f"    fix: {issue.remediation}")


def _exit_code(report: ValidationReport) -> int:
    if report.has_code_prefix("GSL-IO-"):
        return EXIT_INVALID_INPUT
    return EXIT_OK if report.ok else EXIT_VALIDATION_FAILED


def _check_game(game: str) -> None:
    if game in PLANNED_GAMES:
        typer.echo(
            f"error: game '{game}' is not implemented yet ({PLANNED_GAMES[game]}).", err=True
        )
        raise typer.Exit(code=EXIT_NOT_IMPLEMENTED)
    if game not in ADAPTERS:
        known = ", ".join(sorted(ADAPTERS))
        typer.echo(f"error: unknown game '{game}'; available: {known}.", err=True)
        raise typer.Exit(code=EXIT_INVALID_INPUT)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def ingest(
    input_path: Annotated[Path, typer.Option("--input", help="Source file to ingest.")],
    output: Annotated[Path, typer.Option("--output", help="Where to write canonical JSON.")],
    game: Annotated[str, typer.Option("--game", help="Adapter name, e.g. 'fixture'.")],
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Ingest a source file into a validated canonical state."""
    _check_game(game)
    if output.exists() and input_path.exists() and output.samefile(input_path):
        _fail_output("--output must differ from --input; raw inputs are never overwritten.")
    result = ADAPTERS[game]().load(input_path)
    _render(result.report, fmt)
    if result.state is not None:
        _write_text(output, to_json(result.state))
    raise typer.Exit(code=_exit_code(result.report))


@app.command()
def validate(
    state: Annotated[Path, typer.Option("--state", help="Canonical state JSON to validate.")],
    game: Annotated[
        str | None,
        typer.Option("--game", help="Adapter whose relation vocabulary to check against."),
    ] = None,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Validate a canonical state file without modifying it."""
    relation_kinds: frozenset[str] | None = None
    if game is not None:
        _check_game(game)
        relation_kinds = ADAPTERS[game]().relation_kinds
    limits = InputLimits()
    raw = read_bounded(state, limits)
    result = (
        raw
        if isinstance(raw, ParseResult)
        else parse_state(raw, limits=limits, relation_kinds=relation_kinds)
    )
    _render(result.report, fmt)
    raise typer.Exit(code=_exit_code(result.report))


@schema_app.command("export")
def schema_export(
    output: Annotated[
        Path, typer.Option("--output", help="Where to write the GameState JSON Schema.")
    ] = DEFAULT_SCHEMA_PATH,
) -> None:
    """Write the canonical GameState JSON Schema."""
    _write_text(output, to_canonical_json(game_state_json_schema()))
    typer.echo(f"wrote {output.as_posix()}")


@app.command()
def smoke(
    fixture: Annotated[
        Path, typer.Option("--fixture", help="Canonical fixture to load and validate.")
    ] = DEFAULT_FIXTURE,
) -> None:
    """Load a bundled fixture through the fixture adapter and print its SHA-256."""
    limits = InputLimits()
    raw = read_bounded(fixture, limits)
    if isinstance(raw, ParseResult):
        _render(raw.report, OutputFormat.text)
        raise typer.Exit(code=EXIT_INVALID_INPUT)
    result = parse_state(raw, limits=limits, relation_kinds=FIXTURE_RELATION_KINDS)
    if result.state is None:
        _render(result.report, OutputFormat.text)
        raise typer.Exit(code=_exit_code(result.report))
    typer.echo(
        f"ok sha256={sha256_bytes(raw)} actors={len(result.state.actors)} path={fixture.as_posix()}"
    )


if __name__ == "__main__":
    app()
