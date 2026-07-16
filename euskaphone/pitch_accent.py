"""Northern Bizkaian lexical pitch-accent annotation.

The Northern Bizkaian (Western) prosodic system — the variety of Getxo–Gernika
and Lekeitio–Ondarroa–Markina described by Hualde (1997, 1999), Hualde,
Elordieta & Elordieta (1994, *The Basque Dialect of Lekeitio*) and Egurtzegi &
Elordieta (*A history of the Basque prosodic systems*) — draws a **lexical**
distinction that Standard Batua does not: a word is either

* **accented** — it contains an accented root or a pre-accenting affix, so one
  lexically fixed syllable carries a ``H*+L`` pitch accent (a fall from a high
  tone), or
* **unaccented** — it has no lexical accent and shows no word-level prominence;
  it acquires only a *derived* accent on its final syllable when it stands
  phrase-finally (immediately before the verb).

Most native stems and singular affixes are unaccented; accentedness is the
marked class, populated by old Latin/Romance loanwords (``ántzar`` < *ánser*
'goose', ``kipúla`` < *cepúlla* 'onion', ``ganbára`` < *cambra*), opaque and
transparent accented compounds (``bélarri`` 'ear', ``egúzki`` 'sun',
``burúgogor`` 'stubborn'), and words carrying pre-accenting suffixes (the plural
``-ak``/``-e-``, comparative ``-ago``, …).

This module is an **annotation layer, not a synthesis model.** It does not
predict F0; it marks, on the segmental IPA the lattice already produced, *which*
syllable is the lexically accented one, so a downstream prosody model or a human
annotator sees the ``H*+L`` target. The marking convention is deliberately
simple and explicit:

* an **accented** word gets a single accent mark (:data:`ACCENT_MARK`,
  U+02C8 ``ˈ``) placed immediately before its lexically accented syllable;
* an **unaccented** word is returned unchanged (no mark);
* an **unknown** word — one not attested in the lexicon — is *also* returned
  unchanged, but its class is :data:`AccentClass.UNKNOWN`, kept distinct from
  ``UNACCENTED`` so callers never mistake "not in the lexicon" for "known to
  bear no accent". Coverage is honest: only the attested, cited words are
  classified; everything else is unmarked-by-default and flagged unknown.

The lexicon is scoped to the Northern Bizkaian sub-area of Biscayan
(``eu-x-bizkaiera``) and is opt-in through the ``pitch_accent=True`` flag on
:meth:`euskaphone.EuskaPhonemizer.phonemize_sentence`. Every entry cites its
source.
"""
from __future__ import annotations

import csv
import enum
import functools
import os
import re
import unicodedata
from typing import Dict, List, NamedTuple, Optional

from orthography2ipa import syllabify

#: The IPA mark placed before the lexically accented syllable of an accented
#: word. U+02C8 (MODIFIER LETTER VERTICAL LINE, the IPA primary-stress mark) is
#: used as a language-neutral, renderable annotation of the ``H*+L`` lexical
#: pitch accent — it flags *the accented syllable*, not a claim about stress or
#: F0 shape. Unaccented and unknown words carry no mark.
ACCENT_MARK = "ˈ"

_DATA = os.path.join(os.path.dirname(__file__), "data", "pitch_accent")

#: The one Northern Bizkaian sub-area the shipped lexicon documents.
NORTHERN_BIZKAIAN = "northern_bizkaian"


class AccentClass(enum.Enum):
    """The lexical accent class of a word in the Northern Bizkaian system."""

    #: Lexically accented: one fixed syllable bears the ``H*+L`` pitch accent.
    ACCENTED = "accented"
    #: Lexically unaccented: no word-level accent (only a phrase-final derived one).
    UNACCENTED = "unaccented"
    #: Not attested in the lexicon — deliberately distinct from ``UNACCENTED``.
    UNKNOWN = "unknown"


class AccentEntry(NamedTuple):
    """A single cited lexicon entry."""

    word: str
    accent_class: AccentClass
    #: 1-based index of the accented syllable (``ACCENTED`` only; else ``None``).
    accent_syllable: Optional[int]
    gloss: str
    source: str


def _strip(word: str) -> str:
    """Lower-case, strip surrounding punctuation, drop diacritics for keying.

    Lexicon keys are bare Batua spellings; a caller's token may be capitalised
    or punctuated. Accent diacritics a user might have typed are folded away so
    ``Amúma,`` and ``amuma`` hit the same entry.
    """
    word = word.strip().lower()
    word = word.strip(".,;:!?¿¡\"'«»()[]…—–")
    nfd = unicodedata.normalize("NFD", word)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", stripped)


class PitchAccentLexicon:
    """A cited word → lexical-accent-class lexicon for one Bizkaian sub-area."""

    def __init__(self, entries: Dict[str, AccentEntry], area: str) -> None:
        self._entries = entries
        self.area = area

    @classmethod
    def from_tsv(cls, path: str, area: str) -> "PitchAccentLexicon":
        entries: Dict[str, AccentEntry] = {}
        with open(path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                cls_ = AccentClass(row["accent_class"].strip())
                syl = row["accent_syllable"].strip()
                entry = AccentEntry(
                    word=row["word"].strip(),
                    accent_class=cls_,
                    accent_syllable=int(syl) if syl else None,
                    gloss=row["gloss"].strip(),
                    source=row["source"].strip(),
                )
                entries[_strip(entry.word)] = entry
        return cls(entries, area)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, word: str) -> bool:
        return _strip(word) in self._entries

    def entries(self) -> List[AccentEntry]:
        """Every attested entry (a copy), sorted by word."""
        return sorted(self._entries.values(), key=lambda e: e.word)

    def lookup(self, word: str) -> AccentEntry:
        """The entry for ``word``; an ``UNKNOWN`` placeholder if unattested."""
        entry = self._entries.get(_strip(word))
        if entry is not None:
            return entry
        return AccentEntry(word, AccentClass.UNKNOWN, None, "", "")


@functools.lru_cache(maxsize=None)
def default_lexicon(area: str = NORTHERN_BIZKAIAN) -> PitchAccentLexicon:
    """The shipped, cited pitch-accent lexicon for ``area`` (cached)."""
    path = os.path.join(_DATA, f"{area}.tsv")
    if not os.path.exists(path):
        raise ValueError(f"unknown pitch-accent area {area!r}")
    return PitchAccentLexicon.from_tsv(path, area)


def mark_ipa(ipa_word: str, syllable: int) -> str:
    """Insert :data:`ACCENT_MARK` before the ``syllable``-th (1-based) syllable.

    The IPA word is syllabified by vowel groups (orthography2ipa's
    :func:`~orthography2ipa.syllabify`); since Basque is near-phonemic the IPA
    syllable count matches the orthographic one, so the lexicon's orthographic
    accent index lands on the right IPA syllable. An out-of-range index leaves
    the word unmarked rather than guessing.
    """
    if syllable < 1:
        return ipa_word
    syls = syllabify(ipa_word)
    if syllable > len(syls):
        return ipa_word
    head = "".join(syls[: syllable - 1])
    tail = "".join(syls[syllable - 1:])
    return head + ACCENT_MARK + tail


def annotate(word_orth: str, ipa_word: str,
             lexicon: Optional[PitchAccentLexicon] = None) -> str:
    """Return ``ipa_word`` with a pitch-accent mark iff ``word_orth`` is accented.

    Unaccented and unknown words are returned unchanged; only a lexically
    *accented* word (with a known accented syllable) receives the mark.
    """
    lex = lexicon or default_lexicon()
    entry = lex.lookup(word_orth)
    if entry.accent_class is AccentClass.ACCENTED and entry.accent_syllable:
        return mark_ipa(ipa_word, entry.accent_syllable)
    return ipa_word


_TOKEN = re.compile(r"\S+")


def annotate_sentence(sentence: str, transcribe_word, *,
                      lexicon: Optional[PitchAccentLexicon] = None) -> str:
    """Word-wise pitch-accent annotation of a whole sentence.

    ``transcribe_word`` is a callable turning one orthographic token into its
    IPA (euskaphone supplies the dialect lattice, code-switch and number stages
    per token). Each token is transcribed, then marked if the lexicon classes it
    accented. Annotation is word-level by design, so cross-word sandhi that the
    phrase transcription would apply is not modelled in this mode; that is the
    honest cost of surfacing the lexical accent per word.
    """
    lex = lexicon or default_lexicon()
    out: List[str] = []
    for m in _TOKEN.finditer(sentence):
        token = m.group(0)
        ipa = transcribe_word(token)
        if not ipa:
            continue
        out.append(annotate(token, ipa, lex))
    return " ".join(out)
