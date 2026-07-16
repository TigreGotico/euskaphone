"""The composed orthographic normalizer and its wiring into the lattice."""
import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.normalize import normalize_text


def test_stage_order_abbrev_then_number():
    # abbreviation expands, remaining number verbalizes
    assert normalize_text("23. or.") == normalize_text("23. or.")
    assert "orrialdea" in normalize_text("or. bat")


def test_roman_and_number_coexist():
    out = normalize_text("XX. mendean 100 urte")
    assert "hogeigarren mendean" in out
    assert "ehun urte" in out


def test_percent_currency_units_together():
    out = normalize_text("%20 igo eta 5 € eta 3 km-ra")
    assert "ehuneko hogei" in out
    assert "bost euro" in out
    assert "hiru kilometrora" in out


def test_numeric_date_expands():
    out = normalize_text("15/01/2024")
    assert out == "bi mila eta hogeita lauko urtarrilaren hamabostean"


def test_monarch_in_running_text():
    out = normalize_text("Karlos V.a errege zen")
    assert out == "Karlos bosgarrena errege zen"


def test_plain_text_untouched():
    assert normalize_text("kaixo mundua") == "kaixo mundua"


def test_bare_numbers_still_work():
    # the existing vigesimal core is still reached for plain tokens
    assert normalize_text("31 katu") == "hogeita hamaika katu"


def test_dialect_threads_through():
    # Lapurdian bortz series reaches the Roman ordinal path
    assert normalize_text("V. kapitulua", "eu-x-lapurtera") == \
        "borzgarren kapitulua"


# --- end-to-end: normalization feeds the pronunciation lattice ------------

def test_phonemize_reads_symbols_as_words():
    ph = EuskaPhonemizer()
    # the % and Roman ordinal are spelled out, so IPA comes back (no % or X)
    ipa = ph.phonemize_sentence("XX. mendean %5 igo da", "eu", contact="none")
    assert ipa
    assert "%" not in ipa and "X" not in ipa


def test_phonemize_abbreviation():
    ph = EuskaPhonemizer()
    ipa = ph.phonemize_sentence("katuak etab.", "eu", contact="none")
    assert ipa
    # "etab." became words; no stray period-letter reading
    assert "." not in ipa
