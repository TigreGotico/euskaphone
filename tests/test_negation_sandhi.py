"""Categorical negative-particle (ez) contraction through the euskaphone lattice.

The connected-speech sandhi of *ez* /es̻/ before a following auxiliary/verb onset
is carried by the shared orthography2ipa `eu` lect spec and reaches euskaphone
because contiguous Basque tokens are transcribed as one phrase. These are
round-trip checks: the written form goes in, the contracted [es̻tut]-class IPA
comes out. Grounding: Hualde & Ortiz de Urbina (2003) §Segmental phonology;
Hualde (1991), Basque Phonology.
"""
import pytest

from euskaphone import EuskaPhonemizer


@pytest.fixture(scope="module")
def ph():
    return EuskaPhonemizer()


# (written negation, expected Batua IPA, rule label)
_EZ_CASES = [
    ("ez dut", "es̻ tut", "ez+d -> ezt"),        # onset devoicing, sibilant kept
    ("ez da", "es̻ ta", "ez+d -> ezt"),
    ("ez dakit", "es̻ takit", "ez+d -> ezt"),
    ("ez zen", "e ts̻en", "ez+z -> etz"),         # sibilant->affricate coalescence
    ("ez zara", "e ts̻aɾa", "ez+z -> etz"),
    ("ez naiz", "e nai̯s̻", "ez+n -> en"),         # deletion before nasal
    ("ez nator", "e nator", "ez+n -> en"),
    ("ez luke", "e luke", "ez+l -> el"),          # deletion before lateral
    ("ez litzateke", "e lits̻ateke", "ez+l -> el"),
    ("ez balitz", "es̻ palits̻", "ez+b -> ezp"),  # onset devoicing, sibilant kept
    ("ez bada", "es̻ pada", "ez+b -> ezp"),
    ("ez gara", "es̻ kaɾa", "ez+g -> ezk"),       # onset devoicing, sibilant kept
    ("ez gaitu", "es̻ kai̯tu", "ez+g -> ezk"),
]


@pytest.mark.parametrize("text,expected,label", _EZ_CASES,
                         ids=[c[2] + ":" + c[0] for c in _EZ_CASES])
def test_ez_contraction_roundtrip(ph, text, expected, label):
    assert ph.phonemize_sentence(text) == expected


def test_ez_contraction_inside_a_full_sentence(ph):
    # the contraction fires mid-phrase, not only in a bare two-word input
    assert ph.phonemize_sentence("Gaur ez dut ezer jan.") == \
        "ɡau̯r es̻ tut es̻er jan"
    assert ph.phonemize_sentence("Ni ez naiz berandu iritsi.") == \
        "ni e nai̯s̻ beɾandu iɾits̺i"


def test_only_the_negator_contracts(ph):
    # 'naiz' ends in the same laminal sibilant but is not the negator, so a
    # following voiced onset is NOT devoiced: no spurious contraction.
    assert ph.phonemize_sentence("naiz da") == "nai̯s̻ da"


def test_contraction_inherited_by_eastern_dialects(ph):
    # eastern varieties keep the laminal /s̻/, so the standard rule fires
    for dialect in ("eu-x-gipuzkera", "eu-x-lapurtera", "souletin"):
        assert ph.phonemize_sentence("ez dut", dialect) == "es̻ tut"
        assert ph.phonemize_sentence("ez zen", dialect) == "e ts̻en"


def test_biscayan_apical_merge_does_not_force_a_wrong_contraction(ph):
    # Western/Biscayan merges laminal <z> to apical [s̺]: 'ez' surfaces as
    # 'es̺', so the laminal-keyed standard rule does not fire (null beats a
    # wrong contraction) — documented dialect variation, not a bug.
    out = ph.phonemize_sentence("ez dut", "biscayan")
    assert out.startswith("es̺")
    assert out != "es̻ tut"
