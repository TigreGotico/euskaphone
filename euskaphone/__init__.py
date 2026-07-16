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
from euskaphone.registry import (
    DEFAULT_DIALECT, dialect_aliases, is_supported as _is_supported,
    list_dialects, resolve_lect,
)


class EuskaPhonemizer:
    """Dialect-aware Basque phonemization on the orthography2ipa lattice.

    The eight Basque lects orthography2ipa ships are reachable by their BCP-47
    codes ("eu", "eu-x-bizkaiera", "eu-x-zuberera", …) or by a human-readable
    alias ("batua", "biscayan", "souletin"); the full list comes from
    :func:`euskaphone.list_dialects`.
    """

    def phonemize_sentence(self, sentence: str, dialect: str = DEFAULT_DIALECT,
                           contact: str = "auto") -> str:
        """Phonemize ``sentence`` for the ``dialect`` lect.

        Parameters:
            sentence: Input text to phonemize.
            dialect: A lect code or human-readable alias (see
                :func:`euskaphone.list_dialects` /
                :func:`euskaphone.dialect_aliases`). Defaults to Standard Batua.
            contact: Embedded-language policy — ``"auto"`` (per-dialect side,
                peninsular→Spanish / continental→French), ``"es"``, ``"fr"`` or
                ``"none"`` (no code-switching).

        Returns:
            Space-separated IPA for each word.
        """
        return _phonemize(sentence, dialect, contact)

    @staticmethod
    def is_supported(dialect: str) -> bool:
        """Whether ``dialect`` names a known Basque lect."""
        return _is_supported(dialect)


__all__ = [
    "EuskaPhonemizer",
    "register_lexicon",
    "list_dialects",
    "dialect_aliases",
    "resolve_lect",
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
