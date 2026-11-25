"""A written acute vowel is a vowel in the output, never dropped."""

import warnings

from euskaphone import EuskaPhonemizer

_SENTENCE = "José Andrés Jaénen jaio zen."
_E_ACUTE_WORDS = ("José", "Andrés", "Jaénen")
_ORTHOGRAPHIC_VOWELS = "aeiouáéíóú"
_IPA_VOWELS = "aeiouɛɔəɐɑɪʊ"


def test_acute_e_is_a_vowel_in_the_output():
    phonemizer = EuskaPhonemizer()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        phonemizer.phonemize_sentence(_SENTENCE, contact="auto")
    unmapped = [str(w.message) for w in caught
                if "U+00E9" in str(w.message)]
    assert unmapped == []
    for word in _E_ACUTE_WORDS:
        written = sum(ch in _ORTHOGRAPHIC_VOWELS for ch in word.lower())
        word_ipa = phonemizer.phonemize_sentence(word, contact="auto")
        spoken = sum(ch in _IPA_VOWELS for ch in word_ipa)
        assert spoken == written, (word, word_ipa)
