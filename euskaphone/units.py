"""Units, currency and percent reading — the pre-lattice normalizer stage.

Symbols are never read letter by letter: ``kg`` is read ``kilogramo`` and ``€``
is read ``euro`` (Euskaltzaindia Araua 197, *Sinboloak*). Three constructions are
handled, each with the Basque-specific word order and declension:

* **Percent** — the ``%`` symbol is the word ``ehuneko``, and it is read
  **before** the number in either writing order: both ``% 5`` and ``5%`` are read
  ``ehuneko bost`` (EIMA *Ortotipografia*, "Ehunekoak").
* **Currency** — ``5 €`` / ``€5`` → ``bost euro`` (``euro`` is invariant in the
  plural); the money word *follows* the number, and a possessive/relational
  ending attaches to the spelled word (``€5eko`` → ``bost euroko``). ``1 €`` reads
  ``euro bat`` because the numeral "one" (``bat``) is postposed in Basque.
* **Units** — ``5 km`` → ``bost kilometro``; the unit word follows the number and
  carries any declension the writer hyphenated onto the symbol
  (``3 km-ra`` → ``hiru kilometrora``, ``50 kg-ko`` → ``berrogeita hamar
  kilogramoko``), the standard Araua 197 symbol-plus-hyphen-suffix convention.

The symbol→word table lives in ``data/units.tsv`` (data, not code). This stage
composes the number verbalizer through :mod:`euskaphone.numverbal` and produces
Basque *words*, so the downstream number stage leaves its output alone.

Sources
-------
* **Euskaltzaindia**, **Araua 197**, EBO (II) *"Sinboloak"* — symbols are read as
  their full word (``kg`` → ``kilogramo``), ``%`` is the ``ehuneko`` symbol, ``€``
  is read ``euro``, and a case ending attaches to the symbol with a hyphen.
* **EIMA / Basque Government**, J. R. Zubimendi, *Ortotipografia* (2004),
  "Ehunekoak" / "Neurri-izenak": ``%`` = ``ehuneko`` written before the number,
  and the natural number-then-unit reading order.
  (``papers/iberian/eima_ortotipografia_zubimendi.pdf``)
"""
from __future__ import annotations

import os
import re
from typing import Dict

from euskaphone.numverbal import spell_token

_DATA = os.path.join(os.path.dirname(__file__), "data", "units.tsv")

_PERCENT_WORD = "ehuneko"


def _load(path: str = _DATA) -> Dict[str, str]:
    table: Dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] and parts[1]:
                table[parts[0]] = parts[1]
    return table


#: symbol → spoken word (singular stem the declension attaches to).
UNITS: Dict[str, str] = _load()

#: Currency symbols may also be written *before* the number (``€5``).
_PREFIX_CURRENCY = ("€", "$", "£")

_NUM = r"\d+(?:,\d+)?"


def _spell(num: str, dialect: str) -> str:
    """Spell a numeric literal (``"5"``, ``"7,3"``); fall back to the literal."""
    return spell_token(num, dialect) or num


_VOWELS = "aeiou"


def _attach(word_phrase: str, suffix: str) -> str:
    """Attach a declension *suffix* to the last word of a spelled phrase.

    The suffix as written on the symbol may carry the epenthetic ``e`` a
    consonant-final digit form needs (``5eko``); when it is re-anchored to a
    vowel-final unit word the ``e`` drops, since Basque inserts the epenthetic
    ``e`` only after a consonant (``euro`` + ``eko`` → ``euroko``, not
    ``*euroeko``; ``kilometro`` + ``ra`` → ``kilometrora``).
    """
    if not suffix:
        return word_phrase
    words = word_phrase.split()
    last = words[-1]
    if last[-1:] in _VOWELS and suffix.startswith("e"):
        suffix = suffix[1:]
    words[-1] = f"{last}{suffix}"
    return " ".join(words)


def _percent_regex() -> "re.Pattern[str]":
    return re.compile(
        rf"(?:%\s?({_NUM})|({_NUM})\s?%)([a-z]*)"
    )


def _postfix_symbol_regex() -> "re.Pattern[str]":
    # longest symbols first so "min"/"km" win over "m"/"k"
    syms = sorted(UNITS, key=len, reverse=True)
    alt = "|".join(re.escape(s) for s in syms)
    return re.compile(rf"({_NUM})\s?({alt})(?:-([a-z]+))?(?![a-zA-Z])")


def _prefix_currency_regex() -> "re.Pattern[str]":
    alt = "|".join(re.escape(s) for s in _PREFIX_CURRENCY)
    return re.compile(rf"({alt})\s?({_NUM})([a-z]*)")


def normalize_units(text: str, dialect: str = "eu") -> str:
    """Read percent, currency and unit expressions in *text* to Basque words."""

    def percent(m: "re.Match[str]") -> str:
        num = m.group(1) or m.group(2)
        suffix = m.group(3)
        spelled = _spell(num, dialect)
        return _attach(f"{_PERCENT_WORD} {spelled}", suffix)

    def prefix_currency(m: "re.Match[str]") -> str:
        word = UNITS[m.group(1)]
        spelled = _spell(m.group(2), dialect)
        suffix = m.group(3)
        return _attach(_order(spelled, word), suffix)

    def postfix(m: "re.Match[str]") -> str:
        spelled = _spell(m.group(1), dialect)
        word = UNITS[m.group(2)]
        suffix = m.group(3) or ""
        return _attach(_order(spelled, word), suffix)

    text = _percent_regex().sub(percent, text)
    text = _prefix_currency_regex().sub(prefix_currency, text)
    text = _postfix_symbol_regex().sub(postfix, text)
    return text


def _order(spelled: str, word: str) -> str:
    """Number-then-unit, except the postposed ``bat`` ("one"): ``euro bat``."""
    if spelled == "bat":
        return f"{word} bat"
    return f"{spelled} {word}"
