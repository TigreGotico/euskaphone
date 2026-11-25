"""Native Basque words with ñ stay on the Basque route under the detector."""

import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.langdetect import get_detector

# Euskaltzaindia rule 17 lists ñ in the Basque alphabet; both words are native.
_NATIVE = ["ñabardura", "Añorga"]

_DETECTOR_ONLY = ["gobierno", "mañana"]


@pytest.mark.skipif(get_detector() is None, reason="needs the char-Markov detector")
@pytest.mark.xfail(
    strict=True,
    reason="https://github.com/TigreGotico/euskaphone/issues/142: the detector "
           "sends native ñ words off the Basque route")
def test_detector_keeps_native_ñ_words_on_the_basque_route():
    phonemizer = EuskaPhonemizer()
    for word in _NATIVE:
        assert (phonemizer.phonemize_sentence(word, contact="auto")
                == phonemizer.phonemize_sentence(word, contact="none")), word
    # Only the detector routes these Spanish words: no orthographic signal marks
    # them. A fix that ignores the detector, or skips it for ñ words, breaks them.
    for word in _DETECTOR_ONLY:
        assert (phonemizer.phonemize_sentence(word, contact="auto")
                != phonemizer.phonemize_sentence(word, contact="none")), word
