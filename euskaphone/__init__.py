"""euskaphone — dialect-aware Basque phonemization on the orthography2ipa lattice.

The phonemizer drives the shared orthography2ipa candidate lattice: a dialect is
an orthography2ipa Basque lect spec, and the lattice — the spec's grapheme
table, ``allophones`` and cross-word sandhi — produces the dialect's phonology
directly. euskaphone contributes the stages orthography2ipa leaves to the
caller: vigesimal (base-20) number verbalization, Spanish/French code-switch
handling with nativization onto the Basque inventory, and a proper-name/loan
lexicon hook. Basque orthography is near-phonemic, so — by design — there is no
homograph subsystem. See :mod:`euskaphone.lattice_core`.
"""
from typing import Optional

from euskaphone.version import __version__
from euskaphone.lattice_core import phonemize as _phonemize, register_lexicon
from euskaphone.lexicons import (
    apply_builtins, register_hitz_overlay, register_toponyms,
)
from euskaphone.pitch_accent import (
    AccentClass, PitchAccentLexicon, annotate_sentence as _annotate_pitch,
    default_lexicon,
)
from euskaphone.registry import (
    DEFAULT_DIALECT, dialect_aliases, is_supported as _is_supported,
    list_dialects, resolve_lect,
)

#: The lects whose lexical pitch accent euskaphone can annotate. The shipped
#: cited lexicon documents the Northern Bizkaian sub-area of Biscayan.
_PITCH_ACCENT_LECTS = ("eu-x-bizkaiera",)


class EuskaPhonemizer:
    """Dialect-aware Basque phonemization on the orthography2ipa lattice.

    The eight Basque lects orthography2ipa ships are reachable by their BCP-47
    codes ("eu", "eu-x-bizkaiera", "eu-x-zuberera", …) or by a human-readable
    alias ("batua", "biscayan", "souletin"); the full list comes from
    :func:`euskaphone.list_dialects`.

    Built-in lexicons (:mod:`euskaphone.lexicons`) are wired at construction:
    the Euskaltzaindia toponym seed is registered by default (``toponyms=True``,
    opt-out) unless a caller already registered a lexicon for ``eu``; the HiTZ
    proper-noun overlay is opt-in (``lexicon="hitz"``) and carries a benchmark
    circularity caveat.
    """

    def __init__(self, toponyms: bool = True,
                 lexicon: Optional[str] = None) -> None:
        apply_builtins(toponyms=toponyms, lexicon=lexicon)

    def phonemize_sentence(self, sentence: str, dialect: str = DEFAULT_DIALECT,
                           contact: str = "auto",
                           pitch_accent: bool = False) -> str:
        """Phonemize ``sentence`` for the ``dialect`` lect.

        Parameters:
            sentence: Input text to phonemize.
            dialect: A lect code or human-readable alias (see
                :func:`euskaphone.list_dialects` /
                :func:`euskaphone.dialect_aliases`). Defaults to Standard Batua.
            contact: Embedded-language policy — ``"auto"`` (detect and classify
                each contact word per-word among es/fr/en, unclassified words
                falling to the dialect's side), ``"es"``, ``"fr"``, ``"en"`` or
                ``"none"`` (no code-switching).
            pitch_accent: When ``True``, annotate lexical Northern Bizkaian pitch
                accent (:mod:`euskaphone.pitch_accent`) — a mark on the accented
                syllable of each lexically accented word, nothing on unaccented
                or unknown words. Opt-in and only defined for Biscayan
                (``eu-x-bizkaiera`` / ``biscayan``); a ``ValueError`` is raised
                for any other lect. Annotation is word-level, so cross-word
                sandhi is not applied in this mode.

        Returns:
            Space-separated IPA for each word.
        """
        if pitch_accent:
            lect = resolve_lect(dialect)
            if lect not in _PITCH_ACCENT_LECTS:
                raise ValueError(
                    f"pitch_accent is only defined for Biscayan "
                    f"({', '.join(_PITCH_ACCENT_LECTS)}); got {dialect!r} "
                    f"({lect}). Coverage is scoped to the Northern Bizkaian "
                    f"sub-area Hualde documents.")
            return _annotate_pitch(
                sentence,
                lambda tok: _phonemize(tok, dialect, contact))
        return _phonemize(sentence, dialect, contact)

    @staticmethod
    def is_supported(dialect: str) -> bool:
        """Whether ``dialect`` names a known Basque lect."""
        return _is_supported(dialect)


__all__ = [
    "EuskaPhonemizer",
    "register_lexicon",
    "register_toponyms",
    "register_hitz_overlay",
    "list_dialects",
    "dialect_aliases",
    "resolve_lect",
    "AccentClass",
    "PitchAccentLexicon",
    "default_lexicon",
    "__version__",
]


if __name__ == "__main__":
    ph = EuskaPhonemizer()
    sentences = [
        "Gaur 1936ko gerra ikasi dugu.",
        "Hogeita hamaika katu zuri ikusi ditut.",
        "Bilbon 20:00etan hasiko da kontzertua.",
    ]
    for s in sentences:
        print(s)
        for code in ["eu", "eu-x-bizkaiera", "eu-x-zuberera"]:
            print(f"{code} → {ph.phonemize_sentence(s, code)}")
        print("######")
