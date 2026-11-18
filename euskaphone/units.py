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

The symbol→word table lives in ``data/units.tsv`` (data, not code).

text2spoken reads these forms for :func:`euskaphone.normalize.normalize_text`.
Two fallbacks read what it leaves as written: a currency symbol before a number
with a case ending (:func:`read_currency_before_number`) and the unit symbols of
:data:`LEFT_BY_TEXT2SPOKEN` (:func:`read_unit_symbols`). :func:`normalize_units`,
the stage that text2spoken replaces, is deprecated.

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
from typing import Dict, List

from euskaphone.deprecation import warn_deprecated
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
    """Deprecated: :func:`euskaphone.normalize.normalize_text` reads units,
    currency and percent through text2spoken.

    Read percent, currency and unit expressions in *text* to Basque words.
    """
    warn_deprecated("units.normalize_units",
                    "use euskaphone.normalize.normalize_text, which reads units through text2spoken")

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


# ---------------------------------------------------------------------------
# Fallbacks: the forms that text2spoken leaves as written. Each one runs on
# text2spoken's output and reads only its own form.
# ---------------------------------------------------------------------------

def _one(suffix: str) -> str:
    """``bat`` ("one") with the case ending of its unit: ``bateko``, ``batek``.

    Araua 197 p.13 puts the ending on ``bat``: «1 s-eko iraupena (segundo bateko
    iraupena)», «1 kg-ek? (... kilogramo batek?)». ``bat`` ends in a consonant,
    so an ending that starts with a consonant takes the epenthetic ``e``.
    """
    if suffix and suffix[0] not in _VOWELS:
        suffix = "e" + suffix
    return "bat" + suffix


def _counted(spelled: str, word: str, suffix: str) -> str:
    """The number, its unit word and the case ending: ``bost gramoko``, and
    ``gramo bateko`` for one."""
    if spelled == "bat":
        return f"{word} {_one(suffix)}"
    return _attach(f"{spelled} {word}", suffix)


def read_currency_before_number(text: str, dialect: str = "eu") -> str:
    """Read a currency symbol before a number with a case ending:
    ``€5eko`` → ``bost euroko``.

    The norm writes the number first (Araua 197), and text2spoken reads
    ``5 €-ko`` and ``€5``. It leaves ``€5eko`` as written.
    TODO(text2spoken issue: CURRENCY_BEFORE_NUMBER)
    """
    def read(m: "re.Match[str]") -> str:
        return _counted(_spell(m.group(2), dialect), UNITS[m.group(1)], m.group(3))
    return _prefix_currency_regex().sub(read, text)


#: The unit symbols that text2spoken leaves as written after a number. Araua
#: 197 names each one: ``t`` (tona), ``mg`` (miligramo), ``h`` (ordu), ``g``
#: (gramo), and the prefixes ``d`` (dezi-) and ``c`` (zenti-) of ``dm``, ``ml``
#: and ``cl``.
#: TODO(text2spoken issue: UNIT_SYMBOL)
LEFT_BY_TEXT2SPOKEN = frozenset({"dm", "g", "mg", "t", "ml", "cl", "h"})

#: A symbol written as its own word, with a hyphenated case ending and
#: punctuation: ``g``, ``g-ko``, ``h.``.
_SYMBOL_WORD = re.compile(r"^([^\W\d_]+)(?:-([a-z]+))?([.,;:!?)»\"']*)$")

#: A number written in digits, as the word before a symbol.
_DIGITS = re.compile(r"-?\d+(?:[.,]\d+)*")


def _glued_symbol_regex() -> "re.Pattern[str]":
    alt = "|".join(re.escape(s) for s in sorted(LEFT_BY_TEXT2SPOKEN, key=len, reverse=True))
    return re.compile(rf"(?<![\w.,])({_NUM})({alt})(?:-([a-z]+))?(?![a-zA-Z])")


def _symbols(words: List[str]) -> List[int]:
    return [i for i, w in enumerate(words)
            if (m := _SYMBOL_WORD.match(w)) and m.group(1) in LEFT_BY_TEXT2SPOKEN]


def read_unit_symbols(spoken: str, written: str, dialect: str = "eu") -> str:
    """Read the symbols of :data:`LEFT_BY_TEXT2SPOKEN` after a number.

    ``spoken`` is text2spoken's reading of ``written``. text2spoken reads the
    number of ``5 g`` and leaves the symbol (``bost g``), so the symbol becomes
    its word and the number stays as text2spoken read it: ``bost gramo``. A
    case ending moves to the word (``bost g-ko`` → ``bost gramoko``), and ``bat``
    follows the word and takes the ending (``1 g-ko`` → ``gramo bateko``).
    text2spoken leaves a symbol glued to its digits (``5g``) whole, and this
    reads both. A symbol that does not follow digits in ``written`` is a letter,
    and stays. The whitespace between words stays as written.
    """
    def glued(m: "re.Match[str]") -> str:
        return _counted(_spell(m.group(1), dialect), UNITS[m.group(2)], m.group(3) or "")
    spoken = _glued_symbol_regex().sub(glued, spoken)

    written_words = written.split()
    numbers = [written_words[i - 1] if i > 0 and _DIGITS.fullmatch(written_words[i - 1]) else None
               for i in _symbols(written_words)]
    parts = re.split(r"(\s+)", spoken)
    words = parts[::2]
    positions = _symbols(words)
    if len(positions) != len(numbers):
        return spoken
    for i, number in zip(positions, numbers):
        if number is None:
            continue
        symbol, suffix, trail = _SYMBOL_WORD.match(words[i]).groups()
        if number == "1" and i > 0 and words[i - 1] == "bat":
            words[i - 1], words[i] = UNITS[symbol], _one(suffix or "") + trail
        else:
            words[i] = _attach(UNITS[symbol], suffix or "") + trail
    parts[::2] = words
    return "".join(parts)
