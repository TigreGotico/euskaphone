"""Code-switch detection, routing and nativization onto the Basque inventory."""
import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.codeswitch import (
    _nativize, contact_language, is_contact_word, split_runs,
    transcribe_contact,
)

#: Phones the Basque inventory does not contain; nativization must remove them.
_NON_BASQUE = ("θ", "ð", "v", "z", "ʒ", "ʁ", "ʀ", "χ", "ɔ", "ɛ", "ə", "ø", "œ",
               "w", "ɹ", "ŋ", "æ", "ʌ", "ɪ", "ʊ", "ˈ", "ˌ", "ː")


@pytest.mark.parametrize("word,expected", [
    ("etxean", False),      # native Basque
    ("hogeita", False),
    ("Plaza", False),       # z is a native Basque letter -> not flagged
    ("Mayor", True),        # y not native
    ("corazón", True),      # c, ó, z, ñ-adjacent
    ("français", True),     # ç, french
    ("el", True),           # Spanish stopword
    ("les", True),          # French stopword
    ("streaming", True),    # English digraph + stopword
    ("weekend", True),      # English (w + ee)
    ("software", True),     # English stopword
    ("kaixo", False),
])
def test_is_contact_word(word, expected):
    assert is_contact_word(word) == expected


@pytest.mark.parametrize("word,expected", [
    ("streaming", "en"),
    ("weekend", "en"),
    ("the", "en"),
    ("français", "fr"),
    ("cette", "fr"),
    ("corazón", "es"),
    ("mañana", "es"),
    ("plaza", "es"),        # no language signal -> default side (es)
])
def test_contact_language_classifies_per_word(word, expected):
    assert contact_language(word, "es") == expected


def test_contact_language_default_side_is_used():
    # a signal-less contact token follows the dialect's geographic side
    assert contact_language("plaza", "fr") == "fr"
    assert contact_language("plaza", "es") == "es"


def test_nativize_projects_out_foreign_phones():
    # Castilian "plaza" /ˈplaθa/ and French "rouge" /ʁuʒ/
    for foreign in ("ˈplaθa", "ʁuʒ", "kɔʁazɔn", "vɛʁy"):
        out = _nativize(foreign)
        assert not any(p in out for p in _NON_BASQUE), out


def test_nativize_english_projects_out_foreign_phones():
    # English "think" /θɪŋk/, "weekend" /wiːkɛnd/, "software" /sɒftwɛəɹ/
    for foreign in ("θɪŋk", "wiːkɛnd", "sɒftwɛəɹ", "stɹiːmɪŋ"):
        out = _nativize(foreign, english=True)
        assert not any(p in out for p in _NON_BASQUE), out


def test_nativize_english_th_stopping_and_glide():
    assert _nativize("θ", english=True) == "t"
    assert _nativize("ð", english=True) == "d"
    assert _nativize("w", english=True) == "u̯"
    assert _nativize("ŋ", english=True) == "n"


def test_nativize_keeps_all_segments():
    # total nativization: never drop, always project -> non-empty projection
    assert _nativize("θ") == "s̻"
    assert _nativize("v") == "b"
    assert len(_nativize("ʁuʒ")) >= 3


def test_transcribe_contact_es_stays_in_basque_inventory():
    out = transcribe_contact("plaza", "es")
    assert out
    assert not any(p in out for p in _NON_BASQUE)


def test_transcribe_contact_fr_stays_in_basque_inventory():
    out = transcribe_contact("rouge", "fr")
    assert out
    assert not any(p in out for p in _NON_BASQUE)


def test_transcribe_contact_en_stays_in_basque_inventory():
    for word in ("streaming", "weekend", "software", "download"):
        out = transcribe_contact(word, "en")
        assert out
        assert not any(p in out for p in _NON_BASQUE), (word, out)


def test_souletin_keeps_y():
    # Zuberera has /y/, so nativization there may preserve it
    with_y = _nativize("y", keep_y=True)
    without_y = _nativize("y", keep_y=False)
    assert with_y == "y"
    assert without_y == "i"


def test_split_runs_none_disables_switching():
    runs = split_runs("Plaza Mayor etxean", "none")
    assert all(lang is None for lang, _ in runs)


def test_split_runs_detects_contact():
    runs = split_runs("Mayor etxean", "es")
    assert runs[0][0] == "es"     # Mayor -> contact routed to es
    assert runs[1][0] is None     # etxean -> Basque


def test_split_runs_auto_routes_per_word():
    # one English, one French, one Spanish, one Basque token
    runs = dict((tok, lang)
                for lang, tok in split_runs(
                    "streaming français corazón etxean", "auto", "es"))
    assert runs["streaming"] == "en"
    assert runs["français"] == "fr"
    assert runs["corazón"] == "es"
    assert runs["etxean"] is None


def test_english_sentence_stays_in_inventory():
    ph = EuskaPhonemizer(toponyms=False)
    out = ph.phonemize_sentence("Streaming plataforma berria da.", contact="auto")
    assert out
    assert not any(p in out for p in _NON_BASQUE), out


def test_en_forced_contact_is_valid():
    ph = EuskaPhonemizer(toponyms=False)
    out = ph.phonemize_sentence("The weekend rock band.", contact="en")
    assert out
    assert not any(p in out for p in _NON_BASQUE), out
