# Orthographic normalization

<!-- agent-hint
covers: how text becomes Basque words before the lattice runs, and which stage reads each form
source: euskaphone/normalize.py, euskaphone/number_utils.py, euskaphone/units.py, euskaphone/romans.py, euskaphone/abbreviations.py, euskaphone/data/abbreviations.tsv, euskaphone/data/units.tsv
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/normalization.md
see: numbers.md, api.md
-->

The pronunciation lattice reads Basque **letters**. A number, a date, a clock
time, an abbreviation, a Roman numeral, a unit or a currency symbol must first
become Basque words. `euskaphone.normalize.normalize_text` does this before the
lattice runs, as the orthography2ipa `expand` stage. The lattice then reads
ordinary Basque words, with allophony, sandhi and stress.

```python
from euskaphone.normalize import normalize_text

normalize_text("XX. mendean %20 igo da", "eu")
# 'hogeigarren mendean ehuneko hogei igo da'
normalize_text("Luis XIV.a errege zen", "eu")
# 'Luis hamalaugarrena errege zen'
normalize_text("Sarrera €5eko da", "eu")
# 'Sarrera bost euroko da'
normalize_text("15/01/2024", "eu")
# 'bi mila eta hogeita lauko urtarrilaren hamabosta'
```

text2spoken reads the Roman-numeral ordinals (`XX.` gives `hogeigarren`), the monarch
numerals (`Luis XIV.a` gives `hamalaugarrena`), the numeric dates, and the unit, currency and
percent symbols with Basque word order and declension. euskaphone reads what text2spoken
leaves as written, such as `€5eko`.

## How the text is read

The reading has two steps.

1. **text2spoken reads the text.** [text2spoken](https://github.com/TigreGotico/text2spoken)
   reads numbers, dates, clock times, money, measures, abbreviations and Roman
   numerals. Where it reads a form, its reading stands.
2. **euskaphone reads what text2spoken leaves.** A fallback reads one class of
   form that text2spoken leaves as written. Each fallback names the
   text2spoken issue for its class. When text2spoken reads the form, the
   fallback goes.

text2spoken reads the text in the lect that `euskaphone.registry.resolve_lect`
gives. Every name of a lect reaches text2spoken as one tag: `lapurtera`,
`labourdin` and `eu-x-lapurtera` all reach it as `eu-x-lapurdi`. A lect that
text2spoken refuses as a language tag reads as `eu`.

Text that is already spelled out comes through unchanged.

## What text2spoken reads

Some examples, each with the Euskaltzaindia norm that gives the reading:

```
XX. mendea            -> hogeigarren mendea                   (Araua 18)
16. kapitulua         -> hamaseigarren kapitulua              (Araua 203)
Luis XIV.a            -> Luis hamalaugarrena
1936ko gerra          -> mila bederatziehun eta hogeita hamaseiko gerra
3/4 zati              -> hiru laurden zati                    (Araua 203)
%5, 5%                -> ehuneko bost                         (Araua 197)
5 €, €5               -> bost euro
1 kg                  -> kilogramo bat
3 km-ra               -> hiru kilometrora
etab. hori            -> eta abar hori                        (Araua 196)
23. or.               -> hogeita hirugarren orrialdea.
```

A **bare numeric date** reads the day in the absolutive, with the article
(Araua 203, p. 66: «Data: mila bederatziehun eta laurogeita hiruko martxoaren
zazpia»). A date with a case ending reads the case:

```
2024-01-15               -> bi mila eta hogeita lauko urtarrilaren hamabosta
Bilera 2024-01-15ean da  -> Bilera bi mila eta hogeita lauko urtarrilaren hamabostean da
```

A **clock time** reads with the part of the day, the everyday reading of
Araua 35 (p. 4: «Arratsaldeko hiruretan»). The hour takes the article, and the
case ending goes on the last word (p. 3: «Hamarrak eta hamarrean»):

```
20:00etan  -> arratsaldeko zortzietan
20:10ean   -> arratsaldeko zortziak eta hamarrean
```

A clock time with no case ending reads in the same way, with the article on
the hour (Araua 203, p. 49: «12:15 dira (hamabiak eta hamabost …)»). A fallback
reads it:

```
Bilera 10:30 da  -> Bilera goizeko hamarrak eta hogeita hamar da
12:00            -> eguerdiko hamabiak
12:00 h          -> eguerdiko hamabiak
```

The hour symbol `h` after a clock time adds no word. Araua 203 (p. 51) calls
it redundant: «Itsasgorak: 05:49 h eta 18:07 h» is «erredundantea».

A point between the hour and the minutes, with a case ending of the clock,
also gives a clock time. Araua 203 (p. 51) says that minutes are not decimals.
A fallback reads the time as text2spoken reads it with a colon:

```
Bilera 10.30etan  -> Bilera goizeko hamarrak eta hogeita hamarretan
```

An **abbreviation at the end of a sentence** keeps one period, because its
period also ends the sentence (Araua 196, p. 31):

```
katuak etab.  -> katuak eta abar.
```

A capital after the period starts a name or a sentence (Araua 196, p. 30). So
the period stays before a capital only after `etab.`, the abbreviation that
ends a list. After the other abbreviations, the period goes:

```
katuak etab. Gero etorri  -> katuak eta abar. Gero etorri
h.d. Euskal Herrian       -> hau da Euskal Herrian
```

Where the norm gives two readings, euskaphone follows text2spoken: `3,14` reads
`hiru koma hamalau`, `K.a.` reads `Kristo aurreko` and `hurr.` reads
`hurrengoak`.

## The fallbacks

Before text2spoken reads the text, digits that two commas or more group in
threes are grouped by spaces (`1,000,000` → `1 000 000`). text2spoken reads that
writing with the currency or unit beside it: `€1,000,000` reads `milioi bat
euro`.

The fallbacks run on text2spoken's output, in this order. Each one reads only
its own form.

| Form | Example | Reading | Module |
|---|---|---|---|
| Clock time with no case ending | `10:30` | goizeko hamarrak eta hogeita hamar | `normalize` |
| Space-grouped numbers joined by `-`, `–` or `/` | `10 000-20 000 lagun` | hamar mila-hogei mila lagun | `number_utils` |
| Digits with `-garren` | `16garren` | hamaseigarren | `number_utils` |
| Clock time with a point and a case ending | `10.30etan` | goizeko hamarrak eta hogeita hamarretan | `normalize` |
| A point as the decimal mark | `2.5` | bi koma bost | `number_utils` |
| Currency symbol before the number | `€5eko` | bost euroko | `units` |
| Unit symbols `dm g mg t ml cl h` | `5 g`, `1 g-ko` | bost gramo, gramo bateko | `units` |
| Bare Roman numeral written with the letters `I`, `V` and `X`, after a name | `Karlos V` | Karlos bosgarrena | `romans` |
| `h.d. kap. lib. orr.`, and `etab.` and `k.a.` in another case | `h.d.`, `ETAB.` | hau da., eta abar. | `abbreviations` |
| An abbreviation of the table with a capital, or in capitals | `Jn. Agirre`, `—Jn. Agirre`, `ZK. 5` | Jauna Agirre, —Jauna Agirre, Zenbakia bost | `normalize` |
| Digits with a glued case ending | `100dik gora` | ehundik gora | `number_utils` |

Last, euskaphone reads the digits that are still in the text. text2spoken
leaves a code as a name, and the lattice deletes the digits it cannot read.
So each run of digits reads as a number in its place, and the letters and
marks around it stay: `B12` gives `Bhamabi`, and `AP-8` gives `AP-zortzi`.

The fallbacks keep the whitespace of the text, newlines and tabs included.

The number fallbacks spell with `BasqueNumberParser`. The unit fallback keeps
the number that text2spoken read and reads only the symbol. A unit symbol is a
unit only right after digits, so `g letra` stays as written.

A bare Roman numeral reads as an ordinal only after a name. Araua 203 (p. 7)
says that a Roman numeral is a cardinal, and its dynastic numerals use the
letters `I`, `V` and `X` only. So `Ikastola D eredua` and `Musika CD bat` stay
as written. A name ends in a letter, so the `V` of `Zk. V` stays too.

Some forms get no reading. `ad.` stays as written: Araua 196 lists it as
`aditza`, not `adibidez`. `e.a.` and `at.` stay as written, because no source
that euskaphone cites defines them.

## Lapurdian `bortz`

Araua 7 gives `bortz` for 5 in some northern varieties, and `BasqueNumberParser`
spells the `bortz` series for Lapurdian. text2spoken reads every Basque lect
as Batua, so `normalize_text("15", "eu-x-lapurdi")` gives `hamabost`. A strict
xfail test holds the `bortz` reading until text2spoken reads it.

## The data tables

The abbreviation table (`euskaphone/data/abbreviations.tsv`) and the unit
table (`euskaphone/data/units.tsv`) are data, not code. The header of each
file names its sources. The fallbacks read their words from these tables.

## Deprecated stages

The stages that text2spoken replaces keep their names and their behaviour.
Each call gives a `DeprecationWarning` that names the release that removes the
stage. The warnings of `inessive` and `locative_genitive` say that text2spoken
declines the numerals it reads; every other warning names its replacement:

| Module | Deprecated names | Use in their place |
|---|---|---|
| `euskaphone.number_utils` | `normalize_numbers` | `normalize_text` |
| `euskaphone.dates` | `normalize_dates`, `compose_date`, `MONTHS_GENITIVE` | `normalize_text` |
| `euskaphone.abbreviations` | `expand_abbreviations` | `normalize_text` |
| `euskaphone.romans` | `normalize_romans` | `normalize_text` |
| `euskaphone.units` | `normalize_units` | `normalize_text` |
| `euskaphone.numverbal` | `spell_cardinal` | `BasqueNumberParser(dialect).cardinal` |
| `euskaphone.numverbal` | `inessive`, `locative_genitive` | `normalize_text` (the warning names no function) |

`euskaphone.normalize` and `euskaphone.dates` still give the names they
imported from these modules. `normalize.normalize_numbers` and the other four
names of `normalize` name `normalize_text`. `dates.spell_cardinal`,
`dates.inessive` and `dates.locative_genitive` name the replacement of their
`numverbal` row.

## Sources

- Euskaltzaindia **Araua 7**: *Zenbakien idazkeraz*
- Euskaltzaindia **Araua 18**: *Ordinalen eta banatzaileen idazkera*
- Euskaltzaindia **Araua 35**: *Orduak nola esan*
- Euskaltzaindia **Araua 196**: EBO (I), *Laburtzapenak: laburdurak eta siglak*
- Euskaltzaindia **Araua 197**: EBO (II), *Sinboloak*
- Euskaltzaindia **Araua 203**: EBO (VI), *Zenbakizko adierazpenak*

The PDFs are at `https://www.euskaltzaindia.eus/dok/arauak/Araua_NNNN.pdf`. A
page number is the PDF page.

---
[← Numbers](numbers.md) · [Index](index.md) · [Code-switch →](codeswitch.md)
