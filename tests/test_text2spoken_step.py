"""Numbers, dates and abbreviations read through text2spoken.

:func:`euskaphone.normalize.normalize_text` reads numbers, dates, clock times,
money, measures, abbreviations and Roman numerals with text2spoken, in the lect
that :func:`euskaphone.registry.resolve_lect` gives. Each expected value is
text2spoken's reading, and the Euskaltzaindia norm named next to it gives that
reading. "Araua N p.P" is the page of the PDF at
https://www.euskaltzaindia.eus/dok/arauak/Araua_NNNN.pdf.
"""
import warnings

import pytest
import text2spoken
from text2spoken import InvalidLanguageTagError

from euskaphone import normalize
from euskaphone.lattice_core import phonemize
from euskaphone.registry import list_dialects
from tests.text2spoken_gaps import LAPURDI_LECT

READINGS = [
    # Araua 203 p.24: "(egokia) bigarren edo 2.; hirugarrena edo 3.a; IV.a"
    ("1. kapitulua", "lehen kapitulua"),
    ("2. kapitulua", "bigarren kapitulua"),
    ("5. kapitulua", "bosgarren kapitulua"),
    ("10. kapitulua", "hamargarren kapitulua"),
    ("16. kapitulua", "hamaseigarren kapitulua"),
    ("20. kapitulua", "hogeigarren kapitulua"),
    ("100. kapitulua", "ehungarren kapitulua"),
    # Araua 196 p.27: "(EGOKIA) ikus 25. or. (ikus 25. orrialdea)"; p.31: the
    # period of an abbreviation at the end of a sentence also ends it.
    ("23. or.", "hogeita hirugarren orrialdea."),
    # Araua 203 p.28: "3/4: hiru laurden"
    ("3/4 zati", "hiru laurden zati"),
    # Araua 203 p.66: "Lasterketa 2023-10-14an izango da."
    ("Bilera 2024-01-15ean da", "Bilera bi mila eta hogeita lauko urtarrilaren hamabostean da"),
    # Araua 203 p.15: "0,27: zero koma hogeita zazpi edo zero koma bi zazpi"
    ("3,14", "hiru koma hamalau"),
    # Araua 35 p.4: "Arratsaldeko hiruretan"
    ("Kontzertua 20:00etan hasiko da.", "Kontzertua arratsaldeko zortzietan hasiko da."),
    # Araua 196 p.27: "K.a. (Kristo aurreko; Kristo aurretik)"; p.41: "Kristo
    # ondoko; Kristo ondoren"
    ("K.a.", "Kristo aurreko."),
    ("K.o.", "Kristo ondoko."),
    ("K.a. 50", "Kristo aurreko berrogeita hamar"),
    # Araua 196 p.26: "hurr. (hurrengoa zein hurrengoak)"
    ("hurr.", "hurrengoak."),
]


@pytest.mark.parametrize("text,spoken", READINGS)
def test_text2spoken_reads_the_form(text, spoken):
    with warnings.catch_warnings():
        # The reading path calls no deprecated reader.
        warnings.simplefilter("error", DeprecationWarning)
        assert normalize.normalize_text(text) == spoken
    assert normalize.text2spoken_reading(text) == spoken
    # Text that is already spelled out comes through unchanged.
    assert normalize.normalize_text(spoken) == spoken


@pytest.mark.parametrize("text,spoken", READINGS)
def test_the_engine_reads_the_spoken_form(text, spoken):
    assert phonemize(text, "eu", contact="none") == phonemize(spoken, "eu", contact="none")


# Araua 7 gives "bortz" for some northern varieties.
@LAPURDI_LECT
@pytest.mark.parametrize("text,spoken", [
    ("5", "bortz"),
    ("15", "hamabortz"),
    ("500", "bortzehun"),
    ("15 katu", "hamabortz katu"),
    ("V. kapitulua", "borzgarren kapitulua"),
])
def test_lapurdian_reads_the_bortz_series(text, spoken):
    assert normalize.normalize_text(text, "eu-x-lapurdi") == spoken


@pytest.mark.parametrize("name", ["eu-x-lapurtera", "lapurtera", "labourdin", "eu-x-lapurdi"])
def test_every_lapurdian_name_reaches_text2spoken_as_one_lect(name):
    assert normalize.text2spoken_tag(name) == "eu-x-lapurdi"


@pytest.mark.parametrize("lect", list_dialects())
def test_each_lect_reaches_text2spoken_as_itself(lect):
    assert normalize.text2spoken_tag(lect) == lect


def test_a_lect_text2spoken_refuses_reads_as_eu(monkeypatch):
    def refuse(tag):
        raise InvalidLanguageTagError(tag)

    monkeypatch.setattr(text2spoken, "supports", refuse)
    normalize.text2spoken_tag.cache_clear()
    try:
        assert normalize.text2spoken_tag("eu-x-zuberera") == "eu"
    finally:
        normalize.text2spoken_tag.cache_clear()
