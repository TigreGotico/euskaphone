"""Basque number verbalization — the orthography2ipa normalizer stage.

Numbers written as digits carry no orthography a grapheme-to-phoneme lattice can
read, so they are spelled out into Basque words *before* the pronunciation
lattice runs. This mirrors the architecture tugaphone uses for Portuguese and
mwl_phonemizer for Mirandese: a :class:`BasqueNumberParser` turns one numeric
token into words, and :func:`normalize_numbers` rewrites every numeric token in
running text, leaving non-numeric tokens untouched.
:class:`~euskaphone.EuskaPhonemizer` wires it as the orthography2ipa
``normalizer``, so the spelled-out words then flow through the eu lattice's
allophony, sandhi and stress like any other word.

The Basque cardinal system is **vigesimal** (base-20): the tens are built on
``hogei`` (20), ``berrogei`` (40 = 2×20), ``hirurogei`` (60 = 3×20) and
``laurogei`` (80 = 4×20), and 30/50/70/90 are the preceding twenty *plus ten*
(``hogeita hamar`` = 20-and-10 = 30). Groups are joined by the copulative
**eta** ("and"), which contracts to **-ta** on the twenties
(``hogei`` + ``eta`` → ``hogeita``): ``hogeita hamaika`` = 20-and-11 = 31.

Unlike tugaphone this module does **not** delegate to ``unicode_rbnf`` — the
attested/derived provenance of every base word matters here (and the vigesimal
composition and *eta*-placement are stated as source rules), so the number
words are a native, source-cited table plus a small recursive composer, exactly
as in :mod:`mwl_phonemizer.number_utils`.

Sources
-------
* **Euskaltzaindia** (Academy of the Basque Language), **Araua 7**, *"Zenbakien
  idazkeraz"* (Bilbao, 1994-10-28) — the normative arau that fixes the whole
  cardinal table 0–10⁹ verbatim, the spacing of ``hogeita hamar`` (never solid
  ``*hogeitamar``), the ``eta`` linking/dropping rule, and the ``bost``/``bortz``
  variant policy. (``papers/iberian/euskaltzaindia_araua07_zenbakien_idazkera.pdf``)
* **Euskaltzaindia**, **Araua 18**, *"Ordinalen eta banatzaileen idazkera"*
  (Oiartzun, 1994-12-29) — the ``-garren`` ordinal suffix, the digit-plus-period
  convention (``20.`` = ``hogeigarren``), ``bosgarren`` (not ``*bostgarren``),
  and the year-as-cardinal / century-as-ordinal reading rule.
  (``papers/iberian/euskaltzaindia_araua18_ordinalak.pdf``)
* **Hualde & Ortiz de Urbina (2003)**, *A Grammar of Basque* (Mouton de
  Gruyter), the numerals section — corroborating reference grammar.

Dialect note (Araua 7, point 3)
-------------------------------
The common belief that Souletin (Zuberera) is *the* ``bortz`` dialect is
**contradicted** by Araua 7, which states verbatim that ``bortz`` is used *in
some northern (Iparralde) dialects*, but that **most of Low Navarre and Zuberoa
say ``bost``**. euskaphone therefore keeps Batua ``bost`` for every coded lect
by default, and offers the ``bortz`` series (``hamabortz``, ``bortzehun``) only
for Lapurdian — the clearest "northern variety" case — rather than silently
substituting it for a dialect the Academy explicitly records as ``bost``. The
Souletin ``bederatzü`` and the citation stems ``hirur``/``laur`` are *not* in
the arau (they are phonological/compound reflexes) and are not used as base
forms here. This is the "null beats wrong" rule: an unattested dialect swap is
worse than the attested standard form.

Attestation
-----------
Every base word is tagged :data:`ATTESTED` or :data:`DERIVED`:

* **Attested** forms are the cardinals/ordinals spelled verbatim in Araua 7/18.
* **Derived** forms are the ones the arau states as a *rule* rather than spell
  out — the compound strings the vigesimal + ``eta`` rule composes
  (``hogeita hamasei``) and a couple of reading-convention words (``minus``,
  ``bilioi``) — and are marked so a reviewer can tell a citation from a
  reconstruction.
"""
from typing import Dict, List, Optional, Tuple

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

#: Copulative conjunction ("and") joining numeral groups. Full form between
#: larger groups (``ehun eta bat``); contracts to ``-ta`` on the twenties.
_AND = "eta"

#: Decimal separator word ("koma"). ATTESTED (loan, standard reading).
_DECIMAL_WORD = "koma"

#: Word for a negative sign ("minus"). DERIVED (reading convention).
_MINUS_WORD = "minus"

#: Ordinal suffix. ATTESTED (Euskaltzaindia; Hualde & Ortiz de Urbina 2003).
_ORDINAL_SUFFIX = "garren"

# ---------------------------------------------------------------------------
# Base numeral tables. Standard Batua is the default; per-dialect overrides
# layer on top (see _DIALECT_OVERRIDES).
# ---------------------------------------------------------------------------

#: units 0-10. ATTESTED (standard Batua). 0 is a modern loan.
_UNITS: Dict[int, str] = {
    0: "zero",        # ATTESTED (loan; also "huts")
    1: "bat",         # ATTESTED
    2: "bi",          # ATTESTED
    3: "hiru",        # ATTESTED
    4: "lau",         # ATTESTED
    5: "bost",        # ATTESTED
    6: "sei",         # ATTESTED
    7: "zazpi",       # ATTESTED
    8: "zortzi",      # ATTESTED
    9: "bederatzi",   # ATTESTED
    10: "hamar",      # ATTESTED
}

#: 11-19. Built on the ``hama(r)-`` "ten-" prefix; 11/18/19 are irregular
#: (``hamaika``, ``hemezortzi``, ``hemeretzi``). All ATTESTED.
_TEENS: Dict[int, str] = {
    11: "hamaika",      # ATTESTED (irregular, not *hamabat)
    12: "hamabi",       # ATTESTED
    13: "hamahiru",     # ATTESTED
    14: "hamalau",      # ATTESTED
    15: "hamabost",     # ATTESTED
    16: "hamasei",      # ATTESTED
    17: "hamazazpi",    # ATTESTED
    18: "hemezortzi",   # ATTESTED (irregular hama- → heme-)
    19: "hemeretzi",    # ATTESTED (irregular)
}

#: The vigesimal "twenty" heads. 20/40/60/80 are the base-20 multiples;
#: 30/50/70/90 are composed as ``<twenty> + eta + hamar`` by the composer.
#: All ATTESTED (Hualde & Ortiz de Urbina 2003, numerals section).
_TWENTIES: Dict[int, str] = {
    1: "hogei",         # 20   ATTESTED
    2: "berrogei",      # 40   ATTESTED (2×20)
    3: "hirurogei",     # 60   ATTESTED (3×20)
    4: "laurogei",      # 80   ATTESTED (4×20)
}

#: hundreds. 100 is ``ehun``; 200-900 use special combining stems
#: (``berr-``, ``hirur-``, ``laur-``) + ``-ehun``. ATTESTED.
_HUNDRED_ONE = "ehun"        # 100  ATTESTED (standalone and compound head)
_HUNDREDS: Dict[int, str] = {
    2: "berrehun",          # 200  ATTESTED (bi → berr-)
    3: "hirurehun",         # 300  ATTESTED (hiru → hirur-)
    4: "laurehun",          # 400  ATTESTED (lau → laur-)
    5: "bostehun",          # 500  ATTESTED
    6: "seiehun",           # 600  ATTESTED
    7: "zazpiehun",         # 700  ATTESTED
    8: "zortziehun",        # 800  ATTESTED
    9: "bederatziehun",     # 900  ATTESTED
}

#: scale words. ``mila`` ATTESTED; ``milioi`` ATTESTED (loan, standardized).
#: ``bilioi`` DERIVED (regular ``-lioi`` reflex).
_THOUSAND = "mila"          # ATTESTED
_MILLION = "milioi"         # ATTESTED
_BILLION = "bilioi"         # DERIVED

#: ordinals 1-10. The suffix is ``-garren``; 1st is suppletive
#: (``lehen``/``lehenengo``). ``bosgarren`` drops the ``t`` of ``bost``.
#: 1-10 ATTESTED (Euskaltzaindia; Hualde & Ortiz de Urbina 2003).
_ORDINALS: Dict[int, str] = {
    1: "lehenengo",        # ATTESTED (also "lehen")
    2: "bigarren",         # ATTESTED
    3: "hirugarren",       # ATTESTED
    4: "laugarren",        # ATTESTED
    5: "bosgarren",        # ATTESTED (bost → bos-)
    6: "seigarren",        # ATTESTED
    7: "zazpigarren",      # ATTESTED
    8: "zortzigarren",     # ATTESTED
    9: "bederatzigarren",  # ATTESTED
    10: "hamargarren",     # ATTESTED
}

#: Base entries attested verbatim in the reference grammar / Academy norm.
ATTESTED = {
    "zero", "bat", "bi", "hiru", "lau", "bost", "sei", "zazpi", "zortzi",
    "bederatzi", "hamar",
    "hamaika", "hamabi", "hamahiru", "hamalau", "hamabost", "hamasei",
    "hamazazpi", "hemezortzi", "hemeretzi",
    "hogei", "berrogei", "hirurogei", "laurogei",
    "ehun", "berrehun", "hirurehun", "laurehun", "bostehun", "seiehun",
    "zazpiehun", "zortziehun", "bederatziehun",
    "mila", "milioi",
    "lehen", "lehenengo", "bigarren", "hirugarren", "laugarren", "bosgarren",
    "seigarren", "zazpigarren", "zortzigarren", "bederatzigarren", "hamargarren",
    "koma",
    # the "bortz" series (Araua 7 point 3: attested in some Iparralde dialects)
    "bortz", "hamabortz", "bortzehun", "borzgarren",
}
DERIVED = {
    "bilioi",
    "minus",
    # every *composed* compound string (hogeita hamasei, mila bederatziehun …)
    # is produced by the attested vigesimal + eta rule, not spelled in a source.
}

#: Per-dialect overrides applied on top of the Batua tables. Araua 7 (point 3)
#: attests ``bortz`` for 5 only in *some* Iparralde varieties, and explicitly
#: records ``bost`` for Zuberoa and most of Low Navarre — so the ``bortz``
#: series is offered for Lapurdian alone, and every other lect keeps the Batua
#: forms. Each override table mirrors mwl_phonemizer's units/teens/hundreds shape.
_DIALECT_OVERRIDES: Dict[str, Dict[str, Dict[int, str]]] = {
    "eu-x-lapurtera": {
        "units": {5: "bortz"},
        "teens": {15: "hamabortz"},
        "hundreds": {5: "bortzehun"},
    },
}


def _tables(dialect: str) -> Dict[str, Dict[int, str]]:
    """Numeral tables for *dialect* (Batua base + attested overrides)."""
    units = dict(_UNITS)
    teens = dict(_TEENS)
    hundreds = dict(_HUNDREDS)
    ov = _DIALECT_OVERRIDES.get(dialect, {})
    units.update(ov.get("units", {}))
    teens.update(ov.get("teens", {}))
    hundreds.update(ov.get("hundreds", {}))
    return {"units": units, "teens": teens, "hundreds": hundreds}


class BasqueNumberParser:
    """Spell an integer or numeric token into Basque words (vigesimal).

    The composer is recursive over scale groups (units < 100 via the base-20
    twenties, hundreds, thousands, millions) joined by the copulative
    :data:`_AND`, which contracts to ``-ta`` on the twenties. Only the units
    table varies by dialect (``bost``/``bortz`` …).
    """

    def __init__(self, dialect: str = "eu"):
        if dialect not in DIALECTS:
            raise ValueError(
                f"unknown dialect {dialect!r}; expected one of {DIALECTS}")
        self.dialect = dialect
        t = _tables(dialect)
        self.units = t["units"]
        self.teens = t["teens"]
        self.hundreds = t["hundreds"]

    # -- sub-100: the vigesimal core ------------------------------------
    def _under_100(self, n: int) -> str:
        if n < 11:
            return self.units[n]
        if n < 20:
            return self.teens[n]
        twenties, rem = divmod(n, 20)
        head = _TWENTIES[twenties]
        if rem == 0:
            return head
        # eta contracts to -ta directly on the twenty head (hogei+eta →
        # hogeita), but the "ten" component always stays a separate word
        # (Araua 7: hogeita hamar, never *hogeitamar).
        return f"{head}ta {self._under_100_rem(rem)}"

    def _under_100_rem(self, rem: int) -> str:
        """A 1-19 remainder after a twenty head (10 → ``hamar``)."""
        if rem < 11:
            return self.units[rem]
        return self.teens[rem]

    def _under_1000(self, n: int) -> str:
        if n < 100:
            return self._under_100(n)
        hundreds, rem = divmod(n, 100)
        head = _HUNDRED_ONE if hundreds == 1 else self.hundreds[hundreds]
        if rem == 0:
            return head
        return f"{head} {_AND} {self._under_100(rem)}"

    def _under_million(self, n: int) -> str:
        if n < 1000:
            return self._under_1000(n)
        thousands, rem = divmod(n, 1000)
        # 1000 is bare "mila", not "*bat mila"
        head = _THOUSAND if thousands == 1 \
            else f"{self._under_1000(thousands)} {_THOUSAND}"
        if rem == 0:
            return head
        return f"{head} {self._join_rem(rem)}"

    def _scale(self, n: int) -> str:
        if n < 1_000_000:
            return self._under_million(n)
        for divisor, word in ((1_000_000_000, _BILLION),
                              (1_000_000, _MILLION)):
            if n >= divisor:
                count, rem = divmod(n, divisor)
                # "a million" is "milioi bat"; N million is "<N> milioi"
                head = f"{word} {self.units[1]}" if count == 1 \
                    else f"{self._under_1000(count)} {word}"
                if rem == 0:
                    return head
                return f"{head} {self._join_rem(rem)}"
        return self._under_million(n)

    def _join_rem(self, rem: int) -> str:
        """Attach a remainder after ``mila``/``milioi`` with the ``eta`` rule.

        Araua 7 ("Oharrak"): ``eta`` links the last two chunks, but it *drops*
        when a lower remainder follows the hundreds — ``mila eta berrehun``
        (1200) vs ``mila berrehun eta bi`` (1202). So ``eta`` is inserted only
        when the remainder is itself a single terminal chunk (below 100, or a
        bare hundreds multiple); a remainder that already carries its own
        internal ``eta`` is simply juxtaposed
        (``mila bederatziehun eta hogeita hamasei``).
        """
        if rem < 100 or rem % 100 == 0:
            return f"{_AND} {self._scale(rem)}"
        return self._scale(rem)

    # -- public API ------------------------------------------------------
    def cardinal(self, n: int) -> str:
        """Spell integer *n* as a Basque cardinal."""
        if n < 0:
            return f"{_MINUS_WORD} {self.cardinal(-n)}"
        if n == 0:
            return self.units[0]
        return self._scale(n)

    def ordinal(self, n: int) -> str:
        """Spell integer *n* as a Basque ordinal (``-garren``).

        1-10 use the attested table (1st suppletive ``lehenengo``). Above ten,
        the ordinal attaches ``-garren`` to the cardinal's final element, with
        the euphonic ``bost`` → ``bos`` drop (``hamabost`` → ``hamabosgarren``).
        """
        if n in _ORDINALS:
            return _ORDINALS[n]
        card = self.cardinal(n)
        words = card.split()
        words[-1] = self._ordinalize(words[-1])
        return " ".join(words)

    @staticmethod
    def _ordinalize(word: str) -> str:
        if word.endswith("bost"):
            word = word[:-1]  # bost → bos (bosgarren)
        return f"{word}{_ORDINAL_SUFFIX}"

    def decimal(self, whole: int, frac: str) -> str:
        """Spell a decimal: whole part, ``koma``, then digit-by-digit frac."""
        digits = " ".join(self.units[int(d)] for d in frac)
        return f"{self.cardinal(whole)} {_DECIMAL_WORD} {digits}"

    def year(self, n: int) -> str:
        """Spell a year. Basque reads years as plain cardinals."""
        return self.cardinal(n)

    def clock(self, hour: int, minute: int) -> str:
        """Spell a ``HH:MM`` clock time as ``<hour> [eta <minute>]``.

        The hour is read as a cardinal and a non-zero minute is joined with
        ``eta`` (``hogei eta hamar`` = 20:10). Any case suffix the writer
        attached to the time (``20:00etan``) is appended by the caller to the
        result's last element.
        """
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
        for sep in (",", "."):
            if sep in t:
                whole_s, _, frac_s = t.partition(sep)
                if whole_s.isdigit() and frac_s.isdigit():
                    out = self.decimal(int(whole_s), frac_s)
                    return f"{_MINUS_WORD} {out}" if neg else out
        if not t.isdigit():
            return None
        n = int(t)
        val = self.ordinal(n) if as_ordinal else self.cardinal(n)
        return f"{_MINUS_WORD} {val}" if neg else val


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
    # trailing alphabetic case suffix
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
    numbers, ``HH:MM`` clock times, and case-suffixed numerals
    (``1936ko`` → ``… hamaseiko``); an explicit ``<digits>garren`` token is read
    as an ordinal. Non-numeric tokens are returned untouched.

    :param dialect: an eu spec code (see :data:`DIALECTS`).
    :param strict: when true, re-raise a token that fails to verbalize.
    """
    if dialect not in DIALECTS:
        dialect = "eu"
    parser = BasqueNumberParser(dialect)
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
