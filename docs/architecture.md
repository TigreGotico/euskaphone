# Architecture

euskaphone phonemizes by driving the shared **orthography2ipa** candidate
lattice and layering on only the concerns orthography2ipa leaves to the
caller.

```
text
  │
  ├─ orthographic normalization  euskaphone.normalize     (o2i `normalize` stage)
  │     abbreviations, Roman ordinals, units/currency/percent, numeric dates
  │
  ├─ number normalization        euskaphone.number_utils  (same stage)
  │     vigesimal cardinals/ordinals, case-suffix, clock time
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
The apical/laminal sibilants, affricates, Souletin aspiration, and `/y/` are
produced by the `eu-x-*` specs orthography2ipa ships.

**Sandhi preservation.** Contiguous Basque tokens are transcribed as one
phrase so cross-word sandhi is preserved. Only detected contact tokens are
transcribed in isolation and nativized.

**Negative-particle contraction.** The most audible Basque sandhi is the
categorical contraction of the negative particle *ez* /es̻/ with a following
auxiliary/verb onset, a connected-speech process every speaker applies. It
is carried by the shared `eu` lect spec's `sandhi_rules`, so euskaphone gets
it for free whenever a Basque run keeps *ez* and its verb in the same
phrase:

| written | rule | IPA | process |
|---------|------|-----|---------|
| ez dut     | ez + d → ezt | `es̻ tut`      | onset /d/ devoices to [t], sibilant kept |
| ez da      | ez + d → ezt | `es̻ ta`       | onset /d/ devoices to [t] |
| ez zen     | ez + z → etz | `e ts̻en`      | sibilants coalesce to the affricate [ts̻] |
| ez naiz    | ez + n → en  | `e nai̯s̻`      | sibilant deleted before a nasal |
| ez luke    | ez + l → el  | `e luke`       | sibilant deleted before a lateral |
| ez balitz  | ez + b → ezp | `es̻ palits̻`  | onset /b/ devoices to [p], sibilant kept |
| ez gara    | ez + g → ezk | `es̻ kaɾa`     | onset /ɡ/ devoices to [k], sibilant kept |

The rules are keyed to the negator alone (a lone *ez* word), so an
unrelated `z`-final word before a voiced onset (`naiz da` → `nai̯s̻ da`) stays
untouched. The contractions are pan-Basque and inherited by every `eu-x-*`
dialect spec. The *degree* varies, and where a dialect merges the laminal
sibilant to apical (the western/Biscayan `⟨z⟩` → [s̺] merger) the standard
laminal-keyed rule does not fire: `ez dut` surfaces there as `es̺ dut`, the
honest "null beats a wrong contraction" outcome rather than a forced
standard form. Grounding: Hualde & Ortiz de Urbina (2003), Hualde
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
| `euskaphone.normalize` | abbreviations, Roman ordinals, units, dates |
| `euskaphone.number_utils` | vigesimal verbalization + `normalize_numbers` |
| `euskaphone.codeswitch` | detection, contact transcription, nativization |
| `euskaphone.langdetect` | statistical per-word language detector (optional) |
| `euskaphone.lexicons` | bundled toponym seed + HiTZ overlay loaders |
| `euskaphone.pitch_accent` | Northern Bizkaian lexical-accent annotation |
| `euskaphone.accent` | accent forcing: IPA delta + gated respelling |
| `euskaphone.registry` | dialect codes, aliases, contact sides |
| `euskaphone.plugin` | OVOS `opm.g2p` plugin wrapper |

---
[← API](api.md) · [Home](../README.md) · [Benchmarks →](benchmarks.md)
