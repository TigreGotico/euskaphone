"""Spanish words with ñ take Spanish stress; native Basque ñ words stay Basque."""

import pytest

from euskaphone import EuskaPhonemizer

# RAE, Ortografía de la lengua española (2010), on the written accent: a word
# without a written accent that ends in a vowel, n or s takes stress on the
# penultimate syllable. Each word below has two syllables.
_SPANISH = ["Peña", "niño", "Doña", "año", "sueño"]

# Euskaltzaindia rule 17 lists ñ in the Basque alphabet.
_BASQUE = ["Iñaki", "andereño", "Begoña"]


@pytest.mark.xfail(
    strict=True,
    reason="https://github.com/TigreGotico/euskaphone/issues/139: Spanish words "
           "with ñ take Basque second-syllable stress under contact=auto")
def test_spanish_ñ_words_take_stress_on_the_first_syllable(classifier):
    phonemizer = EuskaPhonemizer()
    for word in _SPANISH:
        ipa = phonemizer.phonemize_sentence(word, contact="auto")
        assert ipa.startswith("ˈ"), (word, ipa)
    # A fix that stresses every ñ word on its first syllable breaks these.
    for word in _BASQUE:
        assert (phonemizer.phonemize_sentence(word, contact="auto")
                == phonemizer.phonemize_sentence(word, contact="none")), word
