"""Validation issues and reports."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel, ConfigDict, computed_field

from grand_strategy_lab.domain.serialization import SCHEMA_VERSION
from grand_strategy_lab.validation.codes import CODES, Severity


def json_pointer(loc: Sequence[str | int]) -> str:
    """Render a location as an RFC 6901 JSON pointer (``""`` is the document root)."""
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in loc)


class ValidationIssue(BaseModel):
    """One finding about an input or state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: Severity
    code: str
    path: str
    message: str
    remediation: str

    @classmethod
    def from_code(cls, code: str, path: str, message: str) -> ValidationIssue:
        """Build an issue using the catalogue's default severity and remediation."""
        info = CODES[code]
        return cls(
            severity=info.severity,
            code=code,
            path=path,
            message=message,
            remediation=info.remediation,
        )


class ValidationReport(BaseModel):
    """Deterministically ordered collection of issues."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = SCHEMA_VERSION
    issues: tuple[ValidationIssue, ...] = ()

    @computed_field
    @property
    def ok(self) -> bool:
        """True when no issue has error severity."""
        return not any(issue.severity == "error" for issue in self.issues)

    @classmethod
    def from_issues(cls, issues: Iterable[ValidationIssue]) -> ValidationReport:
        """Build a report with issues sorted by (path, code, message)."""
        ordered = sorted(issues, key=lambda issue: (issue.path, issue.code, issue.message))
        return cls(issues=tuple(ordered))

    def has_code_prefix(self, prefix: str) -> bool:
        """Return whether any issue code starts with ``prefix``."""
        return any(issue.code.startswith(prefix) for issue in self.issues)
