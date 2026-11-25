"""<ph> is not a Basque spelling, so smartphone takes the English route."""

import re

import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.codeswitch import route_token


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#121: smartphone stays off the English route and reads ph as p")
def test_smartphone_takes_the_english_route():
    assert route_token("smartphone", "auto") == "en"
    ipa = EuskaPhonemizer().phonemize_sentence("smartphone", contact="auto")
    assert not re.search(r"p[aeiou]", ipa.replace("ˈ", "")), ipa
