"""Dialect registry: resolve dialect names to orthography2ipa Basque lects.

A euskaphone dialect *is* an orthography2ipa Basque lect spec. The canonical
set is therefore the eight ``eu`` specs orthography2ipa ships
(:func:`orthography2ipa.available_codes`), reachable by their BCP-47 codes:

    ``eu``                    Standard Batua (default)
    ``eu-x-bizkaiera``        Biscayan   (Bizkaiera / Biscayan)
    ``eu-x-gipuzkera``        Gipuzkoan  (Gipuzkera / Guipuzcoan)
    ``eu-x-lapurtera``        Lapurdian  (Lapurtera / Labourdin)
    ``eu-x-nafarra-garaia``   High Navarrese  (Nafarrera / Alto Navarro)
    ``eu-x-nafarra-beherea``  Low Navarrese   (Behe-Nafarrera / Bajo Navarro)
    ``eu-x-zuberera``         Souletin   (Zuberera / Souletin / Xiberotarra)
    ``eu-x-erronkariera``     Roncalese  (Erronkariera / Roncalés, †)

Every dialect is also reachable by a human-readable alias, so a caller can say
``dialect="souletin"`` or ``dialect="biscayan"`` instead of the private-use
code. Resolution is case-insensitive and tolerant of trailing subtags
(``eu-x-unknown`` → ``eu``).

    >>> from euskaphone.registry import resolve_lect, list_dialects
    >>> resolve_lect("souletin")
    'eu-x-zuberera'
    >>> resolve_lect("batua")
    'eu'
    >>> resolve_lect("biscayan") in list_dialects()
    True
"""
from __future__ import annotations

import functools
import warnings
from typing import Dict, List

from linguatag import closest_lang, lang_matches, parse_tag, standardize_lang
from orthography2ipa import available_codes, resolve

from euskaphone.version import VERSION_MAJOR

#: The default dialect: Standard Basque (Euskara Batua).
DEFAULT_DIALECT = "eu"


def _canonical_codes() -> List[str]:
    return sorted(c for c in available_codes() if parse_tag(c).language == "eu")


_CANONICAL: List[str] = _canonical_codes()


#: Human-readable aliases → lect code, as this package documents the codes.
#: Basque endonyms and the common English/Spanish/French exonyms all resolve to
#: the same spec.
_NAMES: Dict[str, str] = {
    # Standard Basque
    "batua": "eu",
    "euskara-batua": "eu",
    "standard": "eu",
    # Biscayan
    "bizkaiera": "eu-x-bizkaiera",
    "biscayan": "eu-x-bizkaiera",
    "vizcaino": "eu-x-bizkaiera",
    "bizkaiera-western": "eu-x-bizkaiera",
    "western": "eu-x-bizkaiera",
    # Gipuzkoan
    "gipuzkera": "eu-x-gipuzkera",
    "guipuzcoan": "eu-x-gipuzkera",
    "gipuzkoan": "eu-x-gipuzkera",
    "central": "eu-x-gipuzkera",
    # Lapurdian
    "lapurtera": "eu-x-lapurtera",
    "labourdin": "eu-x-lapurtera",
    "labortano": "eu-x-lapurtera",
    "navarro-labourdin": "eu-x-lapurtera",
    # High Navarrese
    "nafarra-garaia": "eu-x-nafarra-garaia",
    "goi-nafarrera": "eu-x-nafarra-garaia",
    "high-navarrese": "eu-x-nafarra-garaia",
    "alto-navarro": "eu-x-nafarra-garaia",
    # Low Navarrese
    "nafarra-beherea": "eu-x-nafarra-beherea",
    "behe-nafarrera": "eu-x-nafarra-beherea",
    "low-navarrese": "eu-x-nafarra-beherea",
    "bajo-navarro": "eu-x-nafarra-beherea",
    # Souletin
    "zuberera": "eu-x-zuberera",
    "souletin": "eu-x-zuberera",
    "xiberotarra": "eu-x-zuberera",
    "suletino": "eu-x-zuberera",
    # Roncalese (extinct)
    "erronkariera": "eu-x-erronkariera",
    "roncalese": "eu-x-erronkariera",
    "roncales": "eu-x-erronkariera",
}

#: Each documented lect code → the key orthography2ipa registers its spec under.
#: orthography2ipa keeps the old key of a renamed spec as an exact alias, so
#: ``resolve`` maps a documented code to the spec's key in every release.
_CODES: Dict[str, str] = {code: resolve(code) for code in _NAMES.values()}

#: Human-readable aliases → the key orthography2ipa registers the spec under.
_ALIASES: Dict[str, str] = {name: _CODES[code] for name, code in _NAMES.items()}


#: Which geographic side of the Basque Country a dialect belongs to. Continental
#: (Iparralde, France) dialects default their code-switch contact language to
#: French; peninsular (Hegoalde, Spain) dialects default to Spanish. Standard
#: Batua is peninsular-leaning in practice, so it defaults to Spanish.
_CONTINENTAL = {
    _CODES["eu-x-lapurtera"],
    _CODES["eu-x-nafarra-beherea"],
    _CODES["eu-x-zuberera"],
}


def normalize_dialect_code(name: str) -> str:
    """Deprecated: lower-case and trim a dialect name or code.

    .. deprecated::
        :func:`resolve_lect` reads a name or tag in any spelling. Use
        :func:`linguatag.standardize_lang` for the canonical form of a tag.
    """
    warnings.warn(
        "normalize_dialect_code() is deprecated; use linguatag.standardize_lang(). "
        f"It will be removed in euskaphone {VERSION_MAJOR + 1}.0.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return (name or "").strip().lower()


@functools.lru_cache(maxsize=4096)
def resolve_lect(dialect: str = DEFAULT_DIALECT) -> str:
    """Resolve ``dialect`` (a code or a human-readable alias) to an eu lect code.

    Resolution order: a code this package documents, then an alias, each
    matched with trailing subtags removed one at a time, down to but not
    including ``eu`` (``eu-x-bizkaiera-foo`` → ``eu-x-bizkaiera``). A key
    orthography2ipa lists matches the same way. Then the nearest canonical lect
    (``eu-x-unknown`` → ``eu``). An unresolved name falls back to ``eu``
    (Standard Batua).
    """
    tag = standardize_lang((dialect or "").strip())
    key = tag
    while key and key != DEFAULT_DIALECT:
        if lect := _CODES.get(key) or _ALIASES.get(key):
            return lect
        if key in _CANONICAL:
            return key
        key = key.rpartition("-")[0]
    return closest_lang(tag, _CANONICAL, lects="standard") or DEFAULT_DIALECT


def is_supported(dialect: str) -> bool:
    """Whether ``dialect`` names a Basque lect (not just the Batua fallback).

    ``resolve_lect`` always falls back to ``eu``, so it cannot answer this; a
    name is "supported" only if it is Basque or a known human-readable alias.
    """
    tag = standardize_lang((dialect or "").strip())
    return tag in _ALIASES or lang_matches(tag, "eu")


def list_dialects() -> List[str]:
    """Every canonical dialect code (the eight orthography2ipa Basque specs)."""
    return list(_CANONICAL)


def dialect_aliases() -> Dict[str, str]:
    """The human-readable alias → lect-code table (a copy)."""
    return dict(_ALIASES)


def is_continental(lect: str) -> bool:
    """Whether ``lect`` is an Iparralde (continental, France-side) dialect."""
    return resolve_lect(lect) in _CONTINENTAL


def default_contact(lect: str) -> str:
    """The default code-switch contact language for ``lect``.

    Continental dialects embed French; peninsular dialects embed Spanish.
    """
    return "fr" if is_continental(lect) else "es"
