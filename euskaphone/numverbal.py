"""Thin adapter over the Basque number verbalizer.

The Roman-numeral and unit fallbacks spell a numeral through this one adapter
over :class:`euskaphone.number_utils.BasqueNumberParser`: :func:`spell_token` and
:func:`spell_ordinal`. :func:`spell_cardinal`, :func:`inessive` and
:func:`locative_genitive` served only the date stage that text2spoken replaces,
and are deprecated.

The deprecated date stage also used two morphophonological suffix rules — the
Basque **inessive** ("in/on") and **locative-genitive**
("of/-from") definite-singular endings, which choose an epenthetic ``e`` after a
consonant-final word (``hamabost`` → ``hamabostean`` "on the 15th";
``bat`` → ``bateko`` "of the 1st") but attach bare after a vowel
(``lau`` → ``lauko``; ``bi`` → ``bian``). This is the standard vowel/consonant
epenthesis of the Basque declension, not numeral-specific morphology.
"""
from __future__ import annotations

from typing import Optional

from euskaphone.deprecation import warn_deprecated
from euskaphone.number_utils import _SPEC_KEYS, DIALECTS, BasqueNumberParser

_VOWELS = "aeiouAEIOU"

#: What each deprecated reader of this module names in its place.
_REPLACEMENT = {
    "spell_cardinal": "use euskaphone.number_utils.BasqueNumberParser(dialect).cardinal",
    "inessive": "text2spoken declines the numerals it reads",
    "locative_genitive": "text2spoken declines the numerals it reads",
}


def _safe(dialect: str) -> str:
    """Fold an arbitrary dialect/lect string onto a code the composer knows."""
    dialect = _SPEC_KEYS.get(dialect, dialect)
    return dialect if dialect in DIALECTS else "eu"


def spell_token(token: str, dialect: str = "eu") -> Optional[str]:
    """Spell a numeric *token* (``"5"``, ``"7,3"``, ``"-4"``) as words, or None.

    Delegates to the composer's own token reader so decimals (``koma``) and the
    negative sign are handled the same way everywhere.
    """
    return BasqueNumberParser(_safe(dialect)).pronounce_token(token)


def spell_cardinal(n: int, dialect: str = "eu") -> str:
    """Deprecated: only the deprecated date stage spelled a bare cardinal here.

    Spell integer *n* as a Basque cardinal (``14`` → ``hamalau``).
    """
    warn_deprecated("numverbal.spell_cardinal", _REPLACEMENT["spell_cardinal"])
    return _spell_cardinal(n, dialect)


def _spell_cardinal(n: int, dialect: str = "eu") -> str:
    return BasqueNumberParser(_safe(dialect)).cardinal(n)


def spell_ordinal(n: int, dialect: str = "eu") -> str:
    """Spell integer *n* as a Basque ordinal (``14`` → ``hamalaugarren``)."""
    return BasqueNumberParser(_safe(dialect)).ordinal(n)


def inessive(word: str) -> str:
    """Deprecated: only the deprecated date stage declined a numeral here.

    Attach the definite-singular inessive ending (``-an`` / ``-ean``).
    Vowel-final stems take ``-an`` (``mendi`` → ``mendian``); consonant-final
    stems take the epenthetic ``-ean`` (``hamabost`` → ``hamabostean``).
    """
    warn_deprecated("numverbal.inessive", _REPLACEMENT["inessive"])
    return _inessive(word)


def _inessive(word: str) -> str:
    return f"{word}an" if word[-1:] in _VOWELS else f"{word}ean"


def locative_genitive(word: str) -> str:
    """Deprecated: only the deprecated date stage declined a numeral here.

    Attach the locative-genitive ending (``-ko`` / ``-eko``).
    Vowel-final stems take ``-ko`` (``lau`` → ``lauko``); consonant-final stems
    take the epenthetic ``-eko`` (``bat`` → ``bateko``).
    """
    warn_deprecated("numverbal.locative_genitive", _REPLACEMENT["locative_genitive"])
    return _locative_genitive(word)


def _locative_genitive(word: str) -> str:
    return f"{word}ko" if word[-1:] in _VOWELS else f"{word}eko"
