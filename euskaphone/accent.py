"""Accent forcing: re-transcribe or *respell* Batua text toward a target lect.

Two modes, one entry point :func:`force_accent`:

* ``mode="ipa"`` — the direct view. The text is transcribed straight through the
  target lect's lattice, so the return is the target dialect's own IPA (the
  "IPA delta" against Batua).

* ``mode="respell"`` — the verification-gated respeller, ported from tugaphone's
  accent-forcing architecture. It rewrites the *Batua orthography* using Basque
  spelling conventions that push a **Batua** reader toward the target
  pronunciation (``z``→``s`` for the peninsular seseo merger, ``il``→``ill`` for
  palatalisation, ``h``-insertion for continental aspiration, …). Every edit is
  **verification-gated**: an edit is kept only if re-transcribing the respelled
  text *through the base (Batua) lattice* moves the result measurably closer to
  the target lect's IPA. An edit the base lattice cannot cash out — Batua has a
  silent ``h`` and no ``ü``, so continental aspiration and Souletin front
  rounding are simply not recoverable through it — is rejected, and the honest
  consequence is a near-zero respell gain for exactly those features.

The gate is what keeps respell honest: it never invents an orthography whose
Batua reading does not actually approximate the target. :func:`respell_report`
exposes the per-edit accounting so a benchmark can publish the real ceiling.
"""
from __future__ import annotations

import re
from typing import Callable, List, NamedTuple, Optional

from euskaphone.lattice_core import engine
from euskaphone.registry import resolve_lect

#: The base reading lect: respelled orthography is scored by *this* lattice.
BASE_LECT = "eu"


def _transcribe(text: str, lect: str) -> str:
    """Pure-lattice transcription (no code-switch, no number stage)."""
    return engine(lect).transcribe(text)


def _levenshtein(a: str, b: str) -> int:
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return d[len(b)]


def _per(ref: str, hyp: str) -> float:
    r, h = ref.replace(" ", ""), hyp.replace(" ", "")
    return _levenshtein(r, h) / max(1, len(r))


class RespellRule(NamedTuple):
    """One candidate orthographic edit, tried against the verification gate."""

    name: str
    #: What phonological delta the edit chases (documentation only).
    rationale: str
    #: Rewrites Batua orthography toward the target spelling convention.
    apply: Callable[[str], str]


def _sub(pattern: str, repl: str) -> Callable[[str], str]:
    rx = re.compile(pattern)
    return lambda s: rx.sub(repl, s)


#: The respell rule set. Each rule is a *proposal*; the verification gate decides
#: per text and per target whether it survives. Rules whose delta the Batua
#: lattice cannot represent (``h``-insertion, front rounding) are proposed too —
#: they are simply gated out, which is how the honest ceiling is measured.
RESPELL_RULES: List[RespellRule] = [
    RespellRule(
        "seseo_z_to_s",
        "peninsular seseo: laminal /s̻/ (⟨z⟩) merges into apical /s̺/ (⟨s⟩)",
        _sub(r"z", "s"),
    ),
    RespellRule(
        "palatal_il",
        "expressive/contextual palatalisation ⟨il⟩ → /ʎ/ (spelled ⟨ill⟩)",
        _sub(r"il", "ill"),
    ),
    RespellRule(
        "palatal_in",
        "expressive/contextual palatalisation ⟨in⟩ → /ɲ/ (spelled ⟨iñ⟩)",
        _sub(r"in", "iñ"),
    ),
    RespellRule(
        "aspiration_h",
        "continental aspiration: prothetic ⟨h⟩ on vowel-initial words",
        _sub(r"(?<![^\W\d_])(?=[aeiouAEIOU])", "h"),
    ),
    RespellRule(
        "front_rounding_u_ue",
        "Souletin front rounding: ⟨u⟩ → ⟨ü⟩ [y]",
        _sub(r"u", "ü"),
    ),
]


class RespellResult(NamedTuple):
    """The outcome of a respell pass over one text against one target."""

    source: str
    respelled: str
    target_ipa: str
    base_ipa: str
    respelled_ipa: str
    #: PER of the base reading before respelling; the starting distance.
    per_before: float
    #: PER after keeping every surviving edit; ``per_before - per_after`` is gain.
    per_after: float
    #: Names of the rules the verification gate accepted, in order.
    accepted: List[str]

    @property
    def gain(self) -> float:
        """PER reduction the respelling bought (>= 0)."""
        return self.per_before - self.per_after


def respell_report(text: str, dialect: str,
                   rules: Optional[List[RespellRule]] = None,
                   eps: float = 1e-9) -> RespellResult:
    """Greedy, verification-gated respell of ``text`` toward ``dialect``.

    For each rule in turn, the candidate respelling is scored by transcribing it
    through the **base** (Batua) lattice and measuring PER against the target
    lect's own transcription of the original text. The edit is kept only if it
    strictly lowers that PER; otherwise it is discarded. The result carries the
    full accounting for benchmarking.
    """
    rules = RESPELL_RULES if rules is None else rules
    target = resolve_lect(dialect)
    target_ipa = _transcribe(text, target)
    base_ipa = _transcribe(text, BASE_LECT)

    current = text
    current_per = _per(target_ipa, base_ipa)
    per_before = current_per
    accepted: List[str] = []

    for rule in rules:
        candidate = rule.apply(current)
        if candidate == current:
            continue
        cand_ipa = _transcribe(candidate, BASE_LECT)
        cand_per = _per(target_ipa, cand_ipa)
        if cand_per < current_per - eps:
            current, current_per = candidate, cand_per
            accepted.append(rule.name)

    return RespellResult(
        source=text,
        respelled=current,
        target_ipa=target_ipa,
        base_ipa=base_ipa,
        respelled_ipa=_transcribe(current, BASE_LECT),
        per_before=per_before,
        per_after=current_per,
        accepted=accepted,
    )


def force_accent(text: str, dialect: str, mode: str = "ipa") -> str:
    """Force ``text`` toward ``dialect``.

    ``mode="ipa"`` returns the target lect's IPA directly. ``mode="respell"``
    returns Batua orthography rewritten (verification-gated) so a Batua reader
    approximates the target pronunciation.
    """
    if mode == "ipa":
        return _transcribe(text, resolve_lect(dialect))
    if mode == "respell":
        return respell_report(text, dialect).respelled
    raise ValueError(f"unknown mode {mode!r}; expected 'ipa' or 'respell'")
