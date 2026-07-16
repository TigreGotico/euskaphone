# Benchmarks

Run: `python scripts/benchmark.py [--wikipron PATH] [--hitz] [--hitz-overlay] [--sample N]`.

The benchmarks run against the **pure lattice** — the built-in toponym lexicon is
turned off (`EuskaPhonemizer(toponyms=False)`) so every figure stays a
lattice-only floor, not a lexicon-inflated number.

euskaphone drives the shared orthography2ipa lattice, so every figure measures
that lattice — labelled honestly by what it can and cannot claim.

## 1. orthography2ipa eu gold — regression fixture (NOT accuracy)

The 160-row Basque gold (8 lects × 20 sentences) orthography2ipa ships was made
by the same lattice euskaphone drives, so a pure-lattice transcription
reproduces it exactly.

```
eu, eu-x-bizkaiera, … , eu-x-zuberera    PER = 0.0000  (all eight)
```

This proves euskaphone has not perturbed the shared lattice. It says nothing
about closeness to human speech — an engine-pinned gold is circular.

## 2. WikiPron `eus_latn` (broad) — independent word gold

Wiktionary-derived pronunciations, ~20k entries.

```
n = 20115 (full set)   PER = 0.0749   word accuracy = 0.4563
```

Honest floor for the pure lattice with no lexicon: WikiPron is proper-name- and
loan-heavy and lists multiple valid pronunciations per entry (only one is
matched). This is what the lexicon hook exists to raise.

## 3. HiTZ/EHU `wikipedia_basque_ipa` — independent cross-engine

The University of the Basque Country (HiTZ) Wikipedia G2P gold, 836k sentences.
The two engines use different conventions (HiTZ `ʂ` for the coronal sibilants,
apostrophe stress), so the comparison folds `{s̺,s̻,ʂ}→s`, `{ts̺,ts̻,tʂ}→ts` and
strips stress before scoring.

```
n = 3000 (seed-0 sample)   PER (folded) = 0.1384
```

Agreement between two independent Basque G2P engines on raw Wikipedia. Much of
the residual is genuine convention difference (spirantization, embedded-Spanish
handling), not error.

### The HiTZ overlay split (circularity guard)

The opt-in HiTZ proper-noun overlay lexicon (`docs/lexicons.md`) draws its keys
from *this* set, so grading it here would be circular. With `--hitz-overlay` the
harness activates the overlay **and** excludes every reference row whose text
contains an overlay key, then reports the drop:

```
== HiTZ/EHU wikipedia_basque_ipa (… OVERLAY ACTIVE — split) ==
  n = …   PER (folded) = …
  excluded N row(s) containing an overlay key (circularity guard)
```

Enabling the overlay therefore trades a small proper-noun gain for the loss of
those rows as an independent signal — documented, never silent.

## Comparable tools — measured

All three engines scored on the full WikiPron `eus_latn` broad set (20,115
words) under one protocol: Levenshtein over IPA segments (base + combining
marks as one unit), stress and boundary marks stripped, per-word PER averaged
over words. The `0.0749` above uses a different unit and average
(character-level distance, micro-averaged over total characters), which is why
the two euskaphone figures differ; within *this* table all engines are scored
identically.

```
euskaphone     PER = 0.1009   word accuracy = 0.4298
espeak-ng eu   PER = 0.1704   word accuracy = 0.1750
espyak eu      PER = 0.1704   word accuracy = 0.1750
ahotts-g2p     PER = 0.3360   word accuracy = 0.0003
```

- **[ahotts-g2p](https://github.com/TigreGotico/ahotts-g2p)** (from AhoTTS, the
  EHU TTS front end) — Standard Batua only. Its output keeps AhoTTS's own
  symbol conventions rather than WikiPron-style IPA, so a large share of its
  distance here is notation, not phonology; read its row as "convention
  mismatch dominates", not as a 3× error rate.
- **espeak-ng** `eu` — single-dialect, rule-thin; no laminal/apical sibilant
  contrast.
- **[espyak](https://github.com/TigreGotico/espyak)** — pure-Python port of
  espeak-ng's rule engine; scores identically to espeak-ng here (to four
  decimals on all 20,115 words), so its row doubles as a parity check of the
  port.

euskaphone's contribution is eight-lect coverage, sourced vigesimal numerals, and
code-switch nativization, over a lattice shared across the Iberian family.
