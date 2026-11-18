# Orthographic normalization

The pronunciation lattice reads Basque **letters**. A number, a date, a clock
time, an abbreviation, a Roman numeral, a unit or a currency symbol must first
become Basque words. `euskaphone.normalize.normalize_text` does this before the
lattice runs, as the orthography2ipa `expand` stage. The lattice then reads
ordinary Basque words, with allophony, sandhi and stress.

```python
from euskaphone.normalize import normalize_text

normalize_text("XX. mendean %20 igo da", "eu")
# 'hogeigarren mendean ehuneko hogei igo da'
```

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
```

An **abbreviation at the end of a sentence** keeps one period, because its
period also ends the sentence (Araua 196, p. 31):

```
katuak etab.  -> katuak eta abar.
```

Where the norm gives two readings, euskaphone follows text2spoken: `3,14` reads
`hiru koma hamalau`, `K.a.` reads `Kristo aurreko` and `hurr.` reads
`hurrengoak`.

## The fallbacks

The fallbacks run on text2spoken's output, in this order. Each one reads only
its own form.

| Form | Example | Reading | Module |
|---|---|---|---|
| Clock time with no case ending | `10:30` | goizeko hamarrak eta hogeita hamar | `normalize` |
| Space-grouped thousands | `1 000 000 lagun` | milioi bat lagun | `number_utils` |
| Digits with `-garren` | `16garren` | hamaseigarren | `number_utils` |
| A point as the decimal mark | `2.5` | bi koma bost | `number_utils` |
| Currency symbol before the number | `€5eko` | bost euroko | `units` |
| Unit symbols `dm g mg t ml cl h` | `5 g`, `1 g-ko` | bost gramo, gramo bateko | `units` |
| Bare Roman numeral after a name | `Karlos V` | Karlos bosgarrena | `romans` |
| `h.d. kap. lib. orr.`, and `etab.` and `k.a.` in another case | `h.d.`, `ETAB.` | hau da., eta abar. | `abbreviations` |
| An abbreviation of the table with a capital | `Jn. Agirre` | Jauna Agirre | `normalize` |
| Digits with a glued case ending | `100dik gora` | ehundik gora | `number_utils` |

Last, euskaphone reads the digits that are still in the text. text2spoken
leaves a code as a name, and the lattice deletes the digits it cannot read.
So each run of digits reads as a number in its place, and the letters and
marks around it stay: `B12` gives `Bhamabi`, and `AP-8` gives `AP-zortzi`.

The fallbacks keep the whitespace of the text, newlines and tabs included.

The number fallbacks spell with `BasqueNumberParser`. The unit fallback keeps
the number that text2spoken read and reads only the symbol. A unit symbol is a
unit only right after digits, so `g letra` stays as written.

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
table (`euskaphone/data/units.tsv`) are data, not code. Each row names its
source. The fallbacks read their words from these tables.

## Deprecated stages

The stages that text2spoken replaces keep their names and their behaviour, and
each call gives a `DeprecationWarning` that names the release that removes
them:

| Module | Deprecated names |
|---|---|
| `euskaphone.number_utils` | `normalize_numbers` |
| `euskaphone.dates` | `normalize_dates`, `compose_date`, `MONTHS_GENITIVE` |
| `euskaphone.abbreviations` | `expand_abbreviations` |
| `euskaphone.romans` | `normalize_romans` |
| `euskaphone.units` | `normalize_units` |
| `euskaphone.numverbal` | `spell_cardinal`, `inessive`, `locative_genitive` |

Use `normalize_text` in their place.

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
[← Numbers](numbers.md) · [Home](../README.md) · [Code-switch →](codeswitch.md)
