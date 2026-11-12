"""The orthography2ipa lattice as euskaphone's core phonemization pipeline.

euskaphone phonemizes by driving the shared orthography2ipa candidate lattice
(:class:`orthography2ipa.G2P`) for the eight Basque lect specs and layering on
top only the concerns orthography2ipa deliberately does not own. Dialect
selection *is* the choice of orthography2ipa lect spec: every ``eu-x-*`` variety
ships an engine spec whose grapheme table, ``allophones`` and sandhi encode that
variety's phonology (the apical/laminal sibilant contrast, the affricates, the
Souletin aspiration and ``/y/``, …), so the dialect phenomena are produced by
the lattice itself, not by post-hoc string edits.

What euskaphone adds sits in the stages orthography2ipa leaves to the caller,
wired through orthography2ipa's own extension points:

* **number normalization** — vigesimal (base-20) cardinal/ordinal verbalization
  (:mod:`euskaphone.number_utils`) runs as the pipeline's ``expand``, before
  the lattice sees the text;
* **code-switch handling** — embedded Spanish/French words are detected, routed
  through the ``es-ES``/``fr-FR`` lattice and nativized onto the Basque
  inventory (:mod:`euskaphone.codeswitch`), *outside* the engine, so a contact
  word never reaches the Basque lattice;
* **lexicon** — a curated pronunciation lexicon for proper names and loans is
  registered per lect through :func:`register_lexicon`, empty by default. The
  lect's engine holds it in its ``Pipeline(lexicon=...)``, so no other
  orthography2ipa engine in the process reads it.

**No homograph subsystem.** Basque orthography is near-phonemic: a grapheme's
reading is essentially fixed and sense-independent, so — unlike tugaphone's
Portuguese, which needs ``bifonia`` to disambiguate heterophonic homographs —
euskaphone deliberately ships no homograph/heterophone stage. This is a scope
decision, not an omission.
"""
from __future__ import annotations

import functools
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from orthography2ipa import G2P, Pipeline, load_lexicon

from euskaphone.codeswitch import route_token, transcribe_contact
from euskaphone.normalize import normalize_text
from euskaphone.registry import default_contact, resolve_lect

_VALID_CONTACT = ("auto", "es", "fr", "en", "none")

#: lect code -> the lexicon source registered for it (path, URL or ``hf://`` id)
#: and the entries read from it
_LEXICONS: Dict[str, Tuple[str, Dict[str, str]]] = {}


def _expander(lect: str):
    """The orthography2ipa ``expand`` callable euskaphone supplies for ``lect``.

    The full pre-lattice orthographic normalization runs here: abbreviations,
    numeric dates, unit/currency/percent symbols, Roman-numeral ordinals and
    monarch numerals, and finally vigesimal cardinal/ordinal verbalization
    (:func:`euskaphone.normalize.normalize_text`). It is a purely orthographic,
    pre-lattice transformation that leaves the text as Basque words.
    """

    def expand(text: str) -> str:
        return normalize_text(text, lect)

    return expand


@functools.lru_cache(maxsize=None)
def engine(lect: str, expand: bool = True) -> G2P:
    """A cached orthography2ipa engine for ``lect`` with euskaphone's expansion.

    The engine holds the lexicon registered for ``lect``. With none registered,
    the engine reads the process-wide lexicon of orthography2ipa's deprecated
    API, if the caller set one, and the rules otherwise. With ``expand=False``
    the engine reads text that :func:`normalize_text` has already normalized.
    """
    registered = _LEXICONS.get(lect)
    return G2P(lect, pipeline=Pipeline(
        lexicon=None if registered is None else registered[1],
        expand=_expander(lect) if expand else None))


def _validate_contact(contact: str) -> None:
    if contact not in _VALID_CONTACT:
        raise ValueError(
            f"unknown contact {contact!r}; expected one of {_VALID_CONTACT}")


def _route_normalized(text: str, lect: str, contact: str,
                      side: str) -> List[Tuple[Optional[str], str]]:
    """Normalize ``text``, then route each word the normalizer left as written.

    A word the normalizer wrote, such as ``hamalaugarrena`` for ``XIV`` or
    ``hamabost`` for ``15``, is Basque, so it never goes to the router.
    """
    raw, normalized = text.split(), normalize_text(text, lect).split()
    runs: List[Tuple[Optional[str], str]] = []
    # Constraint: a word the normalizer wrote is never routed. The detector
    # scores some of them as foreign (hamabost as en, segundo as es).
    matcher = SequenceMatcher(a=raw, b=normalized, autojunk=False)
    for op, _, _, start, end in matcher.get_opcodes():
        words = normalized[start:end]
        if op == "equal":
            runs += [(route_token(word, contact, side), word) for word in words]
        else:
            runs += [(None, word) for word in words]
    return runs


def phonemize(text: str, dialect: str = "eu", contact: str = "none") -> str:
    """Phonemize ``text`` for ``dialect`` through the orthography2ipa lattice.

    Basque tokens are transcribed by the eu lattice (numbers verbalized by the
    expansion, cross-word sandhi preserved within contiguous Basque runs);
    detected contact-language tokens are transcribed through the
    ``es``/``fr``/``en`` lattice and nativized onto the Basque inventory.
    ``contact`` is one of ``none`` (the default: disable switching), ``auto``
    (detect and classify each contact word among es/fr/en, unclassified words
    falling to the dialect's side), ``es``, ``fr`` or ``en``.

    The text is normalized before the router reads it (see
    :func:`_route_normalized`).
    """
    _validate_contact(contact)
    lect = resolve_lect(dialect)
    if contact == "none":
        return engine(lect).transcribe(text)
    keep_y = lect == "eu-x-zuberera"
    side = default_contact(lect)

    runs = _route_normalized(text, lect, contact, side)
    out: List[str] = []
    # transcribe contiguous Basque tokens as one phrase to preserve sandhi;
    # nativize each contact token individually.
    basque_buffer: List[str] = []

    def flush():
        if basque_buffer:
            phrase = " ".join(basque_buffer)
            out.append(engine(lect, expand=False).transcribe(phrase))
            basque_buffer.clear()

    for contact_lang, token in runs:
        if contact_lang is not None:
            flush()
            out.append(transcribe_contact(token, contact_lang, keep_y=keep_y))
        else:
            basque_buffer.append(token)
    flush()
    return " ".join(p for p in out if p)


def register_lexicon(dialect: str, source: str) -> None:
    """Register a pronunciation lexicon for ``dialect`` (proper names, loans).

    ``source`` follows the orthography2ipa lexicon contract — a path, URL or
    ``hf://`` id to a two-column ``word<TAB>ipa`` table. The lexicon is empty by
    default; a covered word folds into the same override path as a spec
    exception, so lattice generation runs only for uncovered words. euskaphone
    resolves the human-readable ``dialect`` alias to its lect code first. A
    later registration for the same lect replaces the earlier one.

    The lexicon is read here, so a local ``source`` that does not exist raises
    :class:`FileNotFoundError`.
    """
    _LEXICONS[resolve_lect(dialect)] = (source, load_lexicon(source))
    engine.cache_clear()


def lexicon_source(dialect: str) -> Optional[str]:
    """The lexicon source registered for ``dialect``, or ``None``."""
    registered = _LEXICONS.get(resolve_lect(dialect))
    return None if registered is None else registered[0]


def clear_caches() -> None:
    """Drop the per-lect engine cache (tests)."""
    engine.cache_clear()
