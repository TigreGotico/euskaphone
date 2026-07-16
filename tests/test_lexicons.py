"""Shipped toponym seed (opt-out) and HiTZ overlay (opt-in) lexicons."""
import os

import pytest

import orthography2ipa.lexicon as _lex
from euskaphone import EuskaPhonemizer, register_lexicon
from euskaphone.lexicons import (
    HITZ_OVERLAY_LEXICON, TOPONYM_LEXICON, hitz_overlay_words,
    register_hitz_overlay, register_toponyms,
)
from orthography2ipa.lexicon import parse_lexicon_text, validate_lexicon_text


@pytest.fixture(autouse=True)
def _clean_lexicons():
    _lex.clear_lexicons()
    yield
    _lex.clear_lexicons()


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_shipped_lexicons_exist_and_are_valid():
    for path in (TOPONYM_LEXICON, HITZ_OVERLAY_LEXICON):
        assert os.path.isfile(path), path
        text = _read(path)
        assert validate_lexicon_text(text) == [], path


def test_toponym_seed_has_a_meaningful_size():
    entries = parse_lexicon_text(_read(TOPONYM_LEXICON))
    assert len(entries) >= 100
    # a few normative anchors must be present
    for key in ("bilbo", "gasteiz", "donostia", "iruñea", "baiona"):
        assert key in entries


def test_toponyms_registered_by_default():
    ph = EuskaPhonemizer()  # toponyms=True (opt-out default)
    # an explicit foreign-spelled entry is only produced via the lexicon
    assert ph.phonemize_sentence("hollywood", "eu", contact="none") == "oliu̯ud"


def test_toponyms_opt_out():
    EuskaPhonemizer(toponyms=False)
    assert "eu" not in _lex.available_lexicon_codes()


def test_toponyms_do_not_clobber_caller_lexicon(tmp_path):
    mine = tmp_path / "mine.tsv"
    mine.write_text("gasteiz\tabab\n", encoding="utf-8")
    register_lexicon("eu", str(mine))
    # constructing with toponyms=True must NOT overwrite the caller's lexicon
    EuskaPhonemizer(toponyms=True)
    assert _lex.get_lexicon("eu")["gasteiz"] == "abab"


def test_hitz_overlay_opt_in_only():
    EuskaPhonemizer()  # default: no overlay
    reg = getattr(_lex, "_REGISTERED", {})
    assert reg.get("eu") == TOPONYM_LEXICON
    _lex.clear_lexicons()
    EuskaPhonemizer(lexicon="hitz")
    assert getattr(_lex, "_REGISTERED", {}).get("eu") == HITZ_OVERLAY_LEXICON


def test_hitz_overlay_words_match_file_keys():
    words = hitz_overlay_words()
    assert words
    assert words == frozenset(parse_lexicon_text(_read(HITZ_OVERLAY_LEXICON)))


def test_unknown_lexicon_name_raises():
    with pytest.raises(ValueError):
        EuskaPhonemizer(lexicon="nope")


def test_register_helpers_resolve_alias():
    register_toponyms("batua")  # alias for eu
    assert "eu" in _lex.available_lexicon_codes()
    _lex.clear_lexicons()
    register_hitz_overlay("standard")  # alias for eu
    assert getattr(_lex, "_REGISTERED", {}).get("eu") == HITZ_OVERLAY_LEXICON
