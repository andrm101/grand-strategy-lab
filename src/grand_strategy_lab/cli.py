"""Command-line entry point for Grand Strategy Lab (``gsl``).

Milestone 0 exposes only ``version`` and ``smoke``; pipeline commands are stubs
that fail loudly with exit code 2 until their milestone lands.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Annotated

import typer

from grand_strategy_lab import __version__

EXIT_NOT_IMPLEMENTED = 2
EXIT_INVALID_INPUT = 3

DEFAULT_FIXTURE = Path("data/fixtures/minimal_state.json")

app = typer.Typer(
    name="gsl",
    help="Grand Strategy Lab: forecasts, simulations, and explainable recommendations.",
    no_args_is_help=True,
    add_completion=False,
)


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def _not_implemented(command: str, milestone: str) -> None:
    typer.echo(f"error: '{command}' is not implemented yet ({milestone}).", err=True)
    raise typer.Exit(code=EXIT_NOT_IMPLEMENTED)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def smoke(
    fixture: Annotated[
        Path, typer.Option("--fixture", help="JSON fixture to load and hash.")
    ] = DEFAULT_FIXTURE,
) -> None:
    """Load a bundled fixture, check it is valid JSON, and print its SHA-256."""
    if not fixture.is_file():
        typer.echo(f"error: fixture not found: {fixture}", err=True)
        raise typer.Exit(code=EXIT_INVALID_INPUT)
    raw = fixture.read_bytes()
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        typer.echo(f"error: fixture is not valid JSON: {exc}", err=True)
        raise typer.Exit(code=EXIT_INVALID_INPUT) from exc
    typer.echo(f"ok sha256={sha256_bytes(raw)} path={fixture.as_posix()}")


@app.command()
def ingest() -> None:
    """Ingest a save, export, or fixture into the canonical state (not implemented)."""
    _not_implemented("ingest", "Milestone 1/2")


@app.command()
def validate() -> None:
    """Validate a canonical state file (not implemented)."""
    _not_implemented("validate", "Milestone 1")


if __name__ == "__main__":
    app()
