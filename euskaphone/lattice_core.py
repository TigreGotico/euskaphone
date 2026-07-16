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
  (:mod:`euskaphone.number_utils`) runs as the engine's ``normalizer``, i.e.
  before the lattice sees the text (orthography2ipa's ``normalize`` stage);
* **code-switch handling** — embedded Spanish/French words are detected, routed
  through the ``es-ES``/``fr-FR`` lattice and nativized onto the Basque
  inventory (:mod:`euskaphone.codeswitch`), *outside* the engine, so a contact
  word never reaches the Basque lattice;
* **lexicon** — a curated pronunciation lexicon for proper names and loans is
  registered per lect through :func:`orthography2ipa.register_lexicon`
  (:func:`register_lexicon` here), empty by default.

**No homograph subsystem.** Basque orthography is near-phonemic: a grapheme's
reading is essentially fixed and sense-independent, so — unlike tugaphone's
Portuguese, which needs ``bifonia`` to disambiguate heterophonic homographs —
euskaphone deliberately ships no homograph/heterophone stage. This is a scope
decision, not an omission.
"""
from __future__ import annotations

import functools
from typing import List, Optional

from orthography2ipa import G2P, register_lexicon as _o2i_register_lexicon

from euskaphone.codeswitch import split_runs, transcribe_contact
from euskaphone.number_utils import normalize_numbers
from euskaphone.registry import default_contact, resolve_lect

_VALID_CONTACT = ("auto", "es", "fr", "none")


def _normalizer(lect: str):
    """The orthography2ipa ``normalize`` callable euskaphone supplies for ``lect``.

    Vigesimal numbers/ordinals are verbalized before the lattice runs; this is a
    purely orthographic, pre-lattice transformation.
    """

    def normalize(text: str) -> str:
        return normalize_numbers(text, lect)

    return normalize


@functools.lru_cache(maxsize=None)
def engine(lect: str) -> G2P:
    """A cached orthography2ipa engine for ``lect`` with euskaphone's normalizer."""
    return G2P(lect, normalizer=_normalizer(lect))


def _resolve_contact(contact: str, lect: str) -> str:
    if contact not in _VALID_CONTACT:
        raise ValueError(
            f"unknown contact {contact!r}; expected one of {_VALID_CONTACT}")
    if contact == "auto":
        return default_contact(lect)
    return contact


def phonemize(text: str, dialect: str = "eu", contact: str = "auto") -> str:
    """Phonemize ``text`` for ``dialect`` through the orthography2ipa lattice.

    Basque tokens are transcribed by the eu lattice (numbers verbalized by the
    normalizer, cross-word sandhi preserved within contiguous Basque runs);
    detected contact-language tokens are transcribed through the ``es``/``fr``
    lattice and nativized onto the Basque inventory. ``contact`` is one of
    ``auto`` (per-dialect side), ``es``, ``fr`` or ``none`` (disable switching).
    """
    lect = resolve_lect(dialect)
    if contact == "none":
        return engine(lect).transcribe(text)
    contact_lang = _resolve_contact(contact, lect)
    keep_y = lect == "eu-x-zuberera"

    runs = split_runs(text, contact_lang)
    out: List[str] = []
    # transcribe contiguous Basque tokens as one phrase to preserve sandhi;
    # nativize each contact token individually.
    basque_buffer: List[str] = []

    def flush():
        if basque_buffer:
            phrase = " ".join(basque_buffer)
            out.append(engine(lect).transcribe(phrase))
            basque_buffer.clear()

    for is_contact, token in runs:
        if is_contact:
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
    resolves the human-readable ``dialect`` alias to its lect code first.
    """
    _o2i_register_lexicon(resolve_lect(dialect), source)


def clear_caches() -> None:
    """Drop the per-lect engine cache (tests)."""
    engine.cache_clear()
