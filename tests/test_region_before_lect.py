"""A region before the private-use lect keeps the lect (#160)."""
import pytest

from euskaphone.registry import resolve_lect


@pytest.mark.parametrize("tag, lect", [
    ("eu-ES-x-bizkaiera", "eu-biscayan"),
    ("eu-419-x-bizkaiera", "eu-biscayan"),
    ("eu-FR-x-lapurtera", "eu-x-lapurdi"),
    ("eu-US-x-gipuzkera", "eu-x-gipuzkoa"),
    ("eu-FR-x-zuberera-foo", "eu-x-zuberera"),
    ("eu-FR-x-nafarra-beherea", "eu-x-nafarra-beherea"),
    ("eu-FR-x-unknown", "eu"),
    ("eu-ES", "eu"),
])
def test_resolve_lect_with_a_region(tag, lect):
    assert resolve_lect(tag) == lect
