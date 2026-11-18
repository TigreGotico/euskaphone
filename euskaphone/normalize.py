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

* a clock time with no case ending, ``10:30``;
* space-grouped thousands, ``1 000 000`` (:mod:`euskaphone.number_utils`);
* digits with the ordinal suffix, ``16garren``;
* a point as the decimal mark, ``2.5``;
* a currency symbol before the number, ``€5eko`` (:mod:`euskaphone.units`);
* the unit symbols text2spoken does not read, ``5 g``;
* a bare Roman numeral after a name, ``Karlos V`` (:mod:`euskaphone.romans`);
* the abbreviations text2spoken does not read, ``h.d.``
  (:mod:`euskaphone.abbreviations`);
* an abbreviation of the table with a capital, ``Jn.``;
* digits with a case ending that text2spoken does not read, ``100dik``.

Last, euskaphone reads the digits that are still in the text, as in a code
(``B12``, ``AP-8``). text2spoken leaves a code as a name, and the lattice
deletes the digits it cannot read.

text2spoken leaves spelled-out Basque as written, so text that a caller has
already normalized comes through unchanged. The whole pipeline is the
orthography2ipa engine's ``expand`` callable (see :mod:`euskaphone.lattice_core`).
"""
from __future__ import annotations

import functools
import importlib
import re

import text2spoken
from text2spoken import InvalidLanguageTagError

from euskaphone.abbreviations import (_TRAILING, ABBREVIATIONS,
                                      read_left_abbreviations)
from euskaphone.deprecation import warn_deprecated
from euskaphone.number_utils import (read_code_digits, read_dot_decimals,
                                     read_garren_ordinals,
                                     read_glued_case_endings,
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


#: A clock time with no case ending: ``10:30``. A time with seconds
#: (``07:05:15``) or a case ending (``10:30ean``) does not match.
_BARE_CLOCK = re.compile(r"(?<![\w:.,])(\d{1,2}):([0-5]\d)(?![\w:]|[.,]\d)")


def read_bare_clock_times(text: str, dialect: str = DEFAULT_DIALECT) -> str:
    """Read a clock time with no case ending: ``10:30`` → ``goizeko hamarrak eta
    hogeita hamar``.

    Araua 203 p.49 reads ``12:15`` as «hamabiak eta hamabost»: the hour takes the
    plural article and ``eta`` joins the minutes. Note 34 on the same page puts
    the part of the day first («Arratsaldeko zazpiak eta hamar (7:10 p.m.)»), as
    text2spoken does for a time with a case ending. text2spoken reads the hour
    with the article (``10:00ak``), so the hour reads through text2spoken, and
    the minutes follow it.
    https://github.com/TigreGotico/text2spoken/issues/267
    """
    def read(m: "re.Match[str]") -> str:
        hour, minute = int(m.group(1)), int(m.group(2))
        if hour > 24 or (hour == 24 and minute):
            return m.group()
        spoken = text2spoken_reading(f"{hour}:00ak", dialect)
        if minute:
            spoken = f"{spoken} eta {text2spoken_reading(str(minute), dialect)}"
        return spoken
    return _BARE_CLOCK.sub(read, text)


#: Marks that can open a word before an abbreviation: ``(Jn.``.
_OPENING = "(«\"'[¿¡"


def read_capitalized_abbreviations(text: str, dialect: str = DEFAULT_DIALECT) -> str:
    """Read an abbreviation of the table with a capital: ``Jn. Agirre`` →
    ``Jauna Agirre``.

    Araua 196 section 13 (pp. 32-33) lets a sentence open with an
    abbreviation, which then takes a capital. text2spoken reads the lower-case
    form (``jn.``) and leaves the capitalized one as written. The capitalized
    form reads as text2spoken reads the lower-case form before the same next
    word, and keeps the capital. An abbreviation that text2spoken leaves in
    lower case too (``e.a.``, ``at.``) stays as written.
    https://github.com/TigreGotico/text2spoken/issues/265
    """
    parts = re.split(r"(\s+)", text)
    words = parts[::2]
    for i, word in enumerate(words):
        body = word.lstrip(_OPENING)
        opening = word[:len(word) - len(body)]
        core = body.rstrip(_TRAILING)
        lower = core.lower()
        if lower not in ABBREVIATIONS or not core[:1].isupper() or core[1:] != core[1:].lower():
            continue
        lowered = lower + body[len(core):]
        following = next((w for w in words[i + 1:] if w), "")
        spoken = text2spoken_reading(f"{lowered} {following}" if following else lowered, dialect)
        if following:
            if not spoken.endswith(f" {following}"):
                continue
            spoken = spoken[:-len(following) - 1]
        if spoken != lowered:
            words[i] = opening + spoken[0].upper() + spoken[1:]
    parts[::2] = words
    return "".join(parts)


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
    spoken = read_bare_clock_times(spoken, lect)
    spoken = read_space_grouped_numbers(spoken, lect)
    spoken = read_garren_ordinals(spoken, lect)
    spoken = read_dot_decimals(spoken, lect)
    spoken = read_currency_before_number(spoken, lect)
    spoken = read_unit_symbols(spoken, text, lect)
    spoken = read_bare_monarch_numerals(spoken, lect)
    spoken = read_left_abbreviations(spoken)
    spoken = read_capitalized_abbreviations(spoken, lect)
    spoken = read_glued_case_endings(spoken, lect)
    return read_code_digits(spoken, lect)


#: The readers this module exported before text2spoken read the text, by the
#: module that defines each one.
_REEXPORTED = {
    "expand_abbreviations": "abbreviations",
    "normalize_dates": "dates",
    "normalize_numbers": "number_utils",
    "normalize_romans": "romans",
    "normalize_units": "units",
}


def __getattr__(name: str):
    home = _REEXPORTED.get(name)
    if home is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    warn_deprecated(f"normalize.{name}", "use euskaphone.normalize.normalize_text")
    return getattr(importlib.import_module(f"euskaphone.{home}"), name)
