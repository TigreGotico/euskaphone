"""The composed orthographic normalizer euskaphone feeds the lattice.

The orthography2ipa lattice reads Basque *letters*; everything that is written
as a symbol, an abbreviation, a Roman numeral or a numeric date must be spelled
out into Basque words first. This module is the single pre-lattice pipeline that
does so, chaining the independent stages in a fixed order and finishing with the
vigesimal number verbalizer (:func:`euskaphone.number_utils.normalize_numbers`),
which mops up any remaining digit tokens.

Stage order (each stage consumes what it recognises and passes the rest on):

1. **abbreviations** (:mod:`euskaphone.abbreviations`) — expand ``etab.`` →
   ``eta abar`` first, so the periods that mark an abbreviation are gone before
   the Roman-numeral stage looks for the ordinal period.
2. **dates** (:mod:`euskaphone.dates`) — numeric ``Y/M/D`` triples become the
   ``…ko …aren …an`` form before the ``/`` gets split up.
3. **units** (:mod:`euskaphone.units`) — percent, currency and unit symbols
   become words (``% 5`` → ``ehuneko bost``).
4. **romans** (:mod:`euskaphone.romans`) — Roman ordinals and monarch numerals.
5. **numbers** — the existing vigesimal cardinal/ordinal verbalizer handles
   every remaining bare or case-suffixed digit token (``2024ko``, ``20:00etan``).

Stages 1–4 emit Basque words, so the number stage never re-touches their output.
The whole pipeline is wired into the orthography2ipa engine as its ``normalize``
callable (see :mod:`euskaphone.lattice_core`).
"""
from __future__ import annotations

from euskaphone.abbreviations import expand_abbreviations
from euskaphone.dates import normalize_dates
from euskaphone.number_utils import normalize_numbers
from euskaphone.romans import normalize_romans
from euskaphone.units import normalize_units


def normalize_text(text: str, dialect: str = "eu") -> str:
    """Run the full pre-lattice orthographic normalization for ``dialect``.

    Expands abbreviations, then reads numeric dates, unit/currency/percent
    expressions, Roman-numeral ordinals and monarch numerals, and finally
    verbalizes every remaining numeric token with the vigesimal number core.
    Returns Basque running text ready for the pronunciation lattice.
    """
    text = expand_abbreviations(text)
    text = normalize_dates(text, dialect)
    text = normalize_units(text, dialect)
    text = normalize_romans(text, dialect)
    text = normalize_numbers(text, dialect)
    return text
