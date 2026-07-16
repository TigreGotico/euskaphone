"""Thin adapter over the Basque number verbalizer.

The orthographic-normalization stages (Roman numerals, units/currency,
dates) all need to spell an integer as a Basque cardinal or ordinal, but the
cardinal composer itself lives in :mod:`euskaphone.number_utils` and is being
migrated to compose the shared ``ovos-number-parser`` API. To keep the new
stages rebase-friendly, every call into the number core goes through this one
adapter: if the composer's import path or signature changes, only this module
follows it, not the four feature modules.

The adapter also handles two morphophonological suffix rules the feature
modules share — the Basque **inessive** ("in/on") and **locative-genitive**
("of/-from") definite-singular endings, which choose an epenthetic ``e`` after a
consonant-final word (``hamabost`` → ``hamabostean`` "on the 15th";
``bat`` → ``bateko`` "of the 1st") but attach bare after a vowel
(``lau`` → ``lauko``; ``bi`` → ``bian``). This is the standard vowel/consonant
epenthesis of the Basque declension, not numeral-specific morphology.
"""
from __future__ import annotations

from typing import Optional

from euskaphone.number_utils import DIALECTS, BasqueNumberParser

_VOWELS = "aeiouAEIOU"


def _safe(dialect: str) -> str:
    """Fold an arbitrary dialect/lect string onto a code the composer knows."""
    return dialect if dialect in DIALECTS else "eu"


def spell_token(token: str, dialect: str = "eu") -> Optional[str]:
    """Spell a numeric *token* (``"5"``, ``"7,3"``, ``"-4"``) as words, or None.

    Delegates to the composer's own token reader so decimals (``koma``) and the
    negative sign are handled the same way everywhere.
    """
    return BasqueNumberParser(_safe(dialect)).pronounce_token(token)


def spell_cardinal(n: int, dialect: str = "eu") -> str:
    """Spell integer *n* as a Basque cardinal (``14`` → ``hamalau``)."""
    return BasqueNumberParser(_safe(dialect)).cardinal(n)


def spell_ordinal(n: int, dialect: str = "eu") -> str:
    """Spell integer *n* as a Basque ordinal (``14`` → ``hamalaugarren``)."""
    return BasqueNumberParser(_safe(dialect)).ordinal(n)


def inessive(word: str) -> str:
    """Attach the definite-singular inessive ending (``-an`` / ``-ean``).

    Vowel-final stems take ``-an`` (``mendi`` → ``mendian``); consonant-final
    stems take the epenthetic ``-ean`` (``hamabost`` → ``hamabostean``).
    """
    return f"{word}an" if word[-1:] in _VOWELS else f"{word}ean"


def locative_genitive(word: str) -> str:
    """Attach the locative-genitive ending (``-ko`` / ``-eko``).

    Vowel-final stems take ``-ko`` (``lau`` → ``lauko``); consonant-final stems
    take the epenthetic ``-eko`` (``bat`` → ``bateko``).
    """
    return f"{word}ko" if word[-1:] in _VOWELS else f"{word}eko"
