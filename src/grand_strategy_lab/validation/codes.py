"""Stable catalogue of validation issue codes (documented in docs/validation-codes.md).

Codes are append-only: once published, a code's meaning never changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True, slots=True)
class CodeInfo:
    """Default severity, title, and remediation for one issue code."""

    severity: Severity
    title: str
    remediation: str


CODES: dict[str, CodeInfo] = {
    # Input / IO
    "GSL-IO-001": CodeInfo(
        "error",
        "Input file missing or unreadable",
        "Check the path and permissions; inputs must be readable regular files.",
    ),
    "GSL-IO-002": CodeInfo(
        "error",
        "Input file exceeds size limit",
        "Use a smaller input or raise InputLimits.max_bytes deliberately.",
    ),
    "GSL-IO-003": CodeInfo(
        "error", "Input is not valid UTF-8 JSON", "Fix the JSON syntax or encoding."
    ),
    "GSL-IO-004": CodeInfo(
        "error",
        "JSON nesting exceeds depth limit",
        "Flatten the document or raise InputLimits.max_depth deliberately.",
    ),
    "GSL-IO-005": CodeInfo(
        "error",
        "Duplicate JSON object key",
        "Remove the repeated key; duplicates would silently overwrite earlier values.",
    ),
    # Schema version
    "GSL-SCH-001": CodeInfo(
        "error",
        "Unsupported or missing schema version",
        "Re-export the state with this release's schema version (see ADR-0005).",
    ),
    # Structure
    "GSL-STR-001": CodeInfo("error", "Required field missing", "Add the field."),
    "GSL-STR-002": CodeInfo(
        "error",
        "Unknown field",
        "Remove the field or move game-specific data under an extensions namespace.",
    ),
    "GSL-STR-003": CodeInfo(
        "error",
        "Invalid value or type",
        "Provide a value of the documented type and format; values are never coerced.",
    ),
    # Numeric
    "GSL-NUM-001": CodeInfo(
        "error", "Non-finite number", "Replace NaN/Infinity with a finite value."
    ),
    "GSL-NUM-002": CodeInfo(
        "error", "Amount below declared lower bound", "Correct the amount or its lower_bound."
    ),
    # Per-object invariants
    "GSL-REL-001": CodeInfo(
        "error", "Self-relation", "A relation must connect two different actors."
    ),
    "GSL-CON-001": CodeInfo(
        "error", "Actor on both sides of a conflict", "Place each actor on exactly one side."
    ),
    "GSL-CON-002": CodeInfo(
        "error",
        "Actor listed twice on one side of a conflict",
        "List each participant once per side.",
    ),
    "GSL-DATE-001": CodeInfo("error", "Start date after end date", "Swap or correct the dates."),
    "GSL-DATE-002": CodeInfo(
        "error",
        "Date after the state's clock",
        "A snapshot cannot contain future events; correct the date or the clock.",
    ),
    # Cross-object
    "GSL-CLK-001": CodeInfo(
        "error",
        "Metadata time differs from clock",
        "Set metadata.observed_at_game_time equal to clock.",
    ),
    "GSL-KEY-001": CodeInfo(
        "error", "Mapping key differs from object id", "Key each object by its own id."
    ),
    "GSL-REF-001": CodeInfo(
        "error", "Relation references unknown actor", "Add the actor or fix the reference."
    ),
    "GSL-REF-002": CodeInfo(
        "error", "Conflict references unknown actor", "Add the actor or fix the reference."
    ),
    "GSL-REF-003": CodeInfo(
        "error", "Territory references unknown actor", "Add the actor or fix the reference."
    ),
    "GSL-REF-004": CodeInfo(
        "error", "Resource references unknown actor", "Add the actor or fix the reference."
    ),
    "GSL-DUP-001": CodeInfo(
        "error", "Duplicate relation", "Keep one relation per (kind, endpoints, direction)."
    ),
    "GSL-DUP-002": CodeInfo("error", "Duplicate conflict id", "Give each conflict a unique id."),
    "GSL-DUP-003": CodeInfo(
        "error", "Duplicate resource position", "Keep one position per (actor, resource)."
    ),
    "GSL-VOC-001": CodeInfo(
        "warning",
        "Relation kind not in adapter vocabulary",
        "Use a declared kind, or extend the adapter vocabulary via an ADR.",
    ),
}
