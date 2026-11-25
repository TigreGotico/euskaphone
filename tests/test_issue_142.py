"""Native Basque words with ñ stay on the Basque route under the detector."""

import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.langdetect import get_detector

# Euskaltzaindia rule 17 lists ñ in the Basque alphabet; both words are native.
_NATIVE = ["ñabardura", "Añorga"]


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
    # A fix that stops routing for every word breaks this loan.
    assert (phonemizer.phonemize_sentence("software", contact="auto")
            != phonemizer.phonemize_sentence("software", contact="none"))
