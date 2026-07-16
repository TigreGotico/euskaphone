"""Date reading — numeric dates to the ``2024ko urtarrilaren 15ean`` form.

Euskaltzaindia Araua 37 (*"Data nola adierazi"*) fixes the spoken shape of a
date as **year-genitive + month-genitive + day-inessive**:

    1995eko martxoaren 7an   ("on the 7th of March 1995")

* the **year** takes the locative-genitive ``-ko`` / ``-eko`` and is read as a
  plain cardinal (no ``-garren``): ``1995eko``, ``2024ko``;
* the **month** name takes the possessive genitive ``-aren``:
  ``martxoaren``, ``urtarrilaren``;
* the **day** takes the inessive ``-an`` / ``-ean``: ``7an``, ``15ean``.

This stage converts **numeric** date tokens (``1995/03/07``, ``2024-01-15``,
``15/01/2024``, ``1995/III/07``) into that spelled form, composing the cardinal
verbalizer through :mod:`euskaphone.numverbal`. A date that is *already* written
with a month name (``2024ko urtarrilaren 15ean``) needs nothing from this stage —
its ``2024ko`` and ``15ean`` are ordinary case-suffixed numerals the downstream
number stage verbalizes on its own.

Field order is resolved without a locale guess: the four-digit (or ``>31``) field
is the year, and its position decides ISO ``Y/M/D`` vs. European ``D/M/Y``; a
Roman-numeral field is the month. A triple that does not validate as a real
calendar date (month 1–12, day 1–31, a four-digit year) is left untouched — null
beats a wrong reading.

Sources
-------
* **Euskaltzaindia**, **Araua 37**, *"Data nola adierazi"* (Donostia,
  1995-07-28) — the ``1995eko martxoaren 7an`` recommendation, the numeric
  formats (``1995/03/07``, ``1995-03-27``, ``1995/III/07``), and the
  year-``ko`` / month-``aren`` / day-``an`` composition.
  (``papers/iberian/euskaltzaindia_araua37_data_nola_adierazi.pdf``)
"""
from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

from euskaphone.numverbal import inessive, locative_genitive, spell_cardinal
from euskaphone.romans import roman_to_int

#: The twelve month names (Batua) in the possessive-genitive form dates use.
MONTHS_GENITIVE: Dict[int, str] = {
    1: "urtarrilaren",
    2: "otsailaren",
    3: "martxoaren",
    4: "apirilaren",
    5: "maiatzaren",
    6: "ekainaren",
    7: "uztailaren",
    8: "abuztuaren",
    9: "irailaren",
    10: "urriaren",
    11: "azaroaren",
    12: "abenduaren",
}

# three numeric/Roman fields separated by / - or .
_DATE_RE = re.compile(
    r"^(\d{1,4}|[IVXLCDM]+)[/.\-](\d{1,4}|[IVXLCDM]+)[/.\-](\d{1,4}|[IVXLCDM]+)$"
)


def _as_int(field: str) -> Optional[int]:
    if field.isdigit():
        return int(field)
    return roman_to_int(field)


def _resolve_fields(a: int, b: int, c: int, a_raw: str, c_raw: str
                    ) -> Optional[Tuple[int, int, int]]:
    """Return ``(year, month, day)`` from three integers, or None if not a date."""
    # a four-digit written field, or a value that cannot be a day/month, is the
    # year; its position picks ISO (year first) vs. European (year last).
    if len(a_raw) == 4 or a > 31:
        year, month, day = a, b, c            # ISO  Y/M/D
    elif len(c_raw) == 4 or c > 31:
        year, month, day = c, b, a            # European D/M/Y
    else:
        return None
    if not (1 <= month <= 12 and 1 <= day <= 31 and year >= 1):
        return None
    return year, month, day


def compose_date(year: int, month: int, day: int, dialect: str = "eu") -> str:
    """Spell ``(year, month, day)`` as ``<year>ko <month>aren <day>an``."""
    y = locative_genitive(spell_cardinal(year, dialect))
    d = inessive(spell_cardinal(day, dialect))
    return f"{y} {MONTHS_GENITIVE[month]} {d}"


def _read_token(tok: str, dialect: str) -> Optional[str]:
    m = _DATE_RE.match(tok)
    if not m:
        return None
    ints = [_as_int(g) for g in m.groups()]
    if any(v is None for v in ints):
        return None
    fields = _resolve_fields(ints[0], ints[1], ints[2],
                             m.group(1), m.group(3))
    if fields is None:
        return None
    return compose_date(*fields, dialect=dialect)


def normalize_dates(text: str, dialect: str = "eu") -> str:
    """Convert numeric date tokens in *text* to the spelled Basque form."""
    out = []
    for word in text.split():
        # keep any leading/trailing punctuation the token carries
        prefix = ""
        suffix = ""
        core = word
        while core and not (core[0].isdigit() or core[0] in "IVXLCDM"):
            prefix += core[0]
            core = core[1:]
        while core and core[-1] in ".,;:!?)»\"'":
            # a trailing period may belong to the date separator; only peel
            # punctuation that cannot be part of a Y/M/D triple's structure
            if core[-1] == "." and _DATE_RE.match(core):
                break
            suffix = core[-1] + suffix
            core = core[:-1]
        spelled = _read_token(core, dialect)
        out.append(f"{prefix}{spelled}{suffix}" if spelled else word)
    return " ".join(out)
