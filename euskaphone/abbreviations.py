"""Abbreviations (laburdurak): the table and the abbreviation fallback.

Written Basque is full of period-marked abbreviations that a grapheme-to-phoneme
lattice would mis-read letter by letter (``etab.`` is not "e-t-a-b", it is
``eta abar``). text2spoken reads most of them for
:func:`euskaphone.normalize.normalize_text`. :func:`read_left_abbreviations` reads
the abbreviations of this table that text2spoken leaves as written.
:func:`expand_abbreviations`, the stage that text2spoken replaces, is deprecated.

The list itself is data, not code: it lives in ``data/abbreviations.tsv`` and is
extended by adding a cited row, never by editing this module.

Sources
-------
* **Euskaltzaindia**, **Araua 196**, EBO (I) *"Laburtzapenak: laburdurak eta
  siglak"* — the Academy's norm fixing the standard abbreviation forms and the
  rule that a laburdura is written with a period and read as the full word.
  Section 4 (p. 12): "Punturik ez badu, ez da laburdura" — with no period, it
  is not an abbreviation.
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
import re
from typing import Dict

from euskaphone.deprecation import warn_deprecated

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


def expand_token(token: str) -> str:
    """Expand one *token* if it is a known abbreviation, else return it as-is.

    Only the written form with its period resolves (``etab.``, and the
    multi-dot ``K.a.`` and ``h.d.`` whole). Araua 196 section 4: a token with no
    period is not an abbreviation, so ``or`` and ``k`` stay words. Matching is
    case-insensitive but the lookup is exact on the letters.
    """
    return ABBREVIATIONS.get(token.lower(), token)


def expand_abbreviations(text: str) -> str:
    """Deprecated: :func:`euskaphone.normalize.normalize_text` reads
    abbreviations through text2spoken.

    Expand every known abbreviation token in *text*, word by word.
    """
    warn_deprecated("abbreviations.expand_abbreviations",
                    "use euskaphone.normalize.normalize_text, which reads abbreviations through text2spoken")
    return " ".join(expand_token(word) for word in text.split())


#: The abbreviations of the table that text2spoken leaves as written, in any
#: case: ``h.d.``, ``kap.`` and ``lib.`` (Araua 196 lists them), ``orr.`` (Araua
#: 196 marks the writing as wrong, but its reading is clear), and ``etab.`` and
#: ``k.a.`` in a case that text2spoken does not read (``ETAB.``).
#: https://github.com/TigreGotico/text2spoken/issues/265
LEFT_BY_TEXT2SPOKEN = frozenset({"h.d.", "kap.", "lib.", "orr.", "etab.", "k.a."})

#: The abbreviations of :data:`LEFT_BY_TEXT2SPOKEN` that end a list, and so can
#: end a sentence before a capital (Araua 196 p.31: «musika klasikoa, etab.»).
#: text2spoken keeps the stop of ``etab.`` before a capital in the same way.
_SENTENCE_FINAL = frozenset({"etab."})

#: Punctuation that can follow the period of an abbreviation.
_TRAILING = ",;:!?)»\"'"


def read_left_abbreviations(text: str) -> str:
    """Expand each abbreviation of :data:`LEFT_BY_TEXT2SPOKEN` in *text*.

    At the end of a sentence the period of the abbreviation also ends the
    sentence, so one period stays (Araua 196, p. 31): ``kap.`` at the end reads
    ``kapitulua.``. A sentence ends at the end of the text, when no other mark
    follows the period. A capital after the period starts a name or a sentence
    (Araua 196, p. 30: «haren ondoren datorren hitza letra xehez hasita idazten
    da, non eta ez den izen berezi bat edo esaldiaren hasierako hitza»), so the
    period stays before a capital only after an abbreviation that ends a list
    (:data:`_SENTENCE_FINAL`): ``h.d. Euskal Herrian`` reads ``hau da Euskal
    Herrian``. The whitespace between words stays as written.
    """
    parts = re.split(r"(\s+)", text)
    words = parts[::2]
    for i, word in enumerate(words):
        core = word.rstrip(_TRAILING)
        if core.lower() not in LEFT_BY_TEXT2SPOKEN:
            continue
        following = next((w for w in words[i + 1:] if w), "")
        ends_sentence = word == core and (
            not following or (core.lower() in _SENTENCE_FINAL and following[0].isupper()))
        stop = "." if ends_sentence else ""
        words[i] = ABBREVIATIONS[core.lower()] + stop + word[len(core):]
    parts[::2] = words
    return "".join(parts)
