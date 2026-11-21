"""Numeric date reading — the 2024ko urtarrilaren 15ean class.

Expected forms follow Euskaltzaindia Araua 37 (*Data nola adierazi*): year in the
locative-genitive, month name in the possessive genitive. A bare numeric date
reads the day in the absolutive with the article (Araua 203 p.66: «Data zifra
bidez adierazten denean testu batean txertatu gabe, absolutiboan, ez zaio
artikulua eransten. Ulertu behar da konbentzio bat dela, eta, beraz,
irakurtzean artikulua ezarri behar da» and «Data: mila bederatziehun eta
laurogeita hiruko martxoaren zazpia»). text2spoken reads the dates for
:func:`euskaphone.normalize.normalize_text`; the date stage of
:mod:`euskaphone.dates` is deprecated.
"""
import pytest

from euskaphone.dates import (
    MONTHS_GENITIVE, normalize_dates,
)
from euskaphone.normalize import normalize_text


def test_month_table_complete():
    assert len(MONTHS_GENITIVE) == 12
    assert MONTHS_GENITIVE[1] == "urtarrilaren"
    assert MONTHS_GENITIVE[3] == "martxoaren"
    assert MONTHS_GENITIVE[12] == "abenduaren"


@pytest.mark.parametrize("text,expected", [
    # ISO year-first
    ("2024-01-15", "bi mila eta hogeita lauko urtarrilaren hamabosta"),
    ("2024/01/15", "bi mila eta hogeita lauko urtarrilaren hamabosta"),
    # European day-first
    ("15/01/2024", "bi mila eta hogeita lauko urtarrilaren hamabosta"),
    ("15-01-2024", "bi mila eta hogeita lauko urtarrilaren hamabosta"),
    # Roman-numeral month (Araua 37 lists 1995/III/07)
    ("1995/III/07", "mila bederatziehun eta laurogeita hamabosteko "
                    "martxoaren zazpia"),
])
def test_numeric_dates(text, expected):
    # Araua 203 p.66: a bare date reads the day in the absolutive.
    assert normalize_text(text) == expected


def test_bare_date_reads_the_day_in_the_absolutive():
    # Araua 203 p.66: «Data: mila bederatziehun eta laurogeita hiruko
    # martxoaren zazpia»
    assert normalize_text("1995-03-07") == \
        "mila bederatziehun eta laurogeita hamabosteko martxoaren zazpia"


def test_day_article_epenthesis():
    # the day takes the article -a: hamabost -> hamabosta, bi -> bia
    assert normalize_text("2000-06-15").endswith("hamabosta")
    assert normalize_text("2000-06-02").endswith("bia")


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
