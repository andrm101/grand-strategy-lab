"""Constrained scalar types shared by the canonical domain model.

Patterns use ``[0-9]`` rather than the backslash-d class: Python and pydantic
match any Unicode digit with it, while other JSON Schema validators read it as ASCII.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import StringConstraints

IDENTIFIER_PATTERN = r"^[A-Za-z0-9_.:-]{1,64}$"
SLUG_PATTERN = r"^[a-z0-9_]+(\.[a-z0-9_]+)*$"
NAMESPACE_PATTERN = r"^[a-z0-9_]+$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"
SEMVER_PATTERN = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"

ActorId = Annotated[str, StringConstraints(pattern=IDENTIFIER_PATTERN)]
"""Stable actor identifier (e.g. a country tag); never a display name."""

TerritoryId = Annotated[str, StringConstraints(pattern=IDENTIFIER_PATTERN)]
"""Stable territory identifier (e.g. a province id)."""

ConflictId = Annotated[str, StringConstraints(pattern=IDENTIFIER_PATTERN)]
"""Stable conflict identifier."""

Slug = Annotated[str, StringConstraints(pattern=SLUG_PATTERN)]
"""Lower-case dotted vocabulary term, e.g. ``alliance`` or ``eu4.march``."""

Namespace = Annotated[str, StringConstraints(pattern=NAMESPACE_PATTERN)]
"""Extension namespace, e.g. ``eu4``."""

Sha256Hex = Annotated[str, StringConstraints(pattern=SHA256_PATTERN)]
"""Lower-case hexadecimal SHA-256 digest."""

SemVer = Annotated[str, StringConstraints(pattern=SEMVER_PATTERN)]
"""``MAJOR.MINOR.PATCH`` version string."""

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
"""Free text that must not be empty."""
