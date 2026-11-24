# API

<!-- agent-hint
covers: every public name of euskaphone with its signature and default
source: euskaphone/__init__.py, euskaphone/registry.py, euskaphone/lattice_core.py, euskaphone/number_utils.py, euskaphone/normalize.py, euskaphone/codeswitch.py, euskaphone/accent.py, euskaphone/pitch_accent.py, euskaphone/plugin.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/api.md
see: quickstart.md, architecture.md
-->

This page lists every public name of euskaphone, grouped by module, with its signature and default.

## `EuskaPhonemizer`

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

A static method. It tells whether `dialect` names a Basque lect, not the Batua fallback.

The signatures below come from `inspect`:

```python
import inspect
from euskaphone import EuskaPhonemizer

str(inspect.signature(EuskaPhonemizer.__init__))
# '(self, toponyms: bool = True, lexicon: Optional[str] = None) -> None'
str(inspect.signature(EuskaPhonemizer.phonemize_sentence))
# "(self, sentence: str, dialect: str = 'eu', contact: str = 'none', pitch_accent: bool = False) -> str"
EuskaPhonemizer.is_supported("souletin"), EuskaPhonemizer.is_supported("xx")
# (True, False)
```

## Registry: `euskaphone.registry`

| function | returns |
|----------|---------|
| `resolve_lect(dialect="eu")` | the eu lect code a name resolves to (falls back to `eu`) |
| `list_dialects()` | the eight canonical lect codes (see [dialects.md](dialects.md)) |
| `dialect_aliases()` | the human-readable alias → code table (a copy) |
| `is_continental(lect)` | whether `lect` is an Iparralde (France-side) dialect |
| `default_contact(lect)` | `"fr"` for continental, `"es"` otherwise |
| `is_supported(dialect)` | strict membership test |
| `normalize_dialect_code(name)` | the lower-cased and trimmed name, used for the lookup |

## Numbers: `euskaphone.number_utils`

`BasqueNumberParser(dialect="eu")` with `.cardinal(n)`, `.ordinal(n)`,
`.decimal(whole, frac)`, `.year(n)`, `.clock(hour, minute)` and
`.pronounce_token(token, as_ordinal=False)`, which returns `None` for a token it cannot read. It takes every name of a lect
that `resolve_lect` takes: a canonical or older code (`eu-x-lapurdi` or
`eu-x-lapurtera`) or an alias such as `labourdin`. A name outside Basque, such
as `xx`, raises `ValueError`. An `eu` tag with a subtag the registry does not
know, such as `eu-ES` or `eu-x-foo`, reads as Batua, as `resolve_lect` does.

`read_space_grouped_numbers(text, dialect)`, `read_garren_ordinals(text, dialect)`,
`read_dot_decimals(text, dialect)` and `read_glued_case_endings(text, dialect)`
are the fallbacks for `10 000-20 000`, `16garren`, `2.5` and `100dik`, which
text2spoken leaves as written. text2spoken reads a single space-grouped number,
`1 000 000`, and leaves two of them joined by a hyphen, an en dash or a slash.
`read_code_digits(text, dialect)` reads the digits of a code (`B12`). They run
on text2spoken's output inside `normalize_text`.

`comma_groups_as_spaces(text)` groups by spaces the digits that two commas or
more group in threes: `1,000,000` becomes `1 000 000`. It runs before
text2spoken inside `normalize_text`, so text2spoken reads the number with the
currency or unit beside it: `€1,000,000` reads `milioi bat euro`.

`normalize_numbers(text, dialect="eu", strict=False)` is deprecated: use
`normalize_text`. `numverbal.spell_token(token, dialect="eu")` and
`numverbal.spell_ordinal(n, dialect="eu")` spell a numeric token and an ordinal through
the same parser.

Vigesimal cardinal/ordinal composition is delegated to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`). euskaphone keeps
only the orthographic layer: written-separator handling, case-suffix
attachment and the Lapurdian `bortz` substitution.

## Code-switch: `euskaphone.codeswitch`

`is_contact_word(token)` is the orthographic heuristic. `detect_contact_word(token)` asks the
statistical detector first and uses the heuristic as backstop.
`contact_language(token, default_side="es")` classifies a contact token as `"en"`, `"fr"` or
`"es"`. `route_token(token, contact, default_side="es")` gives the language that a token
routes through, or `None` for Basque. `transcribe_contact(word, contact, keep_y=False)`
nativizes one word, and `split_runs(text, contact, default_side="es")` splits a text into
Basque and contact runs. The statistical per-word language detector
behind `contact="auto"` is `euskaphone.langdetect.get_detector()` (returns
`None` when the optional `markovonnx` models are not installed; the
orthographic heuristic then takes over). `langdetect` also holds
`MarkovLangDetector(models)`, `is_keep_word(word)`, `BASQUE_KEEP` and `DEFAULT_MARGIN`.

## Normalization: `euskaphone.normalize`

`normalize_text(text, dialect="eu")` spells numbers, dates, clock times,
abbreviations, Roman numerals and unit/currency/percent symbols into Basque
words. text2spoken reads the text first, and the fallbacks read the forms it
leaves as written. It runs automatically as the engine's `expand` stage and
is callable on its own. It resolves an alias such as `labourdin`.

`text2spoken_tag(dialect)` gives the language tag text2spoken reads a lect in,
and `text2spoken_reading(text, dialect)` gives text2spoken's reading with no
fallback. `read_bare_clock_times(text, dialect)` is the fallback for a clock
time with no case ending (`10:30`), `read_point_clock_times(text, dialect)` the
fallback for a clock time with a point and a case ending (`10.30etan`), and
`read_capitalized_abbreviations(text, dialect)` the fallback for an
abbreviation with a capital or in capitals (`Jn.`, `ZK.`).

`romans.roman_to_int(s)` and `romans.monarch_ordinal(n, dialect="eu")` read a Roman numeral.
The fallbacks of the other modules are `units.read_currency_before_number`,
`units.read_unit_symbols`, `romans.read_bare_monarch_numerals` and
`abbreviations.read_left_abbreviations`. The stages that text2spoken replaces
are deprecated: `dates.normalize_dates`, `dates.compose_date`,
`dates.MONTHS_GENITIVE`, `abbreviations.expand_abbreviations`,
`romans.normalize_romans`, `units.normalize_units`,
`numverbal.spell_cardinal`, `numverbal.inessive` and
`numverbal.locative_genitive`. Each call gives a `DeprecationWarning` that names
the release that removes the stage. The replacement of
`numverbal.spell_cardinal` is `BasqueNumberParser(dialect).cardinal`, the warnings of
`numverbal.inessive` and `numverbal.locative_genitive` say that text2spoken
declines the numerals it reads, and the replacement of every other stage is
`normalize_text`. The names that
`normalize` and `dates` imported from these modules still resolve there, and
their warning is the warning of the original name. See the table in
[normalization.md](normalization.md#deprecated-stages).

## Pitch accent: `euskaphone.pitch_accent`

`default_lexicon(area="northern_bizkaian")` loads the cited Northern Bizkaian
accent lexicon as a `PitchAccentLexicon`, which has `entries()`, `lookup(word)` and
`from_tsv`. `lookup(word)` returns an `AccentEntry` with `accent_class`
(`ACCENTED` / `UNACCENTED` / `UNKNOWN`), `accent_syllable`, `gloss`,
`source`. `mark_ipa(ipa_word, syllable)`, `annotate(word_orth, ipa_word, lexicon=None)` and
`annotate_sentence(sentence, transcribe_word, *, lexicon=None)` write the mark.

## Accent forcing: `euskaphone.accent`

`force_accent(text, dialect, mode="ipa")` with `mode` set to `"ipa"` or `"respell"`, and
`respell_report(text, dialect, rules=None, eps=1e-09)`, which returns a `RespellResult`
(`RespellRule` describes one rule; fields
`source`, `respelled`, `target_ipa`, `base_ipa`, `respelled_ipa`, `per_before`,
`per_after`, `accepted`, and the `gain` property). See [accent_forcing.md](accent_forcing.md).

## Lexicon: `euskaphone.register_lexicon`

`register_lexicon(dialect, source)` takes a path, a URL or an `hf://` id of a
`word<TAB>ipa` table. `lattice_core.lexicon_source(dialect)` returns the source registered for a lect, or
`None`, and `lattice_core.clear_caches()` drops the cache of per-lect engines. Both live in
`euskaphone.lattice_core` and are not exported by the package.

`euskaphone.register_toponyms(dialect="eu", *, force=False)` and
`euskaphone.register_hitz_overlay(dialect="eu")` register the two built-in
lexicons by hand. `lexicons.hitz_overlay_words()` returns the keys of the overlay, and
`lexicons.apply_builtins(toponyms=True, lexicon=None, dialect="eu")` applies the constructor flags.

`lattice_core.phonemize(text, dialect="eu", contact="none")` is the function behind
`EuskaPhonemizer.phonemize_sentence`.

## G2P wrapper: `euskaphone.plugin.EuskaphoneG2PPlugin`

`EuskaphoneG2PPlugin(lang="eu", contact="none")`, with `.language_codes`,
`.transcribe(text)` and `.transcribe_word(word, context=None)`. `contact` takes
the same values as `phonemize_sentence`. euskaphone declares no entry point, so
no plugin manager discovers this class: construct it yourself.

---
[← Accent forcing](accent_forcing.md) · [Index](index.md) · [Architecture →](architecture.md)
