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
`.decimal(whole, frac)`, `.year(n)`, `.clock(hour, minute)` and
`.pronounce_token(token, as_ordinal=False)`. It takes a lect code, canonical
or older (`eu-x-lapurdi` or `eu-x-lapurtera`), and does not resolve an alias
such as `labourdin`: it raises `ValueError` for one.

`read_space_grouped_numbers(text, dialect)`, `read_garren_ordinals(text, dialect)`,
`read_dot_decimals(text, dialect)` and `read_glued_case_endings(text, dialect)`
are the fallbacks for `10 000-20 000`, `16garren`, `2.5` and `100dik`, which
text2spoken leaves as written. text2spoken reads a single space-grouped number,
`1 000 000`, and leaves two of them joined by a hyphen, an en dash or a slash.
`read_code_digits(text, dialect)` reads the digits of a code (`B12`). They run
on text2spoken's output inside `normalize_text`.

`normalize_numbers(text, dialect="eu", strict=False)` is deprecated: use
`normalize_text`.

Vigesimal cardinal/ordinal composition is delegated to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`). euskaphone keeps
only the orthographic layer: written-separator handling, case-suffix
attachment and the Lapurdian `bortz` substitution.

## Code-switch: `euskaphone.codeswitch`

`is_contact_word(token)`, `transcribe_contact(word, contact, keep_y=False)`,
`split_runs(text, contact, default_side="es")`. The statistical per-word language detector
behind `contact="auto"` is `euskaphone.langdetect.get_detector()` (returns
`None` when the optional `markovonnx` models are not installed; the
orthographic heuristic then takes over).

## Normalization: `euskaphone.normalize`

`normalize_text(text, dialect="eu")` spells numbers, dates, clock times,
abbreviations, Roman numerals and unit/currency/percent symbols into Basque
words. text2spoken reads the text first, and the fallbacks read the forms it
leaves as written. It runs automatically as the engine's `expand` stage and
is callable on its own. It resolves an alias such as `labourdin`.

`text2spoken_tag(dialect)` gives the language tag text2spoken reads a lect in,
and `text2spoken_reading(text, dialect)` gives text2spoken's reading with no
fallback. `read_bare_clock_times(text, dialect)` is the fallback for a clock
time with no case ending (`10:30`), and `read_capitalized_abbreviations(text,
dialect)` the fallback for an abbreviation with a capital (`Jn.`).

The fallbacks of the other modules are `units.read_currency_before_number`,
`units.read_unit_symbols`, `romans.read_bare_monarch_numerals` and
`abbreviations.read_left_abbreviations`. The stages that text2spoken replaces
are deprecated: `dates.normalize_dates`, `dates.compose_date`,
`dates.MONTHS_GENITIVE`, `abbreviations.expand_abbreviations`,
`romans.normalize_romans`, `units.normalize_units`,
`numverbal.spell_cardinal`, `numverbal.inessive` and
`numverbal.locative_genitive`. Each call gives a `DeprecationWarning` that names
the release that removes it. The names that `normalize` and `dates` imported
from these modules still resolve there. Their warning names the replacement
that the reader they give names, never another deprecated name.

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
