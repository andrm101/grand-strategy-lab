"""In-game calendar date.

Games use their own calendars (EU4 has no leap years), so ``GameDate`` checks
only month 1-12 and day 1-31; per-game calendar rules belong to adapters.
Serialized as a zero-padded ``YYYY-MM-DD`` string and totally ordered.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

GAME_DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
_GAME_DATE_RE = re.compile(GAME_DATE_PATTERN)

MIN_YEAR = 1
MAX_YEAR = 9999
MONTHS_PER_YEAR = 12
MAX_DAY = 31


@dataclass(frozen=True, order=True, slots=True)
class GameDate:
    """A calendar-agnostic in-game date."""

    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if not MIN_YEAR <= self.year <= MAX_YEAR:
            raise ValueError(f"year must be in [{MIN_YEAR}, {MAX_YEAR}], got {self.year}")
        if not 1 <= self.month <= MONTHS_PER_YEAR:
            raise ValueError(f"month must be in [1, {MONTHS_PER_YEAR}], got {self.month}")
        if not 1 <= self.day <= MAX_DAY:
            raise ValueError(f"day must be in [1, {MAX_DAY}], got {self.day}")

    @classmethod
    def parse(cls, text: str) -> GameDate:
        """Parse a ``YYYY-MM-DD`` string."""
        if not _GAME_DATE_RE.fullmatch(text):
            raise ValueError(f"game date must match YYYY-MM-DD, got {text!r}")
        year, month, day = (int(part) for part in text.split("-"))
        return cls(year, month, day)

    def isoformat(self) -> str:
        """Return the canonical ``YYYY-MM-DD`` form."""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def __str__(self) -> str:
        return self.isoformat()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        from_str = core_schema.no_info_after_validator_function(
            cls.parse, core_schema.str_schema(pattern=GAME_DATE_PATTERN)
        )
        return core_schema.json_or_python_schema(
            json_schema=from_str,
            python_schema=core_schema.union_schema([core_schema.is_instance_schema(cls), from_str]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda value: value.isoformat()
            ),
        )
