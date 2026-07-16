"""Per-dialect regression check against the orthography2ipa eu gold.

The 160-row Basque gold (8 lects x 20 sentences) that orthography2ipa ships was
produced by the *same* lattice euskaphone drives, so a pure-lattice transcription
reproduces it exactly. This is therefore a **regression fixture, not an accuracy
measurement**: PER ~= 0 proves euskaphone has not perturbed the shared lattice,
nothing about how close the lattice is to human pronunciation. The honest
independent accuracy signal is the WikiPron benchmark in ``scripts/benchmark.py``.
"""
import csv
import glob
import os

import pytest

import orthography2ipa as o2i
from euskaphone import EuskaPhonemizer

_GOLD_DIR = os.path.join(
    os.path.dirname(o2i.__file__), "data", "gold", "spain_romance_tts")


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


_gold_files = sorted(glob.glob(os.path.join(_GOLD_DIR, "eu*.tsv")))


@pytest.mark.skipif(not _gold_files,
                    reason="orthography2ipa eu gold data not installed")
@pytest.mark.parametrize("path", _gold_files,
                         ids=[os.path.basename(p)[:-4] for p in _gold_files])
def test_dialect_gold_regression(path):
    code = os.path.basename(path)[:-4]
    ph = EuskaPhonemizer()
    rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    assert rows, f"empty gold: {path}"
    total = sum(
        _per(row["ipa"], ph.phonemize_sentence(row["sentence"], code,
                                               contact="none"))
        for row in rows
    )
    per = total / len(rows)
    # regression fixture: the pure lattice must reproduce the shared gold.
    assert per < 0.01, f"{code}: PER regressed to {per:.4f}"
