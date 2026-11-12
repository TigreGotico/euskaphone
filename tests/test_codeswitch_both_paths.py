"""Routing invariants that must hold under either code-switch classifier.

The keep-list in :mod:`euskaphone.langdetect` is the single source of truth for
"this token is Basque, do not route it out". The statistical detector and the
orthographic backstop both consult it, so these tests run under both via the
``classifier`` fixture.
"""
import pytest

from euskaphone import EuskaPhonemizer
from euskaphone.codeswitch import (_CONTACT_STOPWORDS, is_contact_word,
                                   route_token)
from euskaphone.langdetect import BASQUE_KEEP, is_keep_word


@pytest.fixture(scope="module")
def ph():
    return EuskaPhonemizer()


NATIVE_SENTENCES = [
    "nik liburua irakurri du",
    "etxea eraiki du",
    "berak egin du lana",
    "egun on eta eskerrik asko",
    "haiek zoazte etxera",
    "zeundeten bezala genion hori",
    "gerraren kontra egin dugu",
]


@pytest.mark.parametrize("sentence", NATIVE_SENTENCES)
def test_native_sentence_unchanged_by_contact_routing(ph, classifier, sentence):
    auto = ph.phonemize_sentence(sentence, contact="auto")
    none = ph.phonemize_sentence(sentence, contact="none")
    assert auto == none


def test_keep_list_wins_every_contact_stopword_homograph(classifier):
    # The contact stopword lists stay complete for the languages they document,
    # so they overlap the keep-list ("du" is French, "on" is English). Every
    # such homograph must still resolve to Basque.
    overlap = {w for w in _CONTACT_STOPWORDS if is_keep_word(w)}
    assert overlap, "expected the lists to overlap"
    for word in sorted(overlap):
        assert not is_contact_word(word), word
        assert route_token(word, "auto") is None, word


@pytest.mark.parametrize("word", sorted(BASQUE_KEEP))
def test_no_keep_word_routes_to_a_contact_lattice(classifier, word):
    assert route_token(word, "auto") is None


def test_backstop_still_catches_a_basque_legal_loan(classifier):
    # The orthographic backstop exists to catch loans the detector scores as
    # Basque; the keep-list guard must not disarm it.
    assert is_contact_word("software")
    assert route_token("software", "auto") == "en"


def test_keep_list_covers_the_transitive_auxiliary(classifier):
    for word in ["du", "dut", "duzu", "dugu", "duzue", "dute"]:
        assert is_keep_word(word), word
        assert route_token(word, "auto") is None, word


@pytest.mark.parametrize("word", ["urteetan", "Erregeen", "lankideek"])
def test_default_contact_reads_basque_as_basque(word):
    # Code-switching is opt-in. With no contact argument, a Basque word is
    # read by the Basque lattice alone, as bare orthography2ipa reads it.
    from orthography2ipa import G2P
    from euskaphone.plugin import EuskaphoneG2PPlugin
    expected = G2P("eu").transcribe(word)
    assert EuskaPhonemizer(toponyms=False).phonemize_sentence(word) == expected
    assert EuskaphoneG2PPlugin("eu").transcribe(word) == expected


def test_lattice_core_default_contact_reads_basque_as_basque(classifier):
    # Every public entry point calls lattice_core.phonemize, so its own
    # default must be "none" too. "Andereñoak" has a ñ, which "auto" routes
    # to the Spanish lattice; read as Basque it matches o2i gold eu-010.
    from euskaphone.lattice_core import phonemize
    assert phonemize("Andereñoak", contact="auto") != "anˈdeɾeɲoak"
    assert phonemize("Andereñoak") == "anˈdeɾeɲoak"
