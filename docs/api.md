# API

## `EuskaPhonemizer`

```python
from euskaphone import EuskaPhonemizer
ph = EuskaPhonemizer()
```

### `phonemize_sentence(sentence, dialect="eu", contact="auto") -> str`

Phonemize `sentence` for `dialect` (a lect code or human-readable alias).
`contact` is the embedded-language policy: `"auto"` (per-dialect side —
peninsular→Spanish, continental→French), `"es"`, `"fr"`, or `"none"`.

### `is_supported(dialect) -> bool`

Whether `dialect` names a Basque lect (not merely the Batua fallback).

## Registry — `euskaphone.registry`

| function | returns |
|----------|---------|
| `resolve_lect(dialect="eu")` | the eu lect code a name resolves to (falls back to `eu`) |
| `list_dialects()` | the eight canonical lect codes |
| `dialect_aliases()` | the human-readable alias → code table (a copy) |
| `is_continental(lect)` | whether `lect` is an Iparralde (France-side) dialect |
| `default_contact(lect)` | `"fr"` for continental, `"es"` otherwise |
| `is_supported(dialect)` | strict membership test |

## Numbers — `euskaphone.number_utils`

`BasqueNumberParser(dialect="eu")` with `.cardinal(n)`, `.ordinal(n)`,
`.decimal(whole, frac)`, `.year(n)`, `.clock(hour, minute)`.
`normalize_numbers(text, dialect="eu")` rewrites every numeric token in running
text.

Vigesimal cardinal/ordinal composition is delegated to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`); euskaphone keeps only
the orthographic layer — written-separator handling, case-suffix attachment,
clock times, and the Lapurdian `bortz` substitution.

## Code-switch — `euskaphone.codeswitch`

`is_contact_word(token)`, `transcribe_contact(word, contact, keep_y=False)`,
`split_runs(text, contact)`.

## Lexicon — `euskaphone.register_lexicon`

```python
from euskaphone import register_lexicon
register_lexicon("eu", "path/or/url/or/hf://id")   # word<TAB>ipa
```

## OVOS plugin — `euskaphone.plugin.EuskaphoneG2PPlugin`

`.language_codes`, `.transcribe(text)`, `.transcribe_word(word, context=None)`.
Entry-point group `opm.g2p`, name `euskaphone`.
