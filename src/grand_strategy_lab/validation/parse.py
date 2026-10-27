"""Bounded parsing of untrusted canonical-JSON input into a validated ``GameState``."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from grand_strategy_lab.domain.models import GameState
from grand_strategy_lab.domain.serialization import from_json, is_supported_schema_version
from grand_strategy_lab.validation.codes import CODES
from grand_strategy_lab.validation.report import ValidationIssue, ValidationReport, json_pointer
from grand_strategy_lab.validation.semantic import validate_state

DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB: ample for canonical fixtures, bounds memory
DEFAULT_MAX_DEPTH = 64  # canonical states nest < 10 levels; extensions get headroom

_PYDANTIC_CODE_MAP = {
    "missing": "GSL-STR-001",
    "extra_forbidden": "GSL-STR-002",
    "finite_number": "GSL-NUM-001",
}


@dataclass(frozen=True, slots=True)
class InputLimits:
    """Resource limits applied to untrusted input before parsing."""

    max_bytes: int = DEFAULT_MAX_BYTES
    max_depth: int = DEFAULT_MAX_DEPTH


@dataclass(frozen=True, slots=True)
class ParseResult:
    """A state (``None`` whenever any error exists) and its report."""

    state: GameState | None
    report: ValidationReport


def _fail(code: str, path: str, message: str) -> ParseResult:
    issue = ValidationIssue.from_code(code, path, message)
    return ParseResult(state=None, report=ValidationReport.from_issues([issue]))


def _children(node: object) -> list[object]:
    if isinstance(node, dict):
        return list(cast(dict[str, object], node).values())
    if isinstance(node, list):
        return list(cast(list[object], node))
    return []


def _max_depth(document: object) -> int:
    deepest = 0
    stack: list[tuple[object, int]] = [(document, 1)]
    while stack:
        node, depth = stack.pop()
        deepest = max(deepest, depth)
        stack.extend((child, depth + 1) for child in _children(node))
    return deepest


def _declared_schema_version(document: object) -> object:
    if not isinstance(document, dict):
        return None
    metadata = cast(dict[str, object], document).get("metadata")
    if not isinstance(metadata, dict):
        return None
    return cast(dict[str, object], metadata).get("schema_version")


def _structural_issues(error: ValidationError) -> Iterator[ValidationIssue]:
    for detail in error.errors(include_url=False):
        kind = detail["type"]
        code = kind if kind in CODES else _PYDANTIC_CODE_MAP.get(kind, "GSL-STR-003")
        yield ValidationIssue.from_code(code, json_pointer(detail["loc"]), detail["msg"])


def read_bounded(path: Path, limits: InputLimits) -> bytes | ParseResult:
    """Read ``path`` if it is a regular file within ``limits``; otherwise return a failure."""
    if not path.is_file():
        return _fail("GSL-IO-001", "", f"input file not found: {path.name}")
    size = path.stat().st_size
    if size > limits.max_bytes:
        return _fail("GSL-IO-002", "", f"input is {size} bytes; limit is {limits.max_bytes}")
    return path.read_bytes()


def parse_state(
    raw: bytes,
    *,
    limits: InputLimits | None = None,
    relation_kinds: frozenset[str] | None = None,
) -> ParseResult:
    """Parse canonical JSON bytes into a ``GameState`` and validate it fully.

    Order: size → JSON syntax → nesting depth → schema version → structure →
    cross-object checks. The state is returned only if no error-level issue exists,
    so a failed parse can never yield a superficially valid state.
    """
    limits = limits or InputLimits()
    if len(raw) > limits.max_bytes:
        return _fail("GSL-IO-002", "", f"input is {len(raw)} bytes; limit is {limits.max_bytes}")
    try:
        document: object = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _fail("GSL-IO-003", "", str(exc))
    except RecursionError:
        return _fail("GSL-IO-004", "", "JSON nesting exceeds interpreter recursion limit")
    depth = _max_depth(document)
    if depth > limits.max_depth:
        return _fail("GSL-IO-004", "", f"nesting depth {depth} exceeds {limits.max_depth}")

    version = _declared_schema_version(document)
    if not isinstance(version, str) or not is_supported_schema_version(version):
        return _fail(
            "GSL-SCH-001",
            "/metadata/schema_version",
            f"schema version {version!r} is missing or not supported",
        )

    try:
        state = from_json(raw)
    except ValidationError as exc:
        return ParseResult(state=None, report=ValidationReport.from_issues(_structural_issues(exc)))

    report = validate_state(state, relation_kinds=relation_kinds)
    return ParseResult(state=state if report.ok else None, report=report)
