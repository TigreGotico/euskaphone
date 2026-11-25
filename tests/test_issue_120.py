"""A written acute vowel is a vowel in the output, never dropped."""

import warnings

import pytest

from euskaphone import EuskaPhonemizer

_SENTENCE = "José Andrés Jaénen jaio zen."
_ORTHOGRAPHIC_VOWELS = "aeiouáéíóú"
_IPA_VOWELS = "aeiouɛɔəɐɑɪʊ"


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#120: the lattice drops é with UnmappedGraphemeWarning")
def test_acute_e_is_a_vowel_in_the_output():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ipa = EuskaPhonemizer().phonemize_sentence(_SENTENCE, contact="auto")
    unmapped = [str(w.message) for w in caught
                if "U+00E9" in str(w.message)]
    assert unmapped == []
    written = sum(ch in _ORTHOGRAPHIC_VOWELS for ch in _SENTENCE.lower())
    spoken = sum(ch in _IPA_VOWELS for ch in ipa)
    assert spoken == written, ipa
