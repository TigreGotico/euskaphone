# Architecture

euskaphone phonemizes by driving the shared **orthography2ipa** candidate
lattice and layering on only the concerns orthography2ipa leaves to the caller.

```
text
  │
  ├─ number normalization      euskaphone.number_utils  (o2i `normalize` stage)
  │     vigesimal cardinals/ordinals, case-suffix, clock time
  │
  ├─ code-switch routing       euskaphone.codeswitch    (outside the engine)
  │     detect es/fr words → es-ES/fr-FR lattice → nativize to Basque inventory
  │
  ├─ Basque runs → G2P(lect)   orthography2ipa lattice
  │     grapheme table + allophony + cross-word sandhi = the dialect's phonology
  │     (lexicon overlay via register_lexicon, empty by default)
  │
  └─ IPA
```

**A dialect is a lect spec.** There is no euskaphone-side accent transform: the
apical/laminal sibilants, affricates, Souletin aspiration and `/y/` are produced
by the `eu-x-*` specs orthography2ipa ships.

**Sandhi preservation.** Contiguous Basque tokens are transcribed as one phrase
so cross-word sandhi is preserved; only detected contact tokens are transcribed
in isolation and nativized.

**No homograph subsystem — by design.** Basque orthography is near-phonemic, so
grapheme readings are essentially fixed and sense-independent. Where tugaphone
needs `bifonia` for Portuguese heterophones, euskaphone ships nothing — a scope
decision, not an omission.

## Module map

| module | role |
|--------|------|
| `euskaphone.lattice_core` | engine wiring, `phonemize`, `register_lexicon` |
| `euskaphone.number_utils` | vigesimal verbalization + `normalize_numbers` |
| `euskaphone.codeswitch` | detection, contact transcription, nativization |
| `euskaphone.registry` | dialect codes, aliases, contact sides |
| `euskaphone.plugin` | OVOS `opm.g2p` plugin wrapper |
