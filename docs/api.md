# API

## `EuskaPhonemizer`

```python
from euskaphone import EuskaPhonemizer
ph = EuskaPhonemizer()
```

`EuskaPhonemizer(toponyms=True, lexicon=None)` registers the built-in lexicons
for `eu`. `toponyms=False` leaves out the toponym seed, and `lexicon="hitz"`
adds the HiTZ overlay (see [lexicons.md](lexicons.md)).

### `phonemize_sentence(sentence, dialect="eu", contact="none", pitch_accent=False) -> str`

Phonemize `sentence` for `dialect` (a lect code or human-readable alias).
`contact` is the embedded-language policy: `"none"` (the default, no
switching), `"auto"` (per-word detection
among `es`/`fr`/`en`, undetected words falling to the dialect's side,
peninsular→Spanish, continental→French), `"es"`, `"fr"` or `"en"`. `pitch_accent=True` adds the Northern Bizkaian lexical accent
marks (Biscayan only, see [pitch_accent.md](pitch_accent.md)).

### `is_supported(dialect) -> bool`

Whether `dialect` names a Basque lect, not the Batua fallback.

## Registry: `euskaphone.registry`

| function | returns |
|----------|---------|
| `resolve_lect(dialect="eu")` | the eu lect code a name resolves to (falls back to `eu`) |
| `list_dialects()` | the eight canonical lect codes (see [dialects.md](dialects.md)) |
| `dialect_aliases()` | the human-readable alias → code table (a copy) |
| `is_continental(lect)` | whether `lect` is an Iparralde (France-side) dialect |
| `default_contact(lect)` | `"fr"` for continental, `"es"` otherwise |
| `is_supported(dialect)` | strict membership test |

## Numbers: `euskaphone.number_utils`

`BasqueNumberParser(dialect="eu")` with `.cardinal(n)`, `.ordinal(n)`,
`.decimal(whole, frac)`, `.year(n)`, `.clock(hour, minute)`.
`normalize_numbers(text, dialect="eu", strict=False)` rewrites every numeric
token in running text. Both take a lect code, canonical or older (`eu-x-lapurdi`
or `eu-x-lapurtera`), and do not resolve an alias such as `labourdin`:
`BasqueNumberParser` raises `ValueError` for one, and `normalize_numbers` reads it
as `eu`. `EuskaPhonemizer.phonemize_sentence` resolves aliases before it calls
them.

Vigesimal cardinal/ordinal composition is delegated to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`). euskaphone keeps
only the orthographic layer: written-separator handling, case-suffix
attachment, clock times, and the Lapurdian `bortz` substitution.

## Code-switch: `euskaphone.codeswitch`

`is_contact_word(token)`, `transcribe_contact(word, contact, keep_y=False)`,
`split_runs(text, contact, default_side="es")`. The statistical per-word language detector
behind `contact="auto"` is `euskaphone.langdetect.get_detector()` (returns
`None` when the optional `markovonnx` models are not installed; the
orthographic heuristic then takes over).

## Normalization: `euskaphone.normalize`

`normalize_text(text, dialect="eu")` spells abbreviations, Roman-numeral
ordinals, unit/currency/percent symbols, and numeric dates into Basque
words. It runs automatically as the engine's `normalize` stage and is
callable on its own.

## Pitch accent: `euskaphone.pitch_accent`

`default_lexicon(area="northern_bizkaian")` loads the cited Northern Bizkaian
accent lexicon.
`lookup(word)` returns an entry with `accent_class`
(`ACCENTED` / `UNACCENTED` / `UNKNOWN`), `accent_syllable`, `gloss`,
`source`.

## Accent forcing: `euskaphone.accent`

`force_accent(text, dialect, mode="ipa"|"respell")` and
`respell_report(text, dialect)`, which returns a `RespellResult` (fields
`source`, `respelled`, `target_ipa`, `base_ipa`, `respelled_ipa`, `per_before`,
`per_after`, `accepted`, and the `gain` property). See [accent_forcing.md](accent_forcing.md).

## Lexicon: `euskaphone.register_lexicon`

```python
from euskaphone import register_lexicon
register_lexicon("eu", "path/or/url/or/hf://id")   # word<TAB>ipa
```

`euskaphone.register_toponyms(dialect="eu", *, force=False)` and
`euskaphone.register_hitz_overlay(dialect="eu")` register the two built-in
lexicons by hand.

## G2P wrapper: `euskaphone.plugin.EuskaphoneG2PPlugin`

`EuskaphoneG2PPlugin(lang="eu", contact="none")`, with `.language_codes`,
`.transcribe(text)` and `.transcribe_word(word, context=None)`. `contact` takes
the same values as `phonemize_sentence`. euskaphone declares no entry point, so
no plugin manager discovers this class: construct it yourself.

---
[← Accent forcing](accent_forcing.md) · [Home](../README.md) · [Architecture →](architecture.md)
