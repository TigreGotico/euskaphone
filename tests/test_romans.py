"""Roman-numeral reading — ordinal-period and monarch conventions.

Expected forms follow Euskaltzaindia Araua 18 (digit/Roman + period = ordinal,
century-as-ordinal) and the Euskara Batuaren Eskuliburua rule that a dynastic
Roman numeral is a postposed, always-declined ordinal (``Luis XIV.a`` →
``hamalaugarrena``; standard-Batua fifth is ``bosgarren``).
"""
import pytest

from euskaphone.romans import (
    monarch_ordinal, normalize_romans, roman_to_int,
)


@pytest.mark.parametrize("s,n", [
    ("I", 1), ("IV", 4), ("V", 5), ("IX", 9), ("X", 10),
    ("XIV", 14), ("XVI", 16), ("XX", 20), ("XXI", 21),
    ("XL", 40), ("XC", 90), ("C", 100), ("CD", 400), ("MCMLXXXIV", 1984),
])
def test_roman_to_int(s, n):
    assert roman_to_int(s) == n


@pytest.mark.parametrize("s", ["IIII", "VV", "XXXX", "IC", "", "ABC", "Luis"])
def test_roman_rejects_noncanonical(s):
    assert roman_to_int(s) is None


# --- ordinal-period convention (XX. mendea) --------------------------------

@pytest.mark.parametrize("text,expected", [
    ("XX. mendea", "hogeigarren mendea"),         # Araua 18: century-as-ordinal
    ("XXI. mendean", "hogeita batgarren mendean"),
    ("V. kapitulua", "bosgarren kapitulua"),      # Batua bosgarren
    ("XVIII. mendeko", "hemezortzigarren mendeko"),
])
def test_ordinal_period(text, expected):
    assert normalize_romans(text) == expected


# --- monarch / pope postposed ordinal with the article --------------------

@pytest.mark.parametrize("text,expected", [
    ("Luis XIV.a", "Luis hamalaugarrena"),        # written with .a
    ("Karlos V", "Karlos bosgarrena"),            # bare, read the same way
    ("Joan XXIII.a", "Joan hogeita hirugarrena"),
    ("Benedikto XVI.aren", "Benedikto hamaseigarrenaren"),  # declined
    ("Karlos I.a", "Karlos lehena"),              # suppletive first
    ("Elisabet II.a", "Elisabet bigarrena"),
])
def test_monarch_ordinal(text, expected):
    assert normalize_romans(text) == expected


def test_monarch_helper_first_is_suppletive():
    assert monarch_ordinal(1) == "lehena"
    assert monarch_ordinal(2) == "bigarrena"
    assert monarch_ordinal(14) == "hamalaugarrena"


# --- the V. period ambiguity (documented heuristic) ------------------------

def test_sentence_final_roman_left_literal():
    # "V." at the end of a sentence is a numeral + full stop, not "fifth":
    # no lower-case common noun follows, so it is left untouched.
    assert normalize_romans("Ikusi dut V.") == "Ikusi dut V."


def test_roman_period_then_capitalized_word_left_literal():
    # after a lower-case word, a Roman + period + capitalized next word is not
    # the ordinal-noun pattern, so it stays a literal numeral + full stop
    assert normalize_romans("ikus V. Sarrera") == "ikus V. Sarrera"


def test_ordinary_words_with_roman_letters_untouched():
    # tokens that merely start with Roman letters must never be read as numerals
    assert normalize_romans("Luis etorri da") == "Luis etorri da"
    assert normalize_romans("Ikusi dut mendia") == "Ikusi dut mendia"
    assert normalize_romans("Divide et impera") == "Divide et impera"


def test_dialect_bortz_series_for_lapurdian():
    # Lapurdian substitutes the bortz series on the ordinal too
    assert normalize_romans("V. kapitulua", "eu-x-lapurtera") == \
        "borzgarren kapitulua"
