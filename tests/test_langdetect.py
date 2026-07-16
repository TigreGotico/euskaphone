"""Char-Markov word-level language detector and its code-switch integration."""
import pytest

from euskaphone.langdetect import (
    DEFAULT_MARGIN, LANGS, MarkovLangDetector, _normalize, get_detector,
)

pytestmark = pytest.mark.skipif(
    get_detector() is None,
    reason="markovonnx or bundled langdetect models unavailable",
)


def det() -> MarkovLangDetector:
    d = get_detector()
    assert d is not None
    return d


def test_normalize_strips_and_lowercases():
    assert _normalize("Plaza,") == "plaza"
    assert _normalize("Château!") == "château"
    assert _normalize("1936ko") == "ko"  # digits dropped
    assert _normalize("123") == ""


def test_scores_cover_all_languages():
    scores = det().score("etxean")
    assert set(scores) == set(LANGS)
    assert all(isinstance(v, float) for v in scores.values())


@pytest.mark.parametrize("word", ["etxean", "hogeita", "kaixo", "zuri", "ditut"])
def test_native_basque_words_stay_eu(word):
    lang, _ = det().detect(word)
    assert lang == "eu"
    assert det().is_contact(word) is False


@pytest.mark.parametrize("word", ["monsieur", "toujours", "beaucoup"])
def test_clear_french_words_detected_as_contact(word):
    assert det().is_contact(word) is True


@pytest.mark.parametrize("word", ["señora", "ayuntamiento", "corazón"])
def test_clear_spanish_words_detected_as_contact(word):
    assert det().is_contact(word) is True


def test_empty_and_punctuation_are_basque():
    lang, scores = det().detect("...")
    assert lang == "eu"
    assert scores == {}


def test_margin_is_in_language_default():
    # A higher margin can only keep MORE words as eu, never fewer.
    d = det()
    words = ["general", "hotel", "radio", "central", "natural", "capital"]
    low = [d.detect(w, margin=0.0)[0] for w in words]
    high = [d.detect(w, margin=1.5)[0] for w in words]
    # with a very large margin, everything defaults back to eu
    assert all(l == "eu" for l in high)
    # and the default margin never routes MORE than a zero margin would
    default = [d.detect(w, margin=DEFAULT_MARGIN)[0] for w in words]
    for lo, de in zip(low, default):
        if de != "eu":
            assert lo != "eu"


def test_internationalisms_are_handled_by_the_margin_band():
    # Genuinely ambiguous shared-alphabet internationalisms sit near the eu
    # boundary. Some (radio) fall inside the margin band and stay Basque;
    # others are orthographically more Romance/English and route to a contact
    # language — where total nativization projects them back onto the Basque
    # inventory anyway, so either outcome is safe. The margin guarantees the
    # decision is never made on a weak signal: at a large margin they all fall
    # back to eu.
    d = det()
    words = ["hotel", "general", "radio", "natural", "capital"]
    assert all(d.detect(w, margin=2.0)[0] == "eu" for w in words)
    # radio is a documented boundary case that stays Basque at the default.
    assert d.detect("radio")[0] == "eu"


# -- integration with the code-switch router --------------------------------

def test_split_runs_uses_detector():
    from euskaphone.codeswitch import split_runs
    runs = split_runs("Madrilen ayuntamiento ikusi dut", "es")
    routing = {tok: is_c for is_c, tok in runs}
    assert routing["ayuntamiento"] is True   # Spanish -> contact
    assert routing["ikusi"] is False          # Basque -> native
    assert routing["dut"] is False


def test_split_runs_none_disables_detection():
    from euskaphone.codeswitch import split_runs
    runs = split_runs("ayuntamiento etxean", "none")
    assert all(not is_c for is_c, _ in runs)


def test_mixed_sentence_phonemizes(monkeypatch):
    from euskaphone import EuskaPhonemizer
    ph = EuskaPhonemizer()
    out = ph.phonemize_sentence("Madrilen ayuntamiento ikusi dut.", "eu")
    assert out and isinstance(out, str)
