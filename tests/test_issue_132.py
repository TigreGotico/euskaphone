"""A stress acute on a Souletin word is notation, not a sign of a foreign word."""

import pytest

from euskaphone import EuskaPhonemizer

SOULETIN = "eu-x-zuberera"


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#132: stress-marked Souletin words take the French route "
           "under contact=auto and lose /ɡ/, final /n/ and /h/")
@pytest.mark.parametrize("word", ["lagünék", "ginén", "héri"])
def test_stress_marked_souletin_word_stays_on_the_basque_route(classifier, word):
    ph = EuskaPhonemizer(toponyms=False)
    assert (ph.phonemize_sentence(word, SOULETIN, contact="auto")
            == ph.phonemize_sentence(word, SOULETIN, contact="none"))
