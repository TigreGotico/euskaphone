"""Top-level package surface."""
import euskaphone
from euskaphone import (
    EuskaPhonemizer, dialect_aliases, list_dialects, register_lexicon,
    resolve_lect,
)


def test_version_is_semver():
    import re
    assert re.fullmatch(r"\d+\.\d+\.\d+(a\d+)?", euskaphone.__version__)


def test_exports():
    for name in ("EuskaPhonemizer", "register_lexicon", "list_dialects",
                 "dialect_aliases", "resolve_lect", "__version__"):
        assert hasattr(euskaphone, name)


def test_is_supported():
    ph = EuskaPhonemizer()
    assert ph.is_supported("eu")
    assert ph.is_supported("souletin")
    assert not ph.is_supported("pt-PT")


def test_default_dialect_is_batua():
    ph = EuskaPhonemizer()
    out = ph.phonemize_sentence("kaixo")
    assert out == ph.phonemize_sentence("kaixo", "eu")


def test_register_lexicon_is_callable():
    # empty by default; the passthrough must resolve the alias without raising
    # (an empty registration is a no-op contract check, not a data load)
    assert callable(register_lexicon)


def test_no_opm_g2p_entry_point():
    # The wrapper does not implement the OPM Grapheme2PhonemePlugin API
    # (config constructor, get_ipa, available_languages), so the package does
    # not advertise it in the "opm.g2p" group.
    from importlib.metadata import distribution
    groups = {ep.group for ep in distribution("euskaphone").entry_points}
    assert "opm.g2p" not in groups
