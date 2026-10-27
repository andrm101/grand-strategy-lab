"""GameDate parsing, formatting, and ordering."""

import pytest

from grand_strategy_lab.domain import GameDate


def test_parse_and_format_round_trip() -> None:
    date = GameDate.parse("0867-01-01")
    assert date == GameDate(867, 1, 1)
    assert date.isoformat() == "0867-01-01"
    assert str(date) == "0867-01-01"


def test_ordering_is_chronological() -> None:
    assert GameDate(1444, 11, 11) < GameDate(1444, 12, 1) < GameDate(1445, 1, 1)


def test_no_gregorian_assumption_for_day_31() -> None:
    # Calendar rules belong to adapters; the domain only bounds day to 1-31.
    assert GameDate.parse("1444-02-31").day == 31


@pytest.mark.parametrize(
    "text", ["1444-13-01", "1444-00-10", "1444-01-32", "0000-01-01", "1444-1-1", "14441111", ""]
)
def test_rejects_invalid_dates(text: str) -> None:
    with pytest.raises(ValueError):
        GameDate.parse(text)
