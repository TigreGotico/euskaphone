"""Spanish words with ñ take the Spanish route; native Basque ñ words stay Basque."""

import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.codeswitch import route_token

# RAE, Ortografía de la lengua española (2010): a word without a written accent
# that ends in a vowel, n or s takes stress on the penultimate syllable. Basque
# stress on the second syllable misreads these two-syllable Spanish words. The
# Spanish contact route strips stress (docs/codeswitch.md), so the check is the
# route and the contact="es" reading, not a stress mark.
_SPANISH = ["Peña", "niño", "Doña", "año", "sueño"]

# Euskaltzaindia rule 17 lists ñ in the Basque alphabet.
_BASQUE = ["Iñaki", "Begoña", "andereño"]


@pytest.mark.xfail(
    strict=True,
    reason="https://github.com/TigreGotico/euskaphone/issues/139: Spanish words "
           "with ñ take the Basque route under contact=auto", raises=AssertionError)
def test_spanish_ñ_words_take_the_spanish_route_and_basque_ones_do_not(classifier):
    phonemizer = EuskaPhonemizer()
    for word in _SPANISH:
        assert route_token(word, "auto") == "es", word
        assert (phonemizer.phonemize_sentence(word, contact="auto")
                == phonemizer.phonemize_sentence(word, contact="es")), word
    # A fix that routes every ñ word to Spanish breaks these.
    for word in _BASQUE:
        assert route_token(word, "auto") is None, word
