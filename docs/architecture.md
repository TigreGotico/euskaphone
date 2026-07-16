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

**Negative-particle contraction.** The most audible Basque sandhi is the
categorical contraction of the negative particle *ez* /es̻/ with a following
auxiliary/verb onset — a connected-speech process every speaker applies. It is
carried by the shared `eu` lect spec's `sandhi_rules`, so euskaphone gets it for
free whenever a Basque run keeps *ez* and its verb in the same phrase:

| written | rule | IPA | process |
|---------|------|-----|---------|
| ez dut     | ez + d → ezt | `es̻ tut`      | onset /d/ devoices to [t], sibilant kept |
| ez da      | ez + d → ezt | `es̻ ta`       | onset /d/ devoices to [t] |
| ez zen     | ez + z → etz | `e ts̻en`      | sibilants coalesce to the affricate [ts̻] |
| ez naiz    | ez + n → en  | `e nais̻`      | sibilant deleted before a nasal |
| ez luke    | ez + l → el  | `e luke`       | sibilant deleted before a lateral |
| ez balitz  | ez + b → ezp | `es̻ palits̻`  | onset /b/ devoices to [p], sibilant kept |
| ez gara    | ez + g → ezk | `es̻ kaɾa`     | onset /ɡ/ devoices to [k], sibilant kept |

The rules are keyed to the negator alone (a lone *ez* word), so an unrelated
`z`-final word before a voiced onset (`naiz da` → `nais̻ da`) is untouched. The
contractions are pan-Basque and inherited by every `eu-x-*` dialect spec; the
*degree* varies, and where a dialect merges the laminal sibilant to apical (the
western/Biscayan `⟨z⟩` → [s̺] merger) the standard laminal-keyed rule does not
fire — `ez dut` surfaces there as `es̺ dut`, the honest "null beats a wrong
contraction" outcome rather than a forced standard form. Grounding:
Hualde & Ortiz de Urbina (2003), Hualde "Segmental phonology" §2; Hualde (1991),
*Basque Phonology*.

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
