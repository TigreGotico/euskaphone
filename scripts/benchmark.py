"""Measure euskaphone against two golds, honestly labelled.

1. **orthography2ipa eu gold** (160 rows, 8 lects x 20) — a *regression* fixture.
   euskaphone drives the same lattice that produced it, so PER ~= 0 proves only
   that the shared lattice is untouched, not that it matches human speech.

2. **WikiPron** ``eus_latn`` (broad) — an *independent* Wiktionary-derived
   pronunciation gold. This is the honest accuracy signal: a real per / word
   accuracy for the pure lattice with no lexicon. WikiPron is dominated by
   proper names and loans and lists multiple valid pronunciations per entry, so
   word accuracy is a floor, not a ceiling — it is what the lexicon hook exists
   to raise.

Run: ``python scripts/benchmark.py [--wikipron PATH] [--sample N]``. The WikiPron
TSV is not vendored; point ``--wikipron`` at a ``word<TAB>space-phones`` file
(e.g. orthography2ipa's ``.benchmark_cache/eus_latn_broad.tsv``).
"""
import argparse
import csv
import glob
import os
import random

import orthography2ipa as o2i
from euskaphone import EuskaPhonemizer


def levenshtein(a: str, b: str) -> int:
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return d[len(b)]


def per(ref: str, hyp: str) -> float:
    r, h = ref.replace(" ", ""), hyp.replace(" ", "")
    return levenshtein(r, h) / max(1, len(r))


def run_regression(ph: EuskaPhonemizer) -> None:
    gold_dir = os.path.join(
        os.path.dirname(o2i.__file__), "data", "gold", "spain_romance_tts")
    files = sorted(glob.glob(os.path.join(gold_dir, "eu*.tsv")))
    if not files:
        print("orthography2ipa eu gold not found; skipping regression.")
        return
    print("== orthography2ipa eu gold (REGRESSION fixture, not accuracy) ==")
    for path in files:
        code = os.path.basename(path)[:-4]
        rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
        total = sum(per(r["ipa"],
                        ph.phonemize_sentence(r["sentence"], code,
                                              contact="none")) for r in rows)
        print(f"  {code:24s} n={len(rows):2d}  PER={total / len(rows):.4f}")


def run_wikipron(ph: EuskaPhonemizer, path: str, sample: int) -> None:
    rows = [r for r in csv.reader(open(path, encoding="utf-8"), delimiter="\t")
            if len(r) == 2]
    random.seed(0)
    random.shuffle(rows)
    rows = rows[:sample] if sample else rows
    err = tot = exact = 0
    for word, ipa in rows:
        ref = ipa.replace(" ", "")
        hyp = ph.phonemize_sentence(word, "eu", contact="none").replace(" ", "")
        err += levenshtein(ref, hyp)
        tot += len(ref)
        exact += ref == hyp
    print("== WikiPron eus_latn broad (INDEPENDENT accuracy, pure lattice) ==")
    print(f"  n={len(rows)}  PER={err / tot:.4f}  word_acc={exact / len(rows):.4f}")
    print("  (proper-name/loan-heavy; multiple valid variants per entry; "
          "no lexicon -> this is a floor the lexicon hook raises)")


def _fold(s: str) -> str:
    """Fold sibilant notation and strip stress so two G2P conventions compare.

    EHU/HiTZ writes the coronal sibilants as ``ʂ`` and marks stress with an
    apostrophe; orthography2ipa writes the apical/laminal contrast ``s̺``/``s̻``
    and no stress. Folding ``{s̺,s̻,ʂ}→s`` and ``{ts̺,ts̻,tʂ}→ts`` and dropping
    stress measures phonemic agreement, not notation.
    """
    import unicodedata
    for d in (" ", "ˈ", "ˌ", "'", "͡"):
        s = s.replace(d, "")
    s = s.replace("ts̺", "ts").replace("ts̻", "ts").replace("tʂ", "ts")
    s = s.replace("s̺", "s").replace("s̻", "s").replace("ʂ", "s")
    return unicodedata.normalize("NFC", s)


def run_hitz(ph: EuskaPhonemizer, sample: int) -> None:
    """Cross-engine agreement with the HiTZ/EHU (University of the Basque
    Country) Wikipedia G2P gold — an *independent* reference, not human gold.
    Divergence is notation-folded (see :func:`_fold`)."""
    try:
        from huggingface_hub import hf_hub_download
        import pyarrow.parquet as pq
        path = hf_hub_download("HiTZ/wikipedia_basque_ipa",
                               "data/train-00000-of-00002.parquet",
                               repo_type="dataset")
    except Exception as exc:  # network / optional deps
        print(f"HiTZ gold unavailable ({exc}); skipping cross-engine benchmark.")
        return
    import random
    rows = pq.read_table(path).slice(0, 60000).to_pylist()
    random.seed(0)
    random.shuffle(rows)
    rows = rows[:sample] if sample else rows
    err = tot = 0
    for r in rows:
        ref = _fold(r["phonemes"])
        hyp = _fold(ph.phonemize_sentence(r["text"], "eu", contact="none"))
        err += levenshtein(ref, hyp)
        tot += len(ref)
    print("== HiTZ/EHU wikipedia_basque_ipa (INDEPENDENT cross-engine G2P) ==")
    print(f"  n={len(rows)}  PER(folded)={err / tot:.4f}")
    print("  (two independent Basque G2P engines on raw Wikipedia; sibilant "
          "notation folded, stress stripped)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wikipron", default=os.path.join(
        os.path.dirname(o2i.__file__), "..",
        ".benchmark_cache", "eus_latn_broad.tsv"))
    ap.add_argument("--sample", type=int, default=3000,
                    help="words/sentences to sample (0 = all)")
    ap.add_argument("--hitz", action="store_true",
                    help="also run the HiTZ/EHU cross-engine benchmark (network)")
    args = ap.parse_args()
    ph = EuskaPhonemizer()
    run_regression(ph)
    if os.path.exists(args.wikipron):
        run_wikipron(ph, args.wikipron, args.sample)
    else:
        print(f"WikiPron gold not found at {args.wikipron}; "
              "pass --wikipron PATH for the accuracy benchmark.")
    if args.hitz:
        run_hitz(ph, args.sample)


if __name__ == "__main__":
    main()
