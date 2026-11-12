"""The engine reads a number as the words that euskaphone writes for it.

The expected value comes from a plain call: the same engine path reading the
text that :func:`euskaphone.normalize.normalize_text` writes out.
"""
import pytest

from euskaphone.lattice_core import phonemize
from euskaphone.normalize import normalize_text


@pytest.mark.parametrize("text", ["3 katu ditut", "21 urte", "XX. mendea", "45,5 euro"])
def test_phonemize_reads_the_expanded_text(text):
    expanded = normalize_text(text, "eu")
    assert expanded != text
    assert phonemize(text, "eu", contact="none") == phonemize(expanded, "eu", contact="none")
