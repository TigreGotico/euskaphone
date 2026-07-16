"""Code-switch detection, routing and nativization onto the Basque inventory."""
import pytest

from euskaphone.codeswitch import (
    _nativize, is_contact_word, split_runs, transcribe_contact,
)

#: Phones the Basque inventory does not contain; nativization must remove them.
_NON_BASQUE = ("θ", "v", "z", "ʒ", "ʁ", "ʀ", "χ", "ɔ", "ɛ", "ə", "ø", "œ",
               "ˈ", "ˌ")


@pytest.mark.parametrize("word,expected", [
    ("etxean", False),      # native Basque
    ("hogeita", False),
    ("Plaza", False),       # z is a native Basque letter -> not flagged
    ("Mayor", True),        # y not native
    ("corazón", True),      # c, ó, z, ñ-adjacent
    ("français", True),     # ç, french
    ("el", True),           # Spanish stopword
    ("les", True),          # French stopword
    ("kaixo", False),
])
def test_is_contact_word(word, expected):
    assert is_contact_word(word) == expected


def test_nativize_projects_out_foreign_phones():
    # Castilian "plaza" /ˈplaθa/ and French "rouge" /ʁuʒ/
    for foreign in ("ˈplaθa", "ʁuʒ", "kɔʁazɔn", "vɛʁy"):
        out = _nativize(foreign)
        assert not any(p in out for p in _NON_BASQUE), out


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


def test_souletin_keeps_y():
    # Zuberera has /y/, so nativization there may preserve it
    with_y = _nativize("y", keep_y=True)
    without_y = _nativize("y", keep_y=False)
    assert with_y == "y"
    assert without_y == "i"


def test_split_runs_none_disables_switching():
    runs = split_runs("Plaza Mayor etxean", "none")
    assert all(not is_contact for is_contact, _ in runs)


def test_split_runs_detects_contact():
    runs = split_runs("Mayor etxean", "es")
    assert runs[0][0] is True     # Mayor -> contact
    assert runs[1][0] is False    # etxean -> Basque
