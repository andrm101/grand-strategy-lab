"""Validation: issue catalogue, reports, bounded parsing, and cross-object checks."""

from grand_strategy_lab.validation.codes import CODES, CodeInfo, Severity
from grand_strategy_lab.validation.parse import (
    InputLimits,
    ParseResult,
    parse_state,
    read_bounded,
)
from grand_strategy_lab.validation.report import ValidationIssue, ValidationReport, json_pointer
from grand_strategy_lab.validation.semantic import validate_state

__all__ = [
    "CODES",
    "CodeInfo",
    "InputLimits",
    "ParseResult",
    "Severity",
    "ValidationIssue",
    "ValidationReport",
    "json_pointer",
    "parse_state",
    "read_bounded",
    "validate_state",
]
