"""Spanish <gu> before <e> is /g/ with a silent <u>, so the Basque route is wrong."""

import re

import pytest

from euskaphone import EuskaPhonemizer


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#119: Miguel stays on the Basque route and keeps its silent u")
def test_gue_has_a_silent_u():
    ipa = EuskaPhonemizer().phonemize_sentence(
        "Miguel Indurain txirrindularia da.", contact="auto")
    first = ipa.split()[0].replace("ˈ", "")
    assert not re.search(r"[gɡɣ]ue", first), ipa
