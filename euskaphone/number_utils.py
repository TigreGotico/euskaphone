"""Basque number normalization — the orthography2ipa normalizer stage.

Numbers written as digits carry no orthography a grapheme-to-phoneme lattice can
read, so they are spelled out into Basque words *before* the pronunciation
lattice runs. :func:`normalize_numbers` rewrites every numeric token in running
text, leaving non-numeric tokens untouched;
:class:`~euskaphone.EuskaPhonemizer` wires it as the orthography2ipa
``normalizer``, so the spelled-out words then flow through the eu lattice's
allophony, sandhi and stress like any other word.

Where the work lives
--------------------
The vigesimal (base-20) cardinal/ordinal composition is **not** reimplemented
here — it belongs to the shared parser stack and is delegated to
``ovos-number-parser`` (:func:`ovos_number_parser.pronounce_number` /
:func:`~ovos_number_parser.pronounce_ordinal` with ``lang="eu"``). That module
carries the Euskaltzaindia Araua 7 / Araua 18 cardinal and ordinal tables (the
``-ehun`` hundreds, the ``eta``-drop rule, the ``-garren`` ordinal suffix with
the ``bost`` → ``bos`` drop, and magnitudes up to ``bilioi``).

euskaphone keeps only the layer that needs *orthographic context* and therefore
does not belong upstream:

* **separator handling** — mapping the written comma / period / space grouping
  of a digit string onto an integer or decimal (European/Basque convention);
* **case-suffix attachment** — surfacing the declension ending the writer wrote
  (``1936ko`` → ``… hogeita hamaseiko``, ``20:00etan`` → ``hogeietan``) onto the
  spelled numeral's final element;
* **clock times** — reading an ``HH:MM`` token as ``<hour> [eta <minute>]``;
* **dialect selection** — the Lapurdian ``bortz`` series. ``ovos-number-parser``
  has no dialect axis for ``eu``, so euskaphone applies the ``bost`` → ``bortz``
  substitution (Araua 7 point 3: ``bortz`` is attested in *some* northern
  varieties; Batua ``bost`` is kept everywhere else, "null beats wrong").

Separator convention (documented)
---------------------------------
Basque/European usage: the **comma is the decimal separator** and the **period
and space are thousands separators**. So ``2,5`` is the decimal 2.5,
``1.000.000`` and ``1 000 000`` are one million, and the ambiguous ``2.500``
(period + exactly three digits) is read as the **thousands** grouping 2500, not
as 2.5. A period that does not form a 1–3 + 3-digit grouping (``2.5``, ``2.53``)
falls back to being read as a decimal point.
"""
from typing import List, Optional, Tuple
import re

from ovos_number_parser import pronounce_number, pronounce_ordinal

#: Basque spec codes this module verbalizes for (all eight eu lects).
DIALECTS = (
    "eu",
    "eu-x-bizkaiera",
    "eu-x-gipuzkera",
    "eu-x-lapurtera",
    "eu-x-nafarra-garaia",
    "eu-x-nafarra-beherea",
    "eu-x-zuberera",
    "eu-x-erronkariera",
)

#: Copulative conjunction ("and") joining a clock hour and minute.
_AND = "eta"

#: Decimal separator word ("koma").
_DECIMAL_WORD = "koma"

#: Word for a negative sign ("minus").
_MINUS_WORD = "minus"

#: Ordinal suffix (Araua 18).
_ORDINAL_SUFFIX = "garren"

#: Lapurdian ``bortz`` series (Araua 7 point 3). Applied as a whole-token
#: substitution on the Batua forms ``ovos-number-parser`` returns; Batua
#: ``bost`` is kept for every other lect.
_LAPURDIAN_SUBST = {
    "bost": "bortz",
    "hamabost": "hamabortz",
    "bostehun": "bortzehun",
    "bosgarren": "borzgarren",
    "hamabosgarren": "hamaborzgarren",
}

#: 0-9 spelled, for reading a decimal fraction digit by digit.
_DIGIT_WORDS = {d: pronounce_number(d, "eu") for d in range(10)}

#: A digit string grouped into thousands by periods (``1.000.000``, ``2.500``).
_THOUSANDS_DOT = re.compile(r"^\d{1,3}(\.\d{3})+$")
#: Runs of digit groups separated by single spaces (``1 000 000``).
_SPACE_THOUSANDS = re.compile(r"\b\d{1,3}(?: \d{3})+\b")


def _apply_dialect(spelled: str, dialect: str) -> str:
    """Apply per-dialect word substitutions to a spelled numeral."""
    if dialect != "eu-x-lapurtera":
        return spelled
    return " ".join(_LAPURDIAN_SUBST.get(w, w) for w in spelled.split())


class BasqueNumberParser:
    """Spell an integer or numeric token into Basque words.

    Cardinal and ordinal composition is delegated to ``ovos-number-parser``;
    this class adds the euskaphone-domain layer (decimals from a written
    fraction string, clock times, dialect substitution, token handling).
    """

    def __init__(self, dialect: str = "eu"):
        if dialect not in DIALECTS:
            raise ValueError(
                f"unknown dialect {dialect!r}; expected one of {DIALECTS}")
        self.dialect = dialect

    # -- public API ------------------------------------------------------
    def cardinal(self, n: int) -> str:
        """Spell integer *n* as a Basque cardinal."""
        return _apply_dialect(pronounce_number(n, "eu"), self.dialect)

    def ordinal(self, n: int) -> str:
        """Spell integer *n* as a Basque ordinal (``-garren``)."""
        return _apply_dialect(pronounce_ordinal(n, "eu"), self.dialect)

    def decimal(self, whole: int, frac: str) -> str:
        """Spell a decimal: whole part, ``koma``, then digit-by-digit frac.

        The fraction is read from the *written* digit string, so leading zeros
        and arbitrary length are preserved (``2,05`` → ``bi koma zero bost``).
        """
        digits = " ".join(
            _apply_dialect(_DIGIT_WORDS[int(d)], self.dialect) for d in frac)
        return f"{self.cardinal(whole)} {_DECIMAL_WORD} {digits}"

    def year(self, n: int) -> str:
        """Spell a year. Basque reads years as plain cardinals (Araua 18)."""
        return self.cardinal(n)

    def clock(self, hour: int, minute: int) -> str:
        """Spell a ``HH:MM`` clock time as ``<hour> [eta <minute>]``."""
        head = self.cardinal(hour)
        if minute == 0:
            return head
        return f"{head} {_AND} {self.cardinal(minute)}"

    # -- token handling --------------------------------------------------
    def pronounce_token(self, token: str, as_ordinal: bool = False
                        ) -> Optional[str]:
        """Spell one numeric *token* (``"12"``, ``"3,5"``, ``"-4"``), or None."""
        t = token.strip()
        neg = t.startswith("-")
        if neg:
            t = t[1:]
        parsed = _parse_core(t)
        if parsed is None:
            return None
        if parsed[0] == "dec":
            out = self.decimal(parsed[1], parsed[2])
        else:
            n = parsed[1]
            out = self.ordinal(n) if as_ordinal else self.cardinal(n)
        return f"{_MINUS_WORD} {out}" if neg else out


# ---------------------------------------------------------------------------
# Separator parsing.
# ---------------------------------------------------------------------------

def _parse_core(core: str) -> Optional[Tuple]:
    """Map a written numeric string onto an int/decimal per Basque convention.

    Returns ``("int", n)``, ``("dec", whole, frac_str)`` or ``None``. Comma is
    the decimal separator; period and space are thousands separators, with the
    ``2.500``-style period+3-digit grouping read as thousands (see the module
    docstring's separator convention).
    """
    if "," in core:
        whole_s, _, frac_s = core.partition(",")
        whole_s = whole_s.replace(".", "").replace(" ", "")  # thousands grouping
        if whole_s.isdigit() and frac_s.isdigit():
            return ("dec", int(whole_s), frac_s)
        return None
    if "." in core:
        if _THOUSANDS_DOT.match(core):
            return ("int", int(core.replace(".", "")))
        # a lone period that is not a thousands grouping reads as a decimal point
        whole_s, _, frac_s = core.partition(".")
        if core.count(".") == 1 and whole_s.isdigit() and frac_s.isdigit():
            return ("dec", int(whole_s), frac_s)
        return None
    if core.isdigit():
        return ("int", int(core))
    return None


# ---------------------------------------------------------------------------
# Token rewriting over running text.
# ---------------------------------------------------------------------------

def _attach_suffix(spelled: str, suffix: str) -> str:
    """Attach a declension ``suffix`` to the LAST word of a spelled numeral.

    Basque declines a numeral phrase on its final element only
    (``1936ko`` → ``… hogeita hamaseiko``; ``20:00etan`` → ``hogeietan``). The
    surface case ending the writer wrote is appended verbatim to the last
    spelled word; euskaphone does not re-derive Basque numeral morphophonology,
    it surfaces the author's ending onto the pronounced final element.
    """
    if not suffix:
        return spelled
    words = spelled.split()
    words[-1] = f"{words[-1]}{suffix}"
    return " ".join(words)


def _split_affixes(word: str) -> Tuple[str, str, str]:
    """Split leading punctuation and a trailing letter case-suffix off a token.

    Returns ``(prefix, core, suffix)`` where ``core`` is the digit/colon/comma
    body and ``suffix`` is any trailing alphabetic case ending (``1936ko`` →
    ``("", "1936", "ko")``). Trailing non-letter punctuation stays in the
    prefix/word passthrough.
    """
    start = 0
    while start < len(word) and not (word[start].isdigit() or word[start] == "-"):
        start += 1
    prefix = word[:start]
    rest = word[start:]
    end = len(rest)
    while end > 0 and rest[end - 1].isalpha():
        end -= 1
    core = rest[:end]
    suffix = rest[end:]
    return prefix, core, suffix


def _try_time(core: str, suffix: str, parser: "BasqueNumberParser"
             ) -> Optional[str]:
    """Verbalize a ``HH:MM`` core with an optional case suffix, or None."""
    if ":" not in core:
        return None
    h_s, _, m_s = core.partition(":")
    if not (h_s.isdigit() and m_s.isdigit()):
        return None
    spelled = parser.clock(int(h_s), int(m_s))
    return _attach_suffix(spelled, suffix)


def normalize_numbers(text: str, dialect: str = "eu",
                      strict: bool = False) -> str:
    """Replace numeric tokens in *text* with their Basque written forms.

    This is the orthography2ipa normalizer stage: it runs on raw orthographic
    text before the pronunciation lattice, so spelled-out numbers are then
    transcribed like any other word. Handles cardinals, decimals, negative
    numbers, period/space thousands separators, ``HH:MM`` clock times, and
    case-suffixed numerals (``1936ko`` → ``… hamaseiko``); an explicit
    ``<digits>garren`` token is read as an ordinal. Non-numeric tokens are
    returned untouched.

    :param dialect: an eu spec code (see :data:`DIALECTS`).
    :param strict: when true, re-raise a token that fails to verbalize.
    """
    if dialect not in DIALECTS:
        dialect = "eu"
    parser = BasqueNumberParser(dialect)
    # collapse space-grouped thousands ("1 000 000" -> "1000000") before split
    text = _SPACE_THOUSANDS.sub(lambda m: m.group(0).replace(" ", ""), text)
    out: List[str] = []
    for word in text.split():
        prefix, core, suffix = _split_affixes(word)
        if not core:
            out.append(word)
            continue
        try:
            # explicit ordinal: "16garren" / "16garrena" …
            as_ord = suffix.startswith(_ORDINAL_SUFFIX)
            if as_ord:
                trailing = suffix[len(_ORDINAL_SUFFIX):]
                spelled = parser.pronounce_token(core, as_ordinal=True)
                spelled = _attach_suffix(spelled, trailing) if spelled else None
            else:
                spelled = _try_time(core, suffix, parser)
                if spelled is None:
                    base = parser.pronounce_token(core)
                    spelled = _attach_suffix(base, suffix) if base else None
        except Exception:
            if strict:
                raise
            spelled = None
        out.append(f"{prefix}{spelled}" if spelled is not None else word)
    return " ".join(out)
