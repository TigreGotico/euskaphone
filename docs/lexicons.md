# Lexicons

A euskaphone lexicon is a word-keyed `word<TAB>ipa` table registered through
the orthography2ipa lexicon contract (one sidecar source per language
code). A covered word folds into the same override pathway as a spec
exception, so stress, cross-word sandhi, and `confidence == 1.0` still
apply, and lattice generation runs only for uncovered words. Two lexicons
ship with euskaphone. Both are validated
(`orthography2ipa.lexicon.validate_lexicon_text`) at build time by
`scripts/build_lexicons.py`.

## Registering your own

```python
from euskaphone import register_lexicon
register_lexicon("eu", "/path/to/lexicon.tsv")          # local file
register_lexicon("eu", "hf://ORG/repo/eu.tsv")          # Hugging Face
```

A caller-registered lexicon always **wins** over the built-in toponym seed:
the built-in only registers when no lexicon is already registered for the
code.

## Toponym seed (`eu_toponyms.tsv`), opt-out, on by default

A curated seed of about 130 of the most important Basque toponyms and
respelled exonyms in their **Euskaltzaindia normative** forms. It registers
for the standard `eu` code automatically when you construct the phonemizer:

```python
EuskaPhonemizer()                 # toponym seed registered (default)
EuskaPhonemizer(toponyms=False)   # opt out
```

For a regular normative spelling the IPA pins the Batua lattice reading of
that spelling (the entry documents and freezes the normative
pronunciation). For a foreign-spelled entry (`hollywood`, `washington`,
`zürich`) the IPA is the Basque-adapted pronunciation, which the raw
lattice would not produce.

**Source and licensing.** The normative forms come from the Academy's
onomastics database, EODA (*Euskaltzaindiaren Onomastikaren Datu-Basea*,
[euskaltzaindia.eus/eoda](https://www.euskaltzaindia.eus/eoda)), and the
Academy's exonym recommendations. EODA is a query-only public web service
with **no bulk-download endpoint and no explicit open-data licence**, so
nothing is scraped. Only the normative spellings, the Academy's official,
non-copyrightable facts about place names, each recoverable from the EODA
search UI, are transcribed here. No EODA content is redistributed.

## HiTZ overlay (`eu_hitz_overlay.tsv`), opt-in, benchmark-coupled

An overlay of about 40 proper nouns (place and person names) drawn from the
HiTZ/EHU `wikipedia_basque_ipa` set.

```python
EuskaPhonemizer(lexicon="hitz")   # opt in; overrides the code's lexicon
```

**Circularity caveat.** That HiTZ set is also euskaphone's independent
cross-engine benchmark ([`benchmarks.md`](benchmarks.md) section 3). Folding
any of it into a lexicon is circular: the model would then be graded
against data it memorized. The overlay is therefore **opt-in only**, and
the benchmark harness excludes every reference row containing an overlay
key when the overlay is active:

```bash
python scripts/benchmark.py --hitz-overlay   # activates overlay + benchmark split
```

The harness reports how many rows the circularity guard dropped
(`euskaphone.lexicons.hitz_overlay_words` is the exclusion set). Enabling
the overlay trades a small proper-noun accuracy gain for the loss of those
rows as an independent signal.

## Regenerating

```bash
python scripts/build_lexicons.py          # toponym seed only (offline)
python scripts/build_lexicons.py --hitz   # also the HiTZ overlay (network)
```

---
[← Code-switch](codeswitch.md) · [Home](../README.md) · [Pitch accent →](pitch_accent.md)
