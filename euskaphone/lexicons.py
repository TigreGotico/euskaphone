"""Shipped Basque lexicons and the hooks that (de)register them.

euskaphone bundles two small, source-cited lexicons and wires them through the
orthography2ipa lexicon contract (:func:`orthography2ipa.register_lexicon`, one
sidecar source per language code). Both are word-keyed ``word<TAB>ipa`` tables
under :data:`LEXICON_DIR`, validated at build time by
``scripts/build_lexicons.py``.

Toponym lexicon (``eu_toponyms.tsv``) — OPT-OUT
-----------------------------------------------
A curated seed of the most important Basque toponyms and respelled exonyms in
their **Euskaltzaindia normative** forms (source: the Academy's onomastics
database EODA, https://www.euskaltzaindia.eus/eoda, plus the Academy's exonym
recommendations). For a regular normative spelling the IPA pins the Batua
lattice reading of that spelling; foreign-spelled entries carry explicit
adapted IPA. EODA is a query-only public service with no bulk-download endpoint
and no open-data licence, so only the normative spellings — the Academy's
official, non-copyrightable facts about place names — are transcribed, never any
EODA content itself.

This lexicon is registered for the standard ``eu`` code by default
(:class:`euskaphone.EuskaPhonemizer` constructs with ``toponyms=True``); pass
``toponyms=False`` to opt out. A caller's own :func:`euskaphone.register_lexicon`
for ``eu`` always wins — the built-in is only registered when no lexicon is
already registered for the code.

HiTZ overlay (``eu_hitz_overlay.tsv``) — OPT-IN, benchmark-coupled
------------------------------------------------------------------
Proper nouns drawn from the HiTZ/EHU ``wikipedia_basque_ipa`` set. That set is
also euskaphone's independent cross-engine benchmark, so folding any of it into
a lexicon is **circular**: the model would be graded against data it memorised.
The overlay is therefore opt-in (``lexicon="hitz"``) and the benchmark harness,
when the overlay is active, excludes every benchmark row containing an overlay
key (:func:`hitz_overlay_words`). Enabling the overlay trades a small
proper-noun accuracy gain for the loss of those rows as an honest,
independent signal — documented in ``docs/benchmarks.md``.
"""
from __future__ import annotations

import functools
import os
from typing import FrozenSet, Optional

LEXICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "lexicons")

TOPONYM_LEXICON = os.path.join(LEXICON_DIR, "eu_toponyms.tsv")
HITZ_OVERLAY_LEXICON = os.path.join(LEXICON_DIR, "eu_hitz_overlay.tsv")

#: The lect code the built-in lexicons pin (normative Batua).
BUILTIN_CODE = "eu"


def _already_registered(code: str) -> bool:
    """Whether *code* already has a caller-registered lexicon (do not clobber)."""
    from orthography2ipa import lexicon as _lex
    return code in getattr(_lex, "_REGISTERED", {})


def register_toponyms(dialect: str = "eu", *, force: bool = False) -> bool:
    """Register the built-in toponym lexicon for ``dialect``.

    Returns ``True`` if it was registered, ``False`` if skipped because a
    lexicon is already registered for the resolved code (``force=True``
    overrides). A caller's own lexicon therefore always takes precedence.
    """
    from euskaphone.lattice_core import register_lexicon
    from euskaphone.registry import resolve_lect
    code = resolve_lect(dialect)
    if not force and _already_registered(code):
        return False
    register_lexicon(dialect, TOPONYM_LEXICON)
    return True


def register_hitz_overlay(dialect: str = "eu") -> None:
    """Register the opt-in HiTZ proper-noun overlay for ``dialect``.

    This overrides any lexicon currently registered for the code (the overlay is
    an explicit opt-in). See the module docstring for the circularity caveat.
    """
    from euskaphone.lattice_core import register_lexicon
    register_lexicon(dialect, HITZ_OVERLAY_LEXICON)


@functools.lru_cache(maxsize=None)
def hitz_overlay_words() -> FrozenSet[str]:
    """The lower-cased keys of the HiTZ overlay (the benchmark-exclusion set).

    A benchmark harness that has the overlay active must drop every reference
    row whose text contains one of these words, so the overlay is never graded
    against the data it was drawn from.
    """
    from orthography2ipa.lexicon import parse_lexicon_text
    if not os.path.isfile(HITZ_OVERLAY_LEXICON):
        return frozenset()
    with open(HITZ_OVERLAY_LEXICON, encoding="utf-8") as fh:
        return frozenset(parse_lexicon_text(fh.read()))


def apply_builtins(toponyms: bool = True, lexicon: Optional[str] = None,
                   dialect: str = "eu") -> None:
    """Register the built-in lexicons selected by the constructor flags.

    ``toponyms`` (opt-out, default on) registers the toponym seed unless a
    caller lexicon already owns the code. ``lexicon="hitz"`` (opt-in) registers
    the HiTZ overlay, which then takes precedence for the code.
    """
    if toponyms:
        register_toponyms(dialect)
    if lexicon == "hitz":
        register_hitz_overlay(dialect)
    elif lexicon not in (None, "toponyms"):
        raise ValueError(
            f"unknown lexicon {lexicon!r}; expected None, 'toponyms' or 'hitz'")
