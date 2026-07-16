"""Code-switch handling: embedded Spanish / French routed and nativized.

Real Basque text is bilingual. On the peninsular side (Hegoalde) it embeds
Spanish; on the continental side (Iparralde) it embeds French — proper names,
loans, quoted fragments. A TTS frontend that hands such a word to the Basque
lattice mispronounces it, and one that hands it to the raw Spanish/French
lattice emits phones outside the Basque inventory the voice was trained on.

euskaphone takes arbtok's **total-nativization** stance — *never drop a segment,
always project it onto the target inventory* — but keeps the machinery far
simpler than arbtok: a word-level detection heuristic decides whether a token is
Basque or contact-language, a detected contact word is transcribed through the
orthography2ipa ``es-ES`` / ``fr-FR`` lattice, and every phone in that result is
projected onto the Basque phoneme inventory by :data:`_NATIVIZE`. There is no
sub-word alignment and no statistical language ID — just the orthographic
heuristic and the phone projection.

The contact language is chosen by the ``contact`` parameter:

* ``"auto"`` (default) — detect contact words orthographically and route them
  through the dialect's default side (peninsular → Spanish, continental →
  French; see :func:`euskaphone.registry.default_contact`);
* ``"es"`` / ``"fr"`` — force that contact lattice for detected contact words;
* ``"none"`` — disable code-switching; every token is transcribed as Basque.

Detection heuristic
-------------------
Basque orthography does not natively use ``c q v w y ñ ç`` or the Romance
accented vowels ``á í ó ú â è ê î ï ô ù``. A token carrying any of those (and a
handful of very common Spanish/French function words) is treated as a contact
word. This is a deliberately shallow, well-documented heuristic — it catches the
proper names and loans that actually break a Basque TTS voice, and it never
*drops* a word: an undetected contact word simply falls through to the Basque
lattice, which the nativization step would have projected onto the same
inventory anyway.
"""
from __future__ import annotations

import functools
from typing import Callable, List

# ---------------------------------------------------------------------------
# Detection.
# ---------------------------------------------------------------------------

#: Letters not used natively in Basque orthography (loans/proper names only).
_NON_BASQUE_LETTERS = set("cqvwyñçáíóúàâèêîïôùäëö")

#: A small set of very common Spanish/French function words that carry no
#: non-Basque letter but are unambiguous contact-language material.
_CONTACT_STOPWORDS = {
    # Spanish
    "el", "la", "los", "las", "del", "por", "para", "con", "una", "que",
    "más", "muy", "pero", "como", "este", "esta",
    # French
    "le", "les", "des", "du", "et", "un", "une", "dans", "pour", "avec",
    "sur", "pas", "plus", "très", "mais", "cette",
}


def _strip(token: str) -> str:
    """Lower-case a token and strip surrounding punctuation for testing."""
    return token.strip("".join(
        c for c in token if not (c.isalpha() or c == "-"))).lower()


def is_contact_word(token: str) -> bool:
    """Heuristically decide whether *token* is embedded contact-language text."""
    core = _strip(token)
    if not core:
        return False
    if any(ch in _NON_BASQUE_LETTERS for ch in core):
        return True
    return core in _CONTACT_STOPWORDS


# ---------------------------------------------------------------------------
# Nativization: project a contact-language IPA string onto Basque phones.
# ---------------------------------------------------------------------------

#: Combining diacritics dropped before projection (nasal tilde, stress, liaison).
_DROP = ("̃", "ˈ", "ˌ", "‿")  # ̃  ˈ  ˌ  ‿

#: Foreign phone → nearest Basque phone. Multi-character keys are applied
#: longest-first so digraph affricates/glides project as a unit. Every mapping
#: keeps the segment (total nativization); nothing is deleted.
_NATIVIZE = {
    # Romance obstruents absent from Basque
    "θ": "s̻",   # Castilian interdental → laminal sibilant
    "v": "b",    # French /v/ → /b/ (Basque has no /v/)
    "z": "s̻",   # voiced sibilant → laminal (Basque has no voiced sibilant)
    "ʒ": "ʃ",    # French /ʒ/ → postalveolar fricative
    "ʝ": "j",    # Spanish yeísmo fricative → glide
    "ɟʝ": "j",   # Spanish affricated /ʝ/ → glide
    # French uvulars/velars
    "ʁ": "r", "ʀ": "r", "χ": "x",
    # vowels beyond the 5-vowel Basque system
    "ɔ": "o", "ɛ": "e", "ɑ": "a", "ə": "e",
    "ø": "e", "œ": "e", "y": "i",   # (Souletin keeps /y/; overridden per lect)
    "ɥ": "j",
    # denasalized French nasal vowels (tilde already dropped; catch bare marks)
    "æ̃": "e", "ɑ̃": "a", "ɔ̃": "o", "ɛ̃": "e", "œ̃": "e", "õ": "o",
}


def _nativize(ipa: str, keep_y: bool = False) -> str:
    """Project a contact-language IPA string onto the Basque inventory."""
    for d in _DROP:
        ipa = ipa.replace(d, "")
    for src in sorted(_NATIVIZE, key=len, reverse=True):
        if keep_y and src == "y":
            continue
        ipa = ipa.replace(src, _NATIVIZE[src])
    return ipa


# ---------------------------------------------------------------------------
# The contact transcriber.
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _contact_engine(contact: str):
    """A cached orthography2ipa engine for the ``es``/``fr`` contact lattice."""
    from orthography2ipa import G2P
    code = {"es": "es-ES", "fr": "fr-FR"}[contact]
    return G2P(code)


def transcribe_contact(word: str, contact: str, keep_y: bool = False) -> str:
    """Transcribe a contact *word* and nativize it onto the Basque inventory."""
    ipa = _contact_engine(contact).transcribe(word)
    return _nativize(ipa, keep_y=keep_y)


def split_runs(text: str, contact: str) -> List[tuple]:
    """Split *text* into ``(is_contact, token)`` pairs by the word heuristic.

    ``contact == "none"`` marks every token as Basque.
    """
    runs = []
    for token in text.split():
        native = contact != "none" and is_contact_word(token)
        runs.append((native, token))
    return runs
