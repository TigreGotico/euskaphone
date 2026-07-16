"""Northern Bizkaian pitch-accent lexicon and annotation."""
import pytest

from euskaphone import EuskaPhonemizer, AccentClass, default_lexicon
from euskaphone.pitch_accent import (
    ACCENT_MARK, annotate, mark_ipa,
)


@pytest.fixture(scope="module")
def lex():
    return default_lexicon()


def test_lexicon_loads_and_every_entry_is_cited(lex):
    entries = lex.entries()
    assert entries, "shipped lexicon is empty"
    for e in entries:
        assert e.source.strip(), f"{e.word} lacks a citation"
        if e.accent_class is AccentClass.ACCENTED:
            assert e.accent_syllable and e.accent_syllable >= 1
        else:
            assert e.accent_class is AccentClass.UNACCENTED
            assert e.accent_syllable is None


@pytest.mark.parametrize("word,syllable", [
    ("amuma", 2),      # amúma
    ("kipula", 2),     # kipúla
    ("makila", 2),     # makíla
    ("liburu", 1),     # líburu
    ("antzar", 1),     # ántzar
    ("belarri", 1),    # bélarri
])
def test_accented_words_carry_expected_syllable(lex, word, syllable):
    entry = lex.lookup(word)
    assert entry.accent_class is AccentClass.ACCENTED
    assert entry.accent_syllable == syllable


@pytest.mark.parametrize("word", ["lagun", "kale", "txakur", "etxe"])
def test_unaccented_words(lex, word):
    assert lex.lookup(word).accent_class is AccentClass.UNACCENTED


def test_unknown_is_distinct_from_unaccented(lex):
    entry = lex.lookup("mahaia")  # a real Batua word, simply not attested here
    assert entry.accent_class is AccentClass.UNKNOWN
    assert entry.accent_class is not AccentClass.UNACCENTED


def test_lookup_is_punctuation_and_diacritic_tolerant(lex):
    assert lex.lookup("Amúma,").accent_class is AccentClass.ACCENTED
    assert lex.lookup("KIPULA").accent_class is AccentClass.ACCENTED


def test_mark_ipa_places_mark_before_target_syllable():
    # maˈkila: mark before the 2nd syllable
    assert mark_ipa("makila", 2) == "ma" + ACCENT_MARK + "kila"
    assert mark_ipa("makila", 1) == ACCENT_MARK + "makila"


def test_mark_ipa_out_of_range_is_left_unmarked():
    assert mark_ipa("makila", 9) == "makila"
    assert mark_ipa("makila", 0) == "makila"


def test_annotate_only_marks_accented_words(lex):
    assert ACCENT_MARK in annotate("amuma", "amuma", lex)
    assert ACCENT_MARK not in annotate("lagun", "laɡun", lex)   # unaccented
    assert ACCENT_MARK not in annotate("mahaia", "maaia", lex)  # unknown


def test_phonemize_sentence_pitch_accent_marks_accented_words():
    ph = EuskaPhonemizer()
    out = ph.phonemize_sentence(
        "Amuma etxean dago.", "biscayan", contact="none", pitch_accent=True)
    assert ACCENT_MARK in out
    # the accented word is amúma -> aˈmuma
    assert "aˈmuma" in out


def test_pitch_accent_leaves_unaccented_sentence_unmarked():
    ph = EuskaPhonemizer()
    out = ph.phonemize_sentence(
        "Lagun bat etorri da.", "biscayan", contact="none", pitch_accent=True)
    assert ACCENT_MARK not in out


def test_pitch_accent_rejected_for_non_biscayan_lects():
    ph = EuskaPhonemizer()
    for dialect in ["eu", "souletin", "eu-x-gipuzkera"]:
        with pytest.raises(ValueError):
            ph.phonemize_sentence("Amuma", dialect, pitch_accent=True)


def test_pitch_accent_off_by_default_matches_plain_transcription():
    ph = EuskaPhonemizer()
    plain = ph.phonemize_sentence("Kipula eta makila.", "biscayan",
                                  contact="none")
    assert ACCENT_MARK not in plain
