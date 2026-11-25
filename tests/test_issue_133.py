"""⟨ñ⟩ is a Basque letter, so a native word with it stays on the Basque route."""

import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.codeswitch import is_contact_word


@pytest.mark.parametrize("text", ["andereño ona da.", "Andereñoak liburua eman dit.", "iruñea"])
def test_enye_word_reads_as_basque_under_auto(classifier, text):
    ph = EuskaPhonemizer(toponyms=False)
    assert ph.phonemize_sentence(text, contact="auto") == ph.phonemize_sentence(text, contact="none")


@pytest.mark.parametrize("word", ["andereño", "Andereñoak", "iruñea"])
def test_enye_is_not_a_foreign_letter(word):
    assert not is_contact_word(word)
