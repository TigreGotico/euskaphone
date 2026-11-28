"""A tag with extra subtags after an orthography2ipa key keeps that key's lect."""

import pytest
from orthography2ipa import available_codes

from euskaphone import resolve_lect


_KEYS = ["eu-x-lapurdi", "eu-x-gipuzkoa", "eu-x-roncal", "eu-biscayan"]


def test_keys_are_listed():
    assert set(_KEYS) <= set(available_codes())


@pytest.mark.parametrize("key", _KEYS)
def test_key_with_extra_subtags_keeps_its_lect(key):
    assert resolve_lect(f"{key}-foo") == key
