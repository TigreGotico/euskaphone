# Architecture

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
| ez dut     | ez + d → ezt | `ˈes̻ ˈtut`    | onset /d/ devoices to [t], sibilant kept |
| ez da      | ez + d → ezt | `ˈes̻ ˈta`     | onset /d/ devoices to [t] |
| ez zen     | ez + z → etz | `ˈe ˈts̻en`    | sibilants coalesce to the affricate [ts̻] |
| ez naiz    | ez + n → en  | `ˈe ˈnai̯s̻`    | sibilant deleted before a nasal |
| ez luke    | ez + l → el  | `ˈe luˈke`     | sibilant deleted before a lateral |
| ez balitz  | ez + b → ezp | `ˈes̻ paˈlits̻` | onset /b/ devoices to [p], sibilant kept |
| ez gara    | ez + g → ezk | `ˈes̻ kaˈɾa`   | onset /ɡ/ devoices to [k], sibilant kept |

The rules are keyed to the negator alone (a lone *ez* word), so an
unrelated `z`-final word before a voiced onset (`naiz da` → `ˈnai̯s̻ ˈda`) stays
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
| `euskaphone.normalize` | `normalize_text`: text2spoken, then the fallbacks |
| `euskaphone.number_utils` | `BasqueNumberParser` and the number fallbacks |
| `euskaphone.codeswitch` | detection, contact transcription, nativization |
| `euskaphone.langdetect` | statistical per-word language detector (optional) |
| `euskaphone.lexicons` | bundled toponym seed + HiTZ overlay loaders |
| `euskaphone.pitch_accent` | Northern Bizkaian lexical-accent annotation |
| `euskaphone.accent` | accent forcing: IPA delta + gated respelling |
| `euskaphone.registry` | dialect codes, aliases, contact sides |
| `euskaphone.plugin` | G2P wrapper with the orthography2ipa plugin shape |

---
[← API](api.md) · [Home](../README.md) · [Benchmarks →](benchmarks.md)
