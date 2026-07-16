"""Dialect resolution: codes, human-readable aliases, and contact defaults."""
import pytest

from euskaphone.registry import (
    default_contact, dialect_aliases, is_continental, list_dialects,
    resolve_lect,
)

_EXPECTED = {
    "eu", "eu-x-bizkaiera", "eu-x-gipuzkera", "eu-x-lapurtera",
    "eu-x-nafarra-garaia", "eu-x-nafarra-beherea", "eu-x-zuberera",
    "eu-x-erronkariera",
}


def test_all_eight_dialects_present():
    assert set(list_dialects()) == _EXPECTED


@pytest.mark.parametrize("name,code", [
    ("eu", "eu"),
    ("batua", "eu"),
    ("EU", "eu"),
    ("souletin", "eu-x-zuberera"),
    ("zuberera", "eu-x-zuberera"),
    ("biscayan", "eu-x-bizkaiera"),
    ("Bizkaiera", "eu-x-bizkaiera"),
    ("guipuzcoan", "eu-x-gipuzkera"),
    ("labourdin", "eu-x-lapurtera"),
    ("high-navarrese", "eu-x-nafarra-garaia"),
    ("low-navarrese", "eu-x-nafarra-beherea"),
    ("roncalese", "eu-x-erronkariera"),
])
def test_alias_resolution(name, code):
    assert resolve_lect(name) == code


def test_unknown_falls_back_to_batua():
    assert resolve_lect("klingon") == "eu"
    assert resolve_lect("") == "eu"
    assert resolve_lect("eu-x-unknown") == "eu"


def test_aliases_are_readonly_copy():
    a = dialect_aliases()
    a["souletin"] = "tampered"
    assert resolve_lect("souletin") == "eu-x-zuberera"


def test_continental_vs_peninsular_contact_default():
    # continental (Iparralde) dialects -> French; peninsular -> Spanish
    assert is_continental("eu-x-zuberera")
    assert is_continental("eu-x-lapurtera")
    assert is_continental("eu-x-nafarra-beherea")
    assert not is_continental("eu")
    assert not is_continental("eu-x-bizkaiera")
    assert default_contact("souletin") == "fr"
    assert default_contact("eu") == "es"
    assert default_contact("biscayan") == "es"
