"""Per-dialect accent-forcing respell gain table over the eu gold sentences.

Runs the verification-gated respeller (:mod:`euskaphone.accent`) on the 20
Batua gold sentences for every target lect and reports, honestly, how much
closer a *Batua* reading of the respelled orthography gets to the target lect's
own transcription. Peninsular seseo is recoverable through Batua orthography;
continental aspiration and Souletin front rounding are not, and the table shows
that ceiling rather than hiding it.

    python scripts/respell_gains.py
"""
from __future__ import annotations

import csv
import os

import orthography2ipa as o2i
from euskaphone.accent import respell_report
from euskaphone.registry import list_dialects

_GOLD = os.path.join(
    os.path.dirname(o2i.__file__), "data", "gold", "spain_romance_tts", "eu.tsv")


def _sentences():
    with open(_GOLD, encoding="utf-8") as fh:
        return [row["sentence"] for row in csv.DictReader(fh, delimiter="\t")]


def main() -> None:
    sentences = _sentences()
    n = len(sentences)
    print(f"Accent-forcing respell gains over {n} Batua gold sentences")
    print(f"(PER of a Batua reading vs the target lect's own IPA; lower better)\n")
    header = f"{'dialect':<24} {'before':>8} {'after':>8} {'gain':>8}  rules"
    print(header)
    print("-" * len(header))
    for lect in list_dialects():
        if lect == "eu":
            continue
        before = after = 0.0
        rules: set[str] = set()
        for s in sentences:
            r = respell_report(s, lect)
            before += r.per_before
            after += r.per_after
            rules |= set(r.accepted)
        gain = (before - after) / n
        print(f"{lect:<24} {before/n:>8.4f} {after/n:>8.4f} {gain:>8.4f}  "
              f"{', '.join(sorted(rules)) or '-'}")


if __name__ == "__main__":
    main()
