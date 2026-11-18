"""The orthographic normalizer euskaphone feeds the lattice.

The orthography2ipa lattice reads Basque *letters*. A number, a date, a clock
time, an abbreviation, a Roman numeral, a unit or a currency symbol must become
Basque words first. :func:`normalize_text` does this in two steps:

1. **text2spoken** reads the text (:func:`text2spoken_reading`). Where it reads a
   form, its reading stands.
2. **fallbacks** read the forms that text2spoken leaves as written. Each fallback
   reads one class of form, and its comment names the text2spoken issue for that
   class. A fallback goes when text2spoken reads its form.

The fallbacks run in this order:

* space-grouped thousands, ``1 000 000`` (:mod:`euskaphone.number_utils`);
* digits with the ordinal suffix, ``16garren``;
* a point as the decimal mark, ``2.5``;
* a currency symbol before the number, ``€5eko`` (:mod:`euskaphone.units`);
* the unit symbols text2spoken does not read, ``5 g``;
* a bare Roman numeral after a name, ``Karlos V`` (:mod:`euskaphone.romans`);
* the abbreviations text2spoken does not read, ``h.d.``
  (:mod:`euskaphone.abbreviations`).

text2spoken leaves spelled-out Basque as written, so text that a caller has
already normalized comes through unchanged. The whole pipeline is the
orthography2ipa engine's ``expand`` callable (see :mod:`euskaphone.lattice_core`).
"""
from __future__ import annotations

import functools

import text2spoken
from text2spoken import InvalidLanguageTagError

from euskaphone.abbreviations import read_left_abbreviations
from euskaphone.number_utils import (read_dot_decimals, read_garren_ordinals,
                                     read_space_grouped_numbers)
from euskaphone.registry import DEFAULT_DIALECT, resolve_lect
from euskaphone.romans import read_bare_monarch_numerals
from euskaphone.units import read_currency_before_number, read_unit_symbols


@functools.lru_cache(maxsize=None)
def text2spoken_tag(dialect: str = DEFAULT_DIALECT) -> str:
    """The language tag text2spoken reads ``dialect`` in.

    This is the lect that :func:`euskaphone.registry.resolve_lect` gives, so
    every name of a lect reaches text2spoken as one tag: ``lapurtera`` and
    ``eu-x-lapurtera`` both give ``eu-x-lapurdi``. A lect that text2spoken
    refuses as a language tag reads as ``eu``.
    """
    lect = resolve_lect(dialect)
    try:
        text2spoken.supports(lect)
    except InvalidLanguageTagError:
        return DEFAULT_DIALECT
    return lect


def text2spoken_reading(text: str, dialect: str = DEFAULT_DIALECT) -> str:
    """``text`` as text2spoken reads it in ``dialect``, with no fallback."""
    return text2spoken.normalize(text, text2spoken_tag(dialect))


def normalize_text(text: str, dialect: str = DEFAULT_DIALECT) -> str:
    """Rewrite ``text`` as the Basque words a speaker of ``dialect`` says.

    text2spoken reads numbers, dates, clock times, money, measures,
    abbreviations and Roman numerals. The fallbacks then read the forms that
    text2spoken leaves as written. The rest of the text stays as written.

    >>> normalize_text("XX. mendean 100 urte")
    'hogeigarren mendean ehun urte'
    """
    lect = resolve_lect(dialect)
    spoken = text2spoken_reading(text, lect)
    spoken = read_space_grouped_numbers(spoken, lect)
    spoken = read_garren_ordinals(spoken, lect)
    spoken = read_dot_decimals(spoken, lect)
    spoken = read_currency_before_number(spoken, lect)
    spoken = read_unit_symbols(spoken, text, lect)
    spoken = read_bare_monarch_numerals(spoken, lect)
    return read_left_abbreviations(spoken)
