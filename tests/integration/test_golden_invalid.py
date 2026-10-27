"""Golden tests: invalid inputs yield exactly the expected, deterministic issues."""

import json
from pathlib import Path

import pytest

from grand_strategy_lab.adapters import FIXTURE_RELATION_KINDS
from grand_strategy_lab.validation import parse_state
from support import INVALID_FIXTURES

CASES = sorted(p for p in INVALID_FIXTURES.glob("*.json") if not p.name.endswith(".expected.json"))


def test_golden_cases_exist() -> None:
    assert len(CASES) >= 15


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.stem)
def test_golden_case(case: Path) -> None:
    expected = json.loads(case.with_suffix(".expected.json").read_text(encoding="utf-8"))
    raw = case.read_bytes()
    result = parse_state(raw, relation_kinds=FIXTURE_RELATION_KINDS)
    actual = [{"code": i.code, "path": i.path} for i in result.report.issues]
    assert actual == expected["issues"]
    assert result.report.ok is expected["ok"]
    assert (result.state is not None) is expected["ok"]
    assert all(i.remediation for i in result.report.issues)
    rerun = parse_state(raw, relation_kinds=FIXTURE_RELATION_KINDS)
    assert rerun.report.model_dump_json() == result.report.model_dump_json()
