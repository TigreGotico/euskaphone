"""Abbreviation (laburdura) expansion — the pre-lattice normalizer stage.

Written Basque is full of period-marked abbreviations that a grapheme-to-phoneme
lattice would mis-read letter by letter (``etab.`` is not "e-t-a-b", it is
``eta abar``). This stage expands a curated, **cited** list of abbreviations to
their full spoken form *before* the lattice — and before the Roman-numeral stage
— so the trailing periods that mark an abbreviation are consumed here and never
confused with the Roman-numeral ordinal period (``XX.``, see
:mod:`euskaphone.romans`).

The list itself is data, not code: it lives in ``data/abbreviations.tsv`` and is
extended by adding a cited row, never by editing this module.

Sources
-------
* **Euskaltzaindia**, **Araua 196**, EBO (I) *"Laburtzapenak: laburdurak eta
  siglak"* — the Academy's norm fixing the standard abbreviation forms and the
  rule that a laburdura is written with a period and read as the full word.
* **EIMA / Basque Government**, J. R. Zubimendi, *Ortotipografia* (Eusko
  Jaurlaritza, 2004), "Laburdurak" — spells the same list plus the ``K.a.`` /
  ``K.o.`` era abbreviations.
  (``papers/iberian/eima_ortotipografia_zubimendi.pdf``)
* **Euskalterm**, *Laburtzapenen Hiztegia* (Gasteiz, 2010) — the exhaustive
  reference dictionary of Basque abbreviations.
  (``papers/iberian/euskalterm_laburtzapenen_hiztegia_2010.pdf``)
"""
from __future__ import annotations

import os
from typing import Dict

_DATA = os.path.join(os.path.dirname(__file__), "data", "abbreviations.tsv")


def _load(path: str = _DATA) -> Dict[str, str]:
    """Load the abbreviation → expansion table (case-folded keys)."""
    table: Dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            abbr, expansion = parts[0], parts[1]
            if abbr and expansion:
                table[abbr.lower()] = expansion
    return table


#: abbreviation (as written, with its period) → full spoken expansion.
ABBREVIATIONS: Dict[str, str] = _load()

#: The bare (period-stripped) keys, for matching a token whose trailing period
#: the tokenizer may have split off (``etab`` as well as ``etab.``).
_BARE = {k.rstrip("."): v for k, v in ABBREVIATIONS.items()}


def expand_token(token: str) -> str:
    """Expand one *token* if it is a known abbreviation, else return it as-is.

    Both the written form with its period (``etab.``) and the bare form
    (``etab``) resolve; multi-dot abbreviations (``K.a.``, ``h.d.``) are matched
    whole. Matching is case-insensitive but the lookup is exact on the letters.
    """
    key = token.lower()
    if key in ABBREVIATIONS:
        return ABBREVIATIONS[key]
    bare = key.rstrip(".")
    if bare in _BARE:
        return _BARE[bare]
    return token


def expand_abbreviations(text: str) -> str:
    """Expand every known abbreviation token in *text*.

    Runs word by word so surrounding punctuation and spacing are preserved for
    tokens that are not abbreviations. Multi-word expansions are inserted inline
    (``etab.`` → ``eta abar``) and flow on to the pronunciation lattice as
    ordinary Basque words.
    """
    out = []
    for word in text.split():
        out.append(expand_token(word))
    return " ".join(out)
