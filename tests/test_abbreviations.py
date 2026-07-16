"""Abbreviation expansion — cited to the standard laburdura list.

Expected expansions are the forms fixed by Euskaltzaindia Araua 196 and the EIMA
*Ortotipografia* style guide (see ``euskaphone/data/abbreviations.tsv``).
"""
import pytest

from euskaphone.abbreviations import (
    ABBREVIATIONS, expand_abbreviations, expand_token,
)


@pytest.mark.parametrize("token,expected", [
    ("etab.", "eta abar"),          # the fixed et-cetera abbreviation
    ("adib.", "adibidez"),
    ("h.d.", "hau da"),             # multi-dot abbreviation
    ("zk.", "zenbakia"),
    ("or.", "orrialdea"),
    ("kap.", "kapitulua"),
    ("K.a.", "Kristo aurretik"),    # era abbreviation, mixed case
    ("K.o.", "Kristo ondoren"),
    ("jn.", "jauna"),
])
def test_known_abbreviations(token, expected):
    assert expand_token(token) == expected


def test_case_insensitive():
    # the written form matches regardless of case
    assert expand_token("ETAB.") == "eta abar"
    assert expand_token("k.a.") == "Kristo aurretik"


def test_bare_form_without_period():
    # a tokenizer that split the period off still resolves
    assert expand_token("etab") == "eta abar"
    assert expand_token("zk") == "zenbakia"


def test_non_abbreviation_untouched():
    assert expand_token("katua") == "katua"
    assert expand_token("bat") == "bat"


def test_expand_in_running_text():
    out = expand_abbreviations("Katuak, txakurrak, etab.")
    assert "eta abar" in out
    assert "Katuak," in out  # non-abbreviation words preserved


def test_multiword_expansion_flows_as_words():
    # K.a. expands to two words that then reach the lattice individually
    assert expand_abbreviations("K.a. 50") == "Kristo aurretik 50"


def test_table_is_data_driven_and_nonempty():
    assert ABBREVIATIONS  # loaded from the tsv
    assert ABBREVIATIONS["etab."] == "eta abar"
