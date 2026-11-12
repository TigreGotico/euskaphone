"""Shipped toponym seed (opt-out) and HiTZ overlay (opt-in) lexicons."""
import os
import warnings

import pytest

import orthography2ipa.lexicon as _lex
from euskaphone import EuskaPhonemizer, lattice_core, register_lexicon
from euskaphone.lattice_core import engine, lexicon_source
from euskaphone.lexicons import (
    HITZ_OVERLAY_LEXICON, TOPONYM_LEXICON, hitz_overlay_words,
    register_hitz_overlay, register_toponyms,
)
from orthography2ipa import G2P
from orthography2ipa.lexicon import load_lexicon, parse_lexicon_text, validate_lexicon_text


def _clear_process_lexicons():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        _lex.clear_lexicons()


@pytest.fixture(autouse=True)
def _clean_lexicons(monkeypatch):
    monkeypatch.setattr(lattice_core, "_LEXICONS", {})
    engine.cache_clear()
    _clear_process_lexicons()
    yield
    engine.cache_clear()
    _clear_process_lexicons()


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
    # an explicit foreign-spelled entry is only produced via the lexicon; the
    # lexicon writes no stress, and the eu spec marks the accent on its own
    out = ph.phonemize_sentence("hollywood", "eu", contact="none")
    assert out.replace("ˈ", "") == "oliu̯ud"


def test_toponyms_opt_out():
    EuskaPhonemizer(toponyms=False)
    assert lexicon_source("eu") is None
    assert engine("eu").pipeline.lexicon is None


def test_toponyms_do_not_clobber_caller_lexicon(tmp_path):
    mine = tmp_path / "mine.tsv"
    mine.write_text("gasteiz\tabab\n", encoding="utf-8")
    register_lexicon("eu", str(mine))
    # constructing with toponyms=True must NOT overwrite the caller's lexicon
    EuskaPhonemizer(toponyms=True)
    assert engine("eu").pipeline.lexicon["gasteiz"] == "abab"


def test_toponyms_do_not_clobber_a_process_wide_lexicon(tmp_path):
    """A lexicon the caller set through orthography2ipa's deprecated API wins too."""
    mine = tmp_path / "mine.tsv"
    mine.write_text("gasteiz\tabab\n", encoding="utf-8")
    with pytest.warns(DeprecationWarning):
        _lex.register_lexicon("eu", str(mine))
    ph = EuskaPhonemizer(toponyms=True)
    assert lexicon_source("eu") is None
    assert ph.phonemize_sentence("gasteiz", "eu", contact="none").replace("ˈ", "") == "abab"


def test_a_later_registration_replaces_the_engine_lexicon(tmp_path):
    ph = EuskaPhonemizer()
    assert ph.phonemize_sentence("gasteiz", "eu", contact="none").replace("ˈ", "") != "abab"
    mine = tmp_path / "mine.tsv"
    mine.write_text("gasteiz\tabab\n", encoding="utf-8")
    register_lexicon("eu", str(mine))
    assert ph.phonemize_sentence("gasteiz", "eu", contact="none").replace("ˈ", "") == "abab"


def test_no_other_engine_reads_the_lexicon():
    """The euskaphone engine holds the lexicon. An engine the caller builds for
    the same code reads the rules, as the orthography2ipa contract requires."""
    ph = EuskaPhonemizer()
    assert ph.phonemize_sentence("hollywood", "eu", contact="none").replace("ˈ", "") == "oliu̯ud"
    assert G2P("eu").pipeline.lexicon is None
    assert G2P("eu").transcribe("hollywood").replace("ˈ", "") != "oliu̯ud"


def test_a_missing_lexicon_file_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        register_lexicon("eu", str(tmp_path / "missing.tsv"))
    assert lexicon_source("eu") is None


def test_a_registered_lexicon_outlives_its_file(tmp_path):
    mine = tmp_path / "mine.tsv"
    mine.write_text("gasteiz\tabab\n", encoding="utf-8")
    register_lexicon("eu", str(mine))
    mine.unlink()
    lattice_core.clear_caches()
    assert EuskaPhonemizer().phonemize_sentence("gasteiz", "eu", contact="none").replace("ˈ", "") == "abab"


def test_the_default_setup_uses_no_deprecated_lexicon_api():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        EuskaPhonemizer(lexicon="hitz").phonemize_sentence("gasteiz", "eu", contact="none")
    assert not [w for w in caught if "deprecated" in str(w.message)]


def test_hitz_overlay_opt_in_only():
    EuskaPhonemizer()  # default: no overlay
    assert lexicon_source("eu") == TOPONYM_LEXICON
    assert engine("eu").pipeline.lexicon == load_lexicon(TOPONYM_LEXICON)
    EuskaPhonemizer(lexicon="hitz")
    assert lexicon_source("eu") == HITZ_OVERLAY_LEXICON
    assert engine("eu").pipeline.lexicon == load_lexicon(HITZ_OVERLAY_LEXICON)


def test_hitz_overlay_words_match_file_keys():
    words = hitz_overlay_words()
    assert words
    assert words == frozenset(parse_lexicon_text(_read(HITZ_OVERLAY_LEXICON)))


def test_unknown_lexicon_name_raises():
    with pytest.raises(ValueError):
        EuskaPhonemizer(lexicon="nope")


def test_register_helpers_resolve_alias():
    register_toponyms("batua")  # alias for eu
    assert lexicon_source("eu") == TOPONYM_LEXICON
    register_hitz_overlay("standard")  # alias for eu
    assert lexicon_source("eu") == HITZ_OVERLAY_LEXICON
