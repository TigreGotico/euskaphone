"""Vigesimal number verbalization — round-trips against cited Araua 7/18 forms.

Every expected string here is either spelled verbatim in Euskaltzaindia Araua 7
("Zenbakien idazkeraz") / Araua 18 ("Ordinalen … idazkera") or composed by the
attested vigesimal + ``eta`` rule those arauak state.
"""
import pytest

from euskaphone.number_utils import BasqueNumberParser, normalize_numbers


@pytest.mark.parametrize("n,expected", [
    (0, "zero"),
    (1, "bat"),
    (2, "bi"),
    (5, "bost"),
    (10, "hamar"),
    (11, "hamaika"),          # irregular, not *hamabat
    (15, "hamabost"),
    (18, "hemezortzi"),       # irregular hama- -> heme-
    (19, "hemeretzi"),
    (20, "hogei"),
    (21, "hogeita bat"),      # eta -> -ta on the twenty head
    (25, "hogeita bost"),
    (30, "hogeita hamar"),    # Araua 7: always spaced, never *hogeitamar
    (31, "hogeita hamaika"),  # 20-and-11
    (40, "berrogei"),
    (50, "berrogeita hamar"),
    (60, "hirurogei"),
    (70, "hirurogeita hamar"),
    (75, "hirurogeita hamabost"),
    (80, "laurogei"),
    (90, "laurogeita hamar"),
    (99, "laurogeita hemeretzi"),
    (100, "ehun"),
    (101, "ehun eta bat"),
    (200, "berrehun"),
    (300, "hirurehun"),
    (400, "laurehun"),
    (500, "bostehun"),
    (900, "bederatziehun"),
    (1000, "mila"),
    (1001, "mila eta bat"),
    (1200, "mila eta berrehun"),     # eta kept before a bare hundreds multiple
    (1202, "mila berrehun eta bi"),  # eta drops when a lower remainder follows
    (1936, "mila bederatziehun eta hogeita hamasei"),
    (1984, "mila bederatziehun eta laurogeita lau"),
    (1000000, "milioi bat"),
    (2000000, "bi milioi"),
])
def test_cardinal(n, expected):
    assert BasqueNumberParser("eu").cardinal(n) == expected


@pytest.mark.parametrize("n,expected", [
    (1, "lehenengo"),        # suppletive, no -garren
    (2, "bigarren"),
    (5, "bosgarren"),        # bost -> bos- (Araua 18, not *bostgarren)
    (10, "hamargarren"),
    (16, "hamaseigarren"),
    (20, "hogeigarren"),     # attested verbatim in Araua 18
    (100, "ehungarren"),
])
def test_ordinal(n, expected):
    assert BasqueNumberParser("eu").ordinal(n) == expected


def test_negative_and_decimal():
    p = BasqueNumberParser("eu")
    assert p.cardinal(-3) == "minus hiru"
    assert p.decimal(3, "14") == "hiru koma bat lau"


def test_lapurdian_bortz_series():
    # Araua 7 point 3: bortz is attested in some Iparralde varieties.
    p = BasqueNumberParser("eu-x-lapurtera")
    assert p.cardinal(5) == "bortz"
    assert p.cardinal(15) == "hamabortz"
    assert p.cardinal(500) == "bortzehun"


def test_peninsular_and_souletin_keep_bost():
    # Araua 7 explicitly records bost for Zuberoa and most of Low Navarre.
    for code in ("eu", "eu-x-zuberera", "eu-x-nafarra-beherea",
                 "eu-x-bizkaiera"):
        assert BasqueNumberParser(code).cardinal(5) == "bost"


def test_unknown_dialect_rejected():
    with pytest.raises(ValueError):
        BasqueNumberParser("xx")


# -- running-text normalization -------------------------------------------

def test_normalize_plain_and_year():
    assert normalize_numbers("31 katu", "eu") == "hogeita hamaika katu"
    # year read as a plain cardinal (Araua 18)
    assert normalize_numbers("1936 urtea", "eu") == \
        "mila bederatziehun eta hogeita hamasei urtea"


def test_normalize_case_suffix_attaches_to_last_element():
    # 1936ko -> ...hogeita hamaseiko  (declension on the final element)
    assert normalize_numbers("1936ko gerra", "eu") == \
        "mila bederatziehun eta hogeita hamaseiko gerra"


def test_normalize_time_inessive():
    # 20:00etan -> hogeietan (plural inessive on the final numeral element)
    assert normalize_numbers("20:00etan", "eu") == "hogeietan"
    assert normalize_numbers("20:10ean", "eu") == "hogei eta hamarrean" \
        or normalize_numbers("20:10ean", "eu") == "hogei eta hamarean"


def test_normalize_explicit_ordinal():
    assert normalize_numbers("16garren", "eu") == "hamaseigarren"


def test_normalize_leaves_non_numeric_untouched():
    assert normalize_numbers("kaixo mundua", "eu") == "kaixo mundua"


# -- separator handling (European/Basque convention) ----------------------

@pytest.mark.parametrize("token,expected", [
    # comma = decimal separator
    ("2,5", "bi koma bost"),
    ("2,05", "bi koma zero bost"),         # leading zero preserved
    # period = thousands separator
    ("1.000.000", "milioi bat"),
    ("2.500", "bi mila eta bostehun"),      # period + 3 digits = thousands
    ("12.345", "hamabi mila hirurehun eta berrogeita bost"),
    # a lone period that is not a 3-digit grouping falls back to a decimal point
    ("2.5", "bi koma bost"),
    # thousands grouping in the whole part of a comma-decimal
    ("1.234,5", "mila berrehun eta hogeita hamalau koma bost"),
])
def test_separator_matrix(token, expected):
    assert normalize_numbers(token, "eu") == expected


def test_space_separated_thousands():
    # space = thousands separator; collapsed before tokenization
    assert normalize_numbers("1 000 000 lagun", "eu") == "milioi bat lagun"
    assert normalize_numbers("2 500 metro", "eu") == "bi mila eta bostehun metro"


def test_million_no_longer_dropped():
    # regression: "1.000.000 euro" used to drop the number entirely
    assert normalize_numbers("1.000.000 euro", "eu") == "milioi bat euro"


def test_lapurdian_bortz_in_running_text():
    assert normalize_numbers("15 katu", "eu-x-lapurtera") == "hamabortz katu"
