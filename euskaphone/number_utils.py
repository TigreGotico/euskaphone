"""Basque number spelling, and the number fallbacks of the normalizer.

text2spoken reads the numbers of running text for
:func:`euskaphone.normalize.normalize_text`. This module keeps two things:

* :class:`BasqueNumberParser`, which spells an integer or a numeric token as
  Basque words, with the Lapurdian ``bortz`` series;
* the fallbacks for four number forms that text2spoken leaves as written:
  space-grouped thousands (:func:`read_space_grouped_numbers`), digits with the
  ordinal suffix (:func:`read_garren_ordinals`), a point as the decimal mark
  (:func:`read_dot_decimals`) and digits with a glued case ending
  (:func:`read_glued_case_endings`). Each fallback reads its form with
  :class:`BasqueNumberParser`, and goes when text2spoken reads the form;
* :func:`read_code_digits`, which reads the digits of a code (``B12``).
  text2spoken leaves a code as a name, and the lattice deletes digits, so this
  stage stays.

:func:`normalize_numbers`, the number stage that text2spoken replaces, is
deprecated.

Where the work lives
--------------------
The vigesimal (base-20) cardinal/ordinal composition is **not** reimplemented
here. :class:`BasqueNumberParser` delegates it to ``ovos-number-parser``
(:func:`ovos_number_parser.pronounce_number` /
:func:`~ovos_number_parser.pronounce_ordinal` with ``lang="eu"``). That module
carries the Euskaltzaindia Araua 7 / Araua 18 cardinal and ordinal tables (the
``-ehun`` hundreds, the ``eta``-drop rule, the ``-garren`` ordinal suffix with
the ``bost`` → ``bos`` drop, and magnitudes up to ``bilioi``).

euskaphone adds the layer that needs *orthographic context*:

* **separator handling** — mapping the written comma / period / space grouping
  of a digit string onto an integer or decimal (European/Basque convention);
* **case-suffix attachment** — surfacing the declension ending the writer wrote
  (``1936ko`` → ``… hogeita hamaseiko``) onto the spelled numeral's final
  element;
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

from orthography2ipa import resolve
from ovos_number_parser import pronounce_number, pronounce_ordinal

from euskaphone.deprecation import warn_deprecated

#: The eight eu lects, by the codes this package documents, each mapped to the
#: key orthography2ipa registers the spec under. orthography2ipa keeps the old
#: key of a renamed spec as an exact alias, so both keys name the same lect.
_SPEC_KEYS = {code: resolve(code) for code in (
    "eu",
    "eu-x-bizkaiera",
    "eu-x-gipuzkera",
    "eu-x-lapurtera",
    "eu-x-nafarra-garaia",
    "eu-x-nafarra-beherea",
    "eu-x-zuberera",
    "eu-x-erronkariera",
)}

#: Basque spec codes this module verbalizes for (all eight eu lects).
DIALECTS = tuple(_SPEC_KEYS.values())

_LAPURDIAN = _SPEC_KEYS["eu-x-lapurtera"]

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
    if dialect != _LAPURDIAN:
        return spelled
    return " ".join(_LAPURDIAN_SUBST.get(w, w) for w in spelled.split())


class BasqueNumberParser:
    """Spell an integer or numeric token into Basque words.

    Cardinal and ordinal composition is delegated to ``ovos-number-parser``;
    this class adds the euskaphone-domain layer (decimals from a written
    fraction string, clock times, dialect substitution, token handling).
    """

    def __init__(self, dialect: str = "eu"):
        dialect = _SPEC_KEYS.get(dialect, dialect)
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
    """Deprecated: :func:`euskaphone.normalize.normalize_text` reads numbers
    through text2spoken.

    Replace numeric tokens in *text* with their Basque written forms. Handles
    cardinals, decimals, negative numbers, period/space thousands separators,
    ``HH:MM`` clock times, and case-suffixed numerals (``1936ko`` → ``…
    hamaseiko``); an explicit ``<digits>garren`` token is read as an ordinal.
    Non-numeric tokens are returned untouched.

    :param dialect: an eu spec code (see :data:`DIALECTS`).
    :param strict: when true, re-raise a token that fails to verbalize.
    """
    warn_deprecated("number_utils.normalize_numbers",
                    "use euskaphone.normalize.normalize_text, which reads numbers through text2spoken")
    dialect = _SPEC_KEYS.get(dialect, dialect)
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


# ---------------------------------------------------------------------------
# Fallbacks: the number forms that text2spoken leaves as written. Each one runs
# on text2spoken's output and reads only its own form.
# ---------------------------------------------------------------------------

def _parser(dialect: str) -> BasqueNumberParser:
    dialect = _SPEC_KEYS.get(dialect, dialect)
    return BasqueNumberParser(dialect if dialect in DIALECTS else "eu")


def read_space_grouped_numbers(text: str, dialect: str = "eu") -> str:
    """Read digit groups that a space separates: ``1 000 000`` → ``milioi bat``.

    Araua 203 recommends a space between groups of three digits. text2spoken
    leaves them as written: https://github.com/TigreGotico/text2spoken/issues/295
    """
    parser = _parser(dialect)
    return _SPACE_THOUSANDS.sub(
        lambda m: parser.pronounce_token(m.group().replace(" ", "")), text)


#: Digits with the ordinal suffix and a case ending: ``16garren``, ``10garrena``.
_GARREN = re.compile(rf"(?<![\w.,])(\d+(?:\.\d{{3}})*){_ORDINAL_SUFFIX}([^\W\d_]*)")


def read_garren_ordinals(text: str, dialect: str = "eu") -> str:
    """Read digits with the ordinal suffix: ``16garren`` → ``hamaseigarren``.

    Araua 203 marks the writing as wrong (``2garren``), but its reading is the
    ordinal. text2spoken leaves it as written:
    https://github.com/TigreGotico/text2spoken/issues/263
    """
    parser = _parser(dialect)

    def read(m: "re.Match[str]") -> str:
        spelled = parser.pronounce_token(m.group(1), as_ordinal=True)
        return _attach_suffix(spelled, m.group(2)) if spelled else m.group()
    return _GARREN.sub(read, text)


#: A number with one point between digits, and an optional case ending.
_DOT_NUMBER = re.compile(r"(?<![\w.,])(\d+\.\d+)(?!\d|[.,]\d)([^\W\d_]*)")


def read_dot_decimals(text: str, dialect: str = "eu") -> str:
    """Read a point as the decimal mark: ``2.5`` → ``bi koma bost``.

    The comma is the Basque decimal mark (Araua 203), and a point before three
    digits groups thousands (``2.500``). text2spoken reads both, and leaves any
    other point between digits as written.
    https://github.com/TigreGotico/text2spoken/issues/264
    """
    parser = _parser(dialect)

    def read(m: "re.Match[str]") -> str:
        spelled = parser.pronounce_token(m.group(1))
        return _attach_suffix(spelled, m.group(2)) if spelled else m.group()
    return _DOT_NUMBER.sub(read, text)


#: Digits with a lower-case ending glued to them: ``100dik``.
_GLUED_ENDING = re.compile(r"(?<![\w.,])(\d+)([a-z]+)(?!\w)")


def read_glued_case_endings(text: str, dialect: str = "eu") -> str:
    """Read digits with a case ending that text2spoken leaves: ``100dik`` →
    ``ehundik``.

    Araua 203 p.38, note 32: «Ehun hitzaren kasuan, ehunetik da forma
    estandarra, baina ehundik ere erabiltzen da, batez ere ehundik gora / 100dik
    gora esapidean». text2spoken reads ``100etik`` and leaves ``100dik`` as
    written. The ending stays as written after the number.
    https://github.com/TigreGotico/text2spoken/issues/273
    """
    parser = _parser(dialect)

    def read(m: "re.Match[str]") -> str:
        return parser.pronounce_token(m.group(1)) + m.group(2)
    return _GLUED_ENDING.sub(read, text)


#: A number in digits, as a code holds it: the ``12`` of ``B12``, the ``1.0`` of ``v1.0``.
_CODE_DIGITS = re.compile(r"\d+(?:[.,]\d+)*")


def read_code_digits(text: str, dialect: str = "eu") -> str:
    """Read the digits that are still in the text: ``B12`` → ``Bhamabi``.

    text2spoken leaves a code as written (``5G``, ``B12``, ``AP-8``, ``H2O``),
    because a code is a name. The orthography2ipa lattice reads letters only, and
    deletes the digits. So each run of digits reads as a number in its place, and
    the letters and marks around it stay: ``5G`` → ``bostG``, ``AP-8`` →
    ``AP-zortzi``, ``24/7`` → ``hogeita lau/zazpi``. This runs after every
    fallback, so it reads only digits that nothing else reads.
    """
    parser = _parser(dialect)

    def read(m: "re.Match[str]") -> str:
        # A run that is no number, such as ``1.0.0``, reads group by group.
        return parser.pronounce_token(m.group()) or re.sub(
            r"\d+", lambda d: parser.pronounce_token(d.group()), m.group())
    return _CODE_DIGITS.sub(read, text)
