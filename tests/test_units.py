"""Units, currency and percent reading.

Expected forms follow Euskaltzaindia Araua 197 (*Sinboloak*: a symbol is read as
its full word, ``%`` = ``ehuneko``, ``€`` = ``euro``) and the EIMA
*Ortotipografia* rule that ``ehuneko`` precedes the number in either writing
order.
"""
import pytest

from euskaphone.units import UNITS, normalize_units


# --- percent: ehuneko precedes the number in BOTH orders ------------------

@pytest.mark.parametrize("text,expected", [
    ("%5", "ehuneko bost"),
    ("% 5", "ehuneko bost"),
    ("5%", "ehuneko bost"),
    ("5 %", "ehuneko bost"),
    ("%20", "ehuneko hogei"),
    ("%1", "ehuneko bat"),
])
def test_percent_word_order(text, expected):
    assert normalize_units(text) == expected


def test_percent_in_running_text():
    assert normalize_units("Prezioa %20 igo da") == "Prezioa ehuneko hogei igo da"


def test_percent_with_declension():
    # a case ending after the percent attaches to the spelled number
    assert normalize_units("%15era igo") == "ehuneko hamabostera igo"


# --- currency -------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("€5", "bost euro"),
    ("5€", "bost euro"),
    ("5 €", "bost euro"),
    ("€1", "euro bat"),        # "bat" (one) is postposed in Basque
    ("1 €", "euro bat"),
    ("€100", "ehun euro"),
])
def test_currency(text, expected):
    assert normalize_units(text) == expected


def test_currency_possessive_declension():
    # €5eko: the relational -ko attaches to the vowel-final word euro (no
    # epenthetic e), giving euroko, not *euroeko
    assert normalize_units("€5eko sarrera") == "bost euroko sarrera"


# --- units ----------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("5 km", "bost kilometro"),
    ("5km", "bost kilometro"),
    ("3 kg", "hiru kilogramo"),
    ("10 m", "hamar metro"),
    ("1 km", "kilometro bat"),        # postposed bat
])
def test_units(text, expected):
    assert normalize_units(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("3 km-ra", "hiru kilometrora"),          # adlative on the unit word
    ("50 kg-ko", "berrogeita hamar kilogramoko"),
])
def test_unit_declension_on_word(text, expected):
    assert normalize_units(text) == expected


def test_symbol_not_a_prefix_of_a_word():
    # "5 metro" is already a word; "m" must not eat the leading letter
    assert normalize_units("5 metro") == "5 metro"


def test_longest_symbol_wins():
    # "min" is a unit; the "m" alternative must not match first
    assert normalize_units("5 min") == "bost minutu"


def test_table_is_data_driven():
    assert UNITS["km"] == "kilometro"
    assert UNITS["€"] == "euro"
