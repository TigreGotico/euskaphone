"""<ph> is not a Basque spelling, so smartphone is not read as p + vowel."""

import re

import pytest

from euskaphone import EuskaPhonemizer


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#121: smartphone stays on the Basque route and reads ph as p")
def test_ph_is_not_read_as_p():
    ipa = EuskaPhonemizer().phonemize_sentence("smartphone", contact="auto")
    assert not re.search(r"p[aeiou]", ipa.replace("ˈ", "")), ipa
