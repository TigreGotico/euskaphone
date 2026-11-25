"""Language tags reach a lect through linguatag, in every spelling."""
import pytest
from orthography2ipa import resolve

from euskaphone import EuskaPhonemizer, resolve_lect
from euskaphone.codeswitch import _contact_engine


@pytest.mark.parametrize("tag,code", [
    ("eu_x_zuberera", "eu-x-zuberera"),
    ("EU_X_BIZKAIERA", "eu-x-bizkaiera"),
    ("eu-FR-x-zuberera", "eu-x-zuberera"),
    ("  eu_x_nafarra_garaia ", "eu-x-nafarra-garaia"),
])
def test_a_documented_code_in_any_spelling_names_its_spec(tag, code):
    assert resolve_lect(tag) == resolve(code)


@pytest.mark.parametrize("tag", ["eu-Cyrl", "es", "eu--ES"])
def test_a_tag_that_is_not_basque_is_not_supported(tag):
    assert not EuskaPhonemizer.is_supported(tag)


@pytest.mark.parametrize("tag", ["eu_ES", "eu_FR", "eus", "baq", "eu_x_zuberera", "EU-Latn"])
def test_a_spelling_of_basque_is_supported(tag):
    assert EuskaPhonemizer.is_supported(tag)


@pytest.mark.parametrize("contact,tag", [
    ("es", "es-ES"), ("fr", "fr-FR"), ("en", "en-GB"),
])
def test_a_contact_language_reads_its_default_region(contact, tag):
    assert _contact_engine(contact).lang == tag


def test_normalize_dialect_code_is_deprecated_and_keeps_its_value():
    from euskaphone.registry import normalize_dialect_code
    with pytest.warns(DeprecationWarning, match="removed in euskaphone"):
        assert normalize_dialect_code("  Eu-X-Zuberera ") == "eu-x-zuberera"


@pytest.mark.xfail(strict=True, reason="TigreGotico/linguatag#69: every private-use subtag drops at once; "
                   "RFC 4647 §3.4 removes one subtag at a time")
def test_an_unnamed_subtag_after_a_lect_keeps_the_lect():
    assert resolve_lect("eu-x-zuberera-foo") == "eu-x-zuberera"


@pytest.mark.xfail(strict=True, reason="TigreGotico/euskaphone#112: the alias table reads the whole tag only")
@pytest.mark.parametrize("tag,lect", [
    ("eu-x-bizkaiera-foo", "eu-biscayan"),
    ("souletin-foo", "eu-x-zuberera"),
])
def test_an_unnamed_subtag_after_an_alias_keeps_its_lect(tag, lect):
    assert resolve_lect(tag) == lect


def test_normalize_dialect_code_warns_on_every_call():
    from euskaphone.registry import normalize_dialect_code
    for _ in range(2):
        with pytest.warns(DeprecationWarning):
            normalize_dialect_code("eu-ES")
