"""Bounded parsing of untrusted canonical-JSON input into a validated ``GameState``."""

from __future__ import annotations

import json
import math
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


class _JsonObject(dict[str, object]):
    """JSON object that remembers keys which appeared more than once."""

    duplicates: list[str]

    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicates = []
        for key, value in pairs:
            if key in self:
                self.duplicates.append(key)
            self[key] = value


def _fail(code: str, path: str, message: str) -> ParseResult:
    return _fail_many([ValidationIssue.from_code(code, path, message)])


def _fail_many(issues: list[ValidationIssue]) -> ParseResult:
    return ParseResult(state=None, report=ValidationReport.from_issues(issues))


def _children(node: object) -> list[tuple[str | int, object]]:
    if isinstance(node, dict):
        return list(cast(dict[str, object], node).items())
    if isinstance(node, list):
        return list(enumerate(cast(list[object], node)))
    return []


def _scan(document: object, max_depth: int) -> list[ValidationIssue]:
    """Walk the raw document once: depth limit, then duplicate keys and non-finite numbers."""
    issues: list[ValidationIssue] = []
    stack: list[tuple[object, tuple[str | int, ...]]] = [(document, ())]
    while stack:
        node, path = stack.pop()
        if len(path) + 1 > max_depth:
            return [
                ValidationIssue.from_code("GSL-IO-004", "", f"nesting depth exceeds {max_depth}")
            ]
        if isinstance(node, _JsonObject):
            issues.extend(
                ValidationIssue.from_code(
                    "GSL-IO-005", json_pointer((*path, key)), f"duplicate JSON key {key!r}"
                )
                for key in sorted(set(node.duplicates))
            )
        elif isinstance(node, float) and not math.isfinite(node):
            issues.append(
                ValidationIssue.from_code(
                    "GSL-NUM-001", json_pointer(path), f"non-finite number {node}"
                )
            )
        stack.extend((child, (*path, key)) for key, child in _children(node))
    return issues


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
    """Read at most ``limits.max_bytes`` from a regular file; otherwise return a failure.

    The read itself is capped, so a file that grows after any size check still
    cannot exceed the limit.
    """
    if not path.is_file():
        return _fail("GSL-IO-001", "", f"input file not found: {path.name}")
    try:
        with path.open("rb") as handle:
            data = handle.read(limits.max_bytes + 1)
    except OSError as exc:
        return _fail("GSL-IO-001", "", f"cannot read {path.name}: {exc.strerror}")
    if len(data) > limits.max_bytes:
        return _fail("GSL-IO-002", "", f"input exceeds the {limits.max_bytes}-byte limit")
    return data


def parse_state(
    raw: bytes,
    *,
    limits: InputLimits | None = None,
    relation_kinds: frozenset[str] | None = None,
) -> ParseResult:
    """Parse canonical JSON bytes into a ``GameState`` and validate it fully.

    Order: size → JSON syntax → raw-document scan (depth, duplicate keys,
    non-finite numbers) → schema version → structure → cross-object checks.
    The state is returned only if no error-level issue exists, so a failed
    parse can never yield a superficially valid state.
    """
    limits = limits or InputLimits()
    if len(raw) > limits.max_bytes:
        return _fail("GSL-IO-002", "", f"input exceeds the {limits.max_bytes}-byte limit")
    try:
        document: object = json.loads(raw.decode("utf-8"), object_pairs_hook=_JsonObject)
    except RecursionError:
        return _fail("GSL-IO-004", "", "JSON nesting exceeds interpreter recursion limit")
    except ValueError as exc:  # invalid UTF-8, JSON syntax, or integer-digit limit
        return _fail("GSL-IO-003", "", str(exc))

    scan_issues = _scan(document, limits.max_depth)
    if scan_issues:
        return _fail_many(scan_issues)

    version = _declared_schema_version(document)
    if isinstance(version, str) and not is_supported_schema_version(version):
        return _fail(
            "GSL-SCH-001",
            "/metadata/schema_version",
            f"schema version {version!r} is not supported",
        )

    try:
        state = from_json(raw)
    except ValidationError as exc:
        return ParseResult(state=None, report=ValidationReport.from_issues(_structural_issues(exc)))

    report = validate_state(state, relation_kinds=relation_kinds)
    return ParseResult(state=state if report.ok else None, report=report)
