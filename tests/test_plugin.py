"""OVOS G2P plugin contract."""
from euskaphone.plugin import EuskaphoneG2PPlugin
from euskaphone.registry import list_dialects


def test_language_codes_are_the_eight_lects():
    assert set(EuskaphoneG2PPlugin().language_codes) == set(list_dialects())


def test_transcribe_returns_ipa():
    out = EuskaphoneG2PPlugin("eu").transcribe("kaixo mundua")
    assert isinstance(out, str) and out


def test_transcribe_word():
    out = EuskaphoneG2PPlugin("eu").transcribe_word("etxea")
    assert isinstance(out, str) and out


def test_dialect_selection_changes_engine_target():
    # a plugin bound to a dialect targets that lect
    plug = EuskaphoneG2PPlugin("souletin")
    assert plug.transcribe("kaixo")


def test_context_lang_overrides_default():
    from orthography2ipa import WordContext
    plug = EuskaphoneG2PPlugin("eu")
    ctx = WordContext(lang="eu-x-bizkaiera")
    assert plug.transcribe_word("etxea", ctx)


def test_contact_parameter_is_threaded():
    plug = EuskaphoneG2PPlugin("eu", contact="none")
    assert plug.transcribe("Plaza Mayor")
