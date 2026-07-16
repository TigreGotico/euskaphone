"""Roman-numeral reading — the ordinal-period and monarch conventions.

Formal Basque writes ordinals with a Roman numeral plus a period, and the period
*is* the ordinal marker: ``XX. mendea`` is read ``hogeigarren mendea`` ("the
twentieth century"), exactly the digit-plus-period convention Euskaltzaindia
Araua 18 fixes for Arabic digits (``20.`` = ``hogeigarren``), carried onto Roman
numerals. Monarch and pope names, by contrast, carry a Roman numeral
that is read as a *postposed* ordinal bearing the singular article ``-a``, and
that ordinal is **always declined**: ``Luis XIV`` (written ``Luis XIV.a``) →
``Luis hamalaugarrena`` ("Louis the fourteenth"), ``Benedikto XVI.aren`` →
``Benedikto hamaseigarrenaren``, and the first of a name is the suppletive
``lehena`` (``Karlos I`` → ``Karlos lehena``).

This stage produces Basque *words* directly (it does not leave digits for the
number stage), composing the cardinal/ordinal composer through
:mod:`euskaphone.numverbal`.

The period ambiguity, and how it is resolved
---------------------------------------------
A lone ``V.`` at the end of a sentence is a Roman numeral followed by a full
stop, not the ordinal "fifth". The heuristic here:

* **Monarch reading wins first**: a Roman numeral immediately preceded by a
  capitalized word (a proper name — ``Luis``, ``Elisabet``, ``Joan Paulo``) is
  read as a postposed ordinal-with-article, whether or not a period follows
  (the period is then sentence punctuation).
* **Ordinal-period** otherwise: a Roman numeral followed by ``.`` is read as an
  ordinal **only when the next token begins with a lower-case letter** — i.e. a
  common noun the ordinal modifies (``mendea``, ``kapitulua``, ``atala``). A
  Roman-plus-period that ends the string, or is followed by a capitalized word or
  more punctuation, is treated as a literal numeral + full stop and left
  untouched.

This deliberately errs toward *leaving text alone* when the reading is genuinely
ambiguous ("null beats wrong").

Sources
-------
* **Euskaltzaindia**, **Araua 18**, *"Ordinalen eta banatzaileen idazkera"* — the
  digit-plus-period = ordinal convention and the century-as-ordinal reading.
  (``papers/iberian/euskaltzaindia_araua18_ordinalak.pdf``)
* **EIMA / Basque Government**, J. R. Zubimendi, *Ortotipografia* (Eusko
  Jaurlaritza, 2004), "Ordinalak" §2: a period after a digit or Roman numeral is
  the written abbreviation of the ``-garren`` suffix (``XV. biltzarra``,
  ``XVII. eta XVIII. mendeetan``), and a laburdura is read as the full expanded
  word. (``papers/iberian/eima_ortotipografia_zubimendi.pdf``)
* **Euskaltzaindia**, *Euskara Batuaren Eskuliburua*, "zenbaki erromatarrak" —
  dynastic names take a postposed Roman numeral with the article, and the
  ordinal is always declined (``Luis XIV.a``, ``Joan XXIII.a``,
  ``Benedikto XVI.aren``; standard-Batua fifth is ``bosgarren(a)``).
"""
from __future__ import annotations

import re
from typing import Optional

from euskaphone.numverbal import spell_ordinal

#: A strict Roman numeral 1..3999 (subtractive notation), whole-token.
_ROMAN_RE = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)

_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> Optional[int]:
    """Parse a strict Roman numeral to its integer value, or None.

    Only canonical subtractive forms 1..3999 are accepted; ``IIII`` or ``VV``
    return None so ordinary uppercase words are never mistaken for numerals.
    """
    if not s or not _ROMAN_RE.match(s):
        return None
    total = 0
    prev = 0
    for ch in reversed(s):
        val = _VALUES[ch]
        total += -val if val < prev else val
        prev = max(prev, val)
    return total


def _declined_ordinal(n: int, suffix: str, dialect: str = "eu") -> str:
    """Ordinal + an explicit case ending (``14, "a"`` → ``hamalaugarrena``).

    The first of a name is the suppletive ``lehen`` before the ending
    (``lehena``, ``lehenaren``); all others attach the ending to the
    ``-garren`` ordinal.
    """
    stem = "lehen" if n == 1 else spell_ordinal(n, dialect)
    return f"{stem}{suffix}"


def monarch_ordinal(n: int, dialect: str = "eu") -> str:
    """Postposed monarch/pope ordinal with the article (``14`` → ``hamalaugarrena``).

    The written form carries the article ``.a`` (``Luis XIV.a``); a bare
    ``Luis XIV`` is read the same way. The first of a name is ``lehena``.
    """
    return _declined_ordinal(n, "a", dialect)


def _is_capitalized_name(tok: str) -> bool:
    """Whether *tok* looks like a proper name (initial upper, has a lower letter)."""
    core = tok.strip("«»\"'()[].,;:")
    return bool(core) and core[0].isupper() and any(c.islower() for c in core)


# ROMAN, ROMAN., or ROMAN.<lowercase declension> (e.g. "XIV", "XX.", "XVI.aren").
# A lowercase declension is only recognised AFTER the period, so ordinary words
# that merely start with Roman letters ("Luis", "Ikusi", "Divide") never match.
_TOKEN_RE = re.compile(r"^([IVXLCDM]+)(?:(\.)([a-z]+)?)?$")


def normalize_romans(text: str, dialect: str = "eu") -> str:
    """Read Roman-numeral ordinals and monarch numerals in *text* to words.

    See the module docstring for the period/monarch disambiguation heuristic.
    Tokens that are not a resolvable Roman-numeral reading are left untouched.
    """
    tokens = text.split()
    out = []
    for i, tok in enumerate(tokens):
        m = _TOKEN_RE.match(tok)
        n = roman_to_int(m.group(1)) if m else None
        if n is None:
            out.append(tok)
            continue
        has_period = m.group(2) is not None
        suffix = m.group(3)

        if suffix:
            # explicit declined ordinal / monarch form: "XIV.a", "XVI.aren".
            # The written ending already carries the article, so read it as a
            # declined ordinal regardless of the preceding word.
            out.append(_declined_ordinal(n, suffix, dialect))
            continue

        prev_name = i > 0 and _is_capitalized_name(tokens[i - 1])
        if prev_name:
            # monarch reading: Roman after a proper name (a bare period is
            # sentence punctuation and is re-attached).
            word = monarch_ordinal(n, dialect)
            out.append(f"{word}." if has_period else word)
            continue

        if has_period:
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            nxt_core = nxt.lstrip("«»\"'([")
            if nxt_core[:1].islower():
                # Roman + period + lower-case common noun -> ordinal
                out.append(spell_ordinal(n, dialect))
                continue

        # ambiguous / sentence-final Roman -> leave literal
        out.append(tok)
    return " ".join(out)
