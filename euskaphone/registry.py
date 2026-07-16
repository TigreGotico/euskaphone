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
    >>> "eu-x-bizkaiera" in list_dialects()
    True
"""
from __future__ import annotations

from typing import Dict, List

from orthography2ipa import available_codes

#: Basque-family lect prefixes orthography2ipa ships.
_EU_PREFIXES = ("eu", "eu-")

#: The default dialect: Standard Basque (Euskara Batua).
DEFAULT_DIALECT = "eu"


def _canonical_codes() -> List[str]:
    return sorted(
        c for c in available_codes()
        if c == "eu" or c.startswith("eu-")
    )


_CANONICAL: List[str] = _canonical_codes()


#: Human-readable aliases → orthography2ipa lect code. Basque endonyms and the
#: common English/Spanish/French exonyms all resolve to the same spec.
_ALIASES: Dict[str, str] = {
    # Standard Basque
    "batua": "eu",
    "euskara-batua": "eu",
    "standard": "eu",
    "eu-es": "eu",
    "eu-fr": "eu",
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


#: Which geographic side of the Basque Country a dialect belongs to. Continental
#: (Iparralde, France) dialects default their code-switch contact language to
#: French; peninsular (Hegoalde, Spain) dialects default to Spanish. Standard
#: Batua is peninsular-leaning in practice, so it defaults to Spanish.
_CONTINENTAL = {
    "eu-x-lapurtera",
    "eu-x-nafarra-beherea",
    "eu-x-zuberera",
}


def normalize_dialect_code(name: str) -> str:
    """Lower-case and trim a dialect name/code for lookup."""
    return (name or "").strip().lower()


def resolve_lect(dialect: str = DEFAULT_DIALECT) -> str:
    """Resolve ``dialect`` (a code or a human-readable alias) to an eu lect code.

    Resolution order: exact canonical code (case-insensitive), then an alias,
    then a progressive pop of trailing subtags (``eu-x-zuberera-foo`` →
    ``eu-x-zuberera`` → ``eu``). An unresolved name falls back to ``eu``
    (Standard Batua).
    """
    key = normalize_dialect_code(dialect)
    while key:
        for code in _CANONICAL:
            if code.lower() == key:
                return code
        if key in _ALIASES:
            return _ALIASES[key]
        if "-" not in key:
            break
        key = key.rsplit("-", 1)[0]
    return DEFAULT_DIALECT


def is_supported(dialect: str) -> bool:
    """Whether ``dialect`` names a Basque lect (not just the Batua fallback).

    ``resolve_lect`` always falls back to ``eu``, so it cannot answer this; a
    name is "supported" only if its language subtag is ``eu`` or it is a known
    human-readable alias.
    """
    key = normalize_dialect_code(dialect)
    if not key:
        return False
    return key.split("-", 1)[0] == "eu" or key in _ALIASES


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
