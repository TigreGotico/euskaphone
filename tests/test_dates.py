"""Numeric date reading — the 2024ko urtarrilaren 15ean class.

Expected forms follow Euskaltzaindia Araua 37 (*Data nola adierazi*): year in the
locative-genitive, month name in the possessive genitive, day in the inessive.
"""
import pytest

from euskaphone.dates import (
    MONTHS_GENITIVE, compose_date, normalize_dates,
)


def test_month_table_complete():
    assert len(MONTHS_GENITIVE) == 12
    assert MONTHS_GENITIVE[1] == "urtarrilaren"
    assert MONTHS_GENITIVE[3] == "martxoaren"
    assert MONTHS_GENITIVE[12] == "abenduaren"


@pytest.mark.parametrize("text,expected", [
    # ISO year-first
    ("2024-01-15", "bi mila eta hogeita lauko urtarrilaren hamabostean"),
    ("2024/01/15", "bi mila eta hogeita lauko urtarrilaren hamabostean"),
    # European day-first
    ("15/01/2024", "bi mila eta hogeita lauko urtarrilaren hamabostean"),
    ("15-01-2024", "bi mila eta hogeita lauko urtarrilaren hamabostean"),
    # Roman-numeral month (Araua 37 lists 1995/III/07)
    ("1995/III/07", "mila bederatziehun eta laurogeita hamabosteko "
                    "martxoaren zazpian"),
])
def test_numeric_dates(text, expected):
    assert normalize_dates(text) == expected


def test_compose_date_direct():
    assert compose_date(1995, 3, 7) == \
        "mila bederatziehun eta laurogeita hamabosteko martxoaren zazpian"


def test_day_inessive_epenthesis():
    # consonant-final day -> -ean (hamabost -> hamabostean); vowel-final -> -an
    assert compose_date(2000, 6, 15).endswith("hamabostean")
    assert compose_date(2000, 6, 2).endswith("bian")   # bi -> bian


def test_non_date_triples_left_alone():
    # a ratio / score is not a calendar date (no 4-digit year, out of range)
    assert normalize_dates("3/4 zati") == "3/4 zati"
    assert normalize_dates("40/50/60") == "40/50/60"


def test_already_spelled_date_untouched_here():
    # a month-name date needs nothing from this stage
    text = "2024ko urtarrilaren 15ean"
    assert normalize_dates(text) == text


def test_date_in_running_text_keeps_trailing_punctuation():
    out = normalize_dates("Bilera 2024-01-15ean da")
    # the "ean" tail is not part of the numeric triple, so the token is not a
    # bare numeric date and is left for the number stage
    assert "2024-01-15ean" in out
