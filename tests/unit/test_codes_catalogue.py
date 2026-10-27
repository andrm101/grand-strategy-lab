"""The issue-code catalogue is complete, used consistently, and documented."""

import re

from grand_strategy_lab.validation import CODES
from grand_strategy_lab.validation.parse import _PYDANTIC_CODE_MAP  # pyright: ignore[reportPrivateUsage]
from support import REPO_ROOT

CODE_RE = re.compile(r"GSL-[A-Z]+-\d{3}")
DOCS = REPO_ROOT / "docs" / "validation-codes.md"


def test_every_code_used_in_source_is_catalogued() -> None:
    used: set[str] = set()
    for path in (REPO_ROOT / "src").rglob("*.py"):
        used.update(CODE_RE.findall(path.read_text(encoding="utf-8")))
    assert used - set(CODES) == set()
    assert set(_PYDANTIC_CODE_MAP.values()) <= set(CODES)


def test_every_catalogued_code_is_documented() -> None:
    documented = set(CODE_RE.findall(DOCS.read_text(encoding="utf-8")))
    assert set(CODES) == documented
