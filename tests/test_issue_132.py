"""A stress acute on a Souletin word is notation, not a sign of a foreign word."""

import warnings

import pytest
from orthography2ipa import UnmappedGraphemeWarning

from euskaphone import EuskaPhonemizer

SOULETIN = "eu-x-zuberera"


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#132: stress-marked Souletin words take the French route "
           "under contact=auto and lose /ɡ/, final /n/ and /h/")
@pytest.mark.parametrize("word", ["lagünék", "ginén", "héri"])
def test_stress_marked_souletin_word_stays_on_the_basque_route(classifier, word):
    ph = EuskaPhonemizer(toponyms=False)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        auto = ph.phonemize_sentence(word, SOULETIN, contact="auto")
        none = ph.phonemize_sentence(word, SOULETIN, contact="none")
    assert auto == none
    assert not [w for w in caught if issubclass(w.category, UnmappedGraphemeWarning)]
    assert "e" in auto
