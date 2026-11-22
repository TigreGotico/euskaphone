# Architecture

<!-- agent-hint
covers: the stages of the pipeline, which module owns each and the sandhi that the lect spec supplies
source: euskaphone/lattice_core.py, euskaphone/normalize.py, euskaphone/codeswitch.py, orthography2ipa/data/eu.json
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/architecture.md && grep -oP '^\| \x60\Keuskaphone\.\w+(?=\x60)' docs/architecture.md | xargs -I{} .venv/bin/python -I -c 'import {}'
see: api.md, benchmarks.md
-->

euskaphone phonemizes by driving the shared **orthography2ipa** candidate
lattice and layering on only the concerns orthography2ipa leaves to the
caller.

```
text
  │
  ├─ orthographic normalization  euskaphone.normalize     (o2i `expand` stage)
  │     text2spoken: numbers, dates, clock times, money, measures,
  │     abbreviations, Roman numerals
  │     fallbacks: the forms text2spoken leaves as written
  │
  ├─ code-switch routing         euskaphone.codeswitch    (outside the engine)
  │     detect es/fr/en words → es-ES/fr-FR/en-US lattice → nativize to Basque
  │
  ├─ Basque runs → G2P(lect)     orthography2ipa lattice
  │     grapheme table + allophony + cross-word sandhi = the dialect's phonology
  │     (toponym lexicon on by default; caller lexicons via register_lexicon)
  │
  ├─ pitch-accent annotation     euskaphone.pitch_accent  (opt-in, Biscayan only)
  │
  └─ IPA
```

**A dialect is a lect spec.** There is no euskaphone-side accent transform.
The apical/laminal sibilants, affricates, Souletin aspiration, and `/y/`
come from the `eu-x-*` specs that orthography2ipa ships.

**Sandhi preservation.** Contiguous Basque tokens are transcribed as one
phrase so cross-word sandhi is preserved. Only detected contact tokens are
transcribed in isolation and nativized.

**Negative-particle contraction.** The most audible Basque sandhi is the
categorical contraction of the negative particle *ez* /es̻/ with a following
auxiliary/verb onset, a connected-speech process every speaker applies. It
lives in the `sandhi_rules` of the shared `eu` lect spec, so euskaphone gets
it for free whenever a Basque run keeps *ez* and its verb in the same
phrase:

| written | rule | process |
|---------|------|---------|
| ez dut     | ez + d → ezt | onset /d/ devoices to [t], sibilant kept |
| ez da      | ez + d → ezt | onset /d/ devoices to [t] |
| ez zen     | ez + z → etz | sibilants coalesce to the affricate [ts̻] |
| ez naiz    | ez + n → en  | sibilant deleted before a nasal |
| ez luke    | ez + l → el  | sibilant deleted before a lateral |
| ez balitz  | ez + b → ezp | onset /b/ devoices to [p], sibilant kept |
| ez gara    | ez + g → ezk | onset /ɡ/ devoices to [k], sibilant kept |

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
for text in ("ez dut", "ez da", "ez zen", "ez naiz", "ez luke", "ez balitz", "ez gara"):
    print(text, "->", ph.phonemize_sentence(text))
# ez dut -> ˈes̻ ˈtut
# ez da -> ˈes̻ ˈta
# ez zen -> ˈe ˈts̻en
# ez naiz -> ˈe ˈnai̯s̻
# ez luke -> ˈe luˈke
# ez balitz -> ˈes̻ paˈlits̻
# ez gara -> ˈes̻ kaˈɾa
```

The rules are keyed to the negator alone (a lone *ez* word), so an
unrelated `z`-final word before a voiced onset stays untouched:

```python
ph.phonemize_sentence("naiz da")
# 'ˈnai̯s̻ ˈda'
```

The contractions are pan-Basque and inherited by every `eu-x-*`
dialect spec. The *degree* varies. Where a dialect merges the laminal
sibilant to apical (the western/Biscayan `⟨z⟩` → [s̺] merger), the standard
laminal-keyed rule does not fire. The result is the honest "null beats a wrong
contraction" outcome, not a forced standard form:

```python
ph.phonemize_sentence("ez dut", "biscayan")
# 'es̺ dut'
```

Grounding: Hualde & Ortiz de Urbina (2003), Hualde
"Segmental phonology" section 2, and Hualde (1991), *Basque Phonology*.

**No homograph subsystem, by design.** Basque orthography is
near-phonemic, so grapheme readings are essentially fixed and
sense-independent. Where tugaphone needs `bifonia` for Portuguese
heterophones, euskaphone ships nothing. This is a scope decision, not an
omission.

## Module map

| module | role |
|--------|------|
| `euskaphone.lattice_core` | engine wiring, `phonemize`, `register_lexicon` |
| `euskaphone.normalize` | `normalize_text`: text2spoken, then the fallbacks |
| `euskaphone.number_utils` | `BasqueNumberParser` and the number fallbacks |
| `euskaphone.codeswitch` | detection, contact transcription, nativization |
| `euskaphone.langdetect` | statistical per-word language detector (optional) |
| `euskaphone.lexicons` | bundled toponym seed + HiTZ overlay loaders |
| `euskaphone.pitch_accent` | Northern Bizkaian lexical-accent annotation |
| `euskaphone.accent` | accent forcing: IPA delta + gated respelling |
| `euskaphone.registry` | dialect codes, aliases, contact sides |
| `euskaphone.units` | unit and currency fallbacks, with `euskaphone/data/units.tsv` |
| `euskaphone.romans` | Roman numeral fallback and monarch ordinals |
| `euskaphone.abbreviations` | abbreviation fallbacks, with `euskaphone/data/abbreviations.tsv` |
| `euskaphone.dates` | deprecated date stage |
| `euskaphone.numverbal` | spelled-number helpers and deprecated stages |
| `euskaphone.plugin` | G2P wrapper with the orthography2ipa plugin shape |

---
[← API](api.md) · [Index](index.md) · [Benchmarks →](benchmarks.md)
