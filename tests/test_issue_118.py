"""A tag with extra subtags after an orthography2ipa key keeps that key's lect."""

import pytest
from orthography2ipa import available_codes

from euskaphone import resolve_lect


@pytest.mark.xfail(
    strict=True,
    reason="euskaphone#118: resolve_lect falls back to eu for an "
           "orthography2ipa key followed by extra subtags")
@pytest.mark.parametrize("key", [
    "eu-x-lapurdi", "eu-x-gipuzkoa", "eu-x-roncal", "eu-biscayan",
])
def test_key_with_extra_subtags_keeps_its_lect(key):
    assert key in available_codes()
    assert resolve_lect(f"{key}-foo") == key
