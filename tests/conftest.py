"""Shared test fixtures."""

import json
from typing import Any

import pytest

from support import VALID_FIXTURE


@pytest.fixture
def valid_doc() -> dict[str, Any]:
    """A fresh, mutable copy of the canonical valid fixture."""
    return json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
