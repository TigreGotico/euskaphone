# Orthographic normalization

The pronunciation lattice reads Basque **letters**. Anything written as a
symbol, an abbreviation, a Roman numeral, or a numeric date must first be
spelled out into Basque words. euskaphone does this in one pre-lattice
pipeline, `euskaphone.normalize.normalize_text`, wired in as the
orthography2ipa `normalize` stage. By the time the lattice runs, the text is
ordinary Basque words and flows through allophony, sandhi, and stress like
everything else.

```python
from euskaphone.normalize import normalize_text

normalize_text("XX. mendean %20 igo da", "eu")
# 'hogeigarren mendean ehuneko hogei igo da'
```

Everything here is cited: the module docstrings and the data files
(`euskaphone/data/*.tsv`) name the Euskaltzaindia arau or EIMA style-guide
rule behind every form.

## Pipeline order

The stages run in a fixed order, each consuming what it recognizes and
passing the rest on:

1. **abbreviations**: `etab.` → `eta abar`. This runs first, so the periods
   that mark an abbreviation are gone before the Roman-numeral stage looks
   for the ordinal period.
2. **dates**: numeric `Y/M/D` triples become the `…ko …aren …an` form before
   the `/` gets split up.
3. **units**: percent, currency, and unit symbols become words.
4. **romans**: Roman ordinals and monarch numerals.
5. **numbers**: the vigesimal cardinal/ordinal core (see
   [`numbers.md`](numbers.md)) verbalizes every remaining digit token.

Stages 1-4 emit Basque words, so the number stage never re-touches their
output.

## 1. Abbreviations

A curated, cited list of abbreviations (`laburdurak`) expands to the full
spoken form. The list is **data, not code**: it lives in
`euskaphone/data/abbreviations.tsv` and grows by adding a cited row.

```python
normalize_text("Liburuak, aldizkariak, etab.", "eu")   # '… eta abar'
normalize_text("K.a. 50", "eu")                         # 'Kristo aurretik ...'
```

| written | read | gloss |
|---|---|---|
| `etab.` | eta abar | et cetera |
| `adib.` | adibidez | e.g. |
| `zk.` | zenbakia | no. |
| `or.` | orrialdea | page |
| `K.a.` / `K.o.` | Kristo aurretik / Kristo ondoren | BC / AD |

Sources: **Euskaltzaindia Araua 196** (*Laburtzapenak*) and the EIMA
*Ortotipografia* style guide.

## 2. Roman numerals

Two conventions, both cited to **Araua 18** and the *Euskara Batuaren
Eskuliburua*.

**Ordinal-period.** A Roman numeral followed by a period is an ordinal. The
period is the `-garren` marker itself, the same convention Araua 18 fixes
for Arabic digits (`20.` = `hogeigarren`):

```
XX. mendea    -> hogeigarren mendea      (the twentieth century)
V. kapitulua  -> bosgarren kapitulua
```

**Monarchs and popes.** A Roman numeral on a dynastic name is a *postposed*
ordinal that is **always declined**, carrying the article `-a`:

```
Luis XIV.a          -> Luis hamalaugarrena
Benedikto XVI.aren  -> Benedikto hamaseigarrenaren
Karlos I.a          -> Karlos lehena          (suppletive first)
```

### The `V.` ambiguity

A lone `V.` at the end of a sentence is a numeral plus a full stop, not
"fifth". The heuristic:

- **Monarch reading wins first.** A Roman numeral immediately preceded by a
  capitalized word (a proper name) is read as a postposed declined ordinal,
  period or not.
- **Ordinal-period otherwise.** A Roman plus period is read as an ordinal
  only when the next token starts with a lower-case letter, the common noun
  the ordinal modifies (`mendea`, `kapitulua`). A Roman plus period that ends
  the string, or is followed by a capitalized word, is left as a literal
  numeral.

This deliberately errs toward leaving text alone when the reading is
genuinely ambiguous: null beats a wrong reading. Ordinary words that merely
start with Roman letters (`Luis`, `Ikusi`) are never read as numerals,
because a lower-case declension is only recognized after the period.

## 3. Units, currency, and percent

Symbols are read as their full word (**Araua 197**, *Sinboloak*), with the
Basque-specific word order and declension.

**Percent.** `%` is the word `ehuneko`, read before the number in either
writing order:

```
%5   -> ehuneko bost
5%   -> ehuneko bost
```

**Currency.** The money word follows the number, and a relational ending
attaches to the spelled word. The numeral "one" (`bat`) is postposed:

```
5 €     -> bost euro
€5eko   -> bost euroko       (relational -ko on the vowel-final word: no epenthetic e)
1 €     -> euro bat
```

**Units.** Number then unit word, carrying any declension the writer
hyphenated onto the symbol:

```
5 km      -> bost kilometro
3 km-ra   -> hiru kilometrora
50 kg-ko  -> berrogeita hamar kilogramoko
```

The symbol-to-word table is in `euskaphone/data/units.tsv` (data, not code).

## 4. Dates

Numeric dates convert to the spoken shape **Araua 37** (*Data nola
adierazi*) fixes: year in the locative-genitive, month name in the
possessive genitive, day in the inessive.

```
2024-01-15   -> bi mila eta hogeita lauko urtarrilaren hamabostean
15/01/2024   -> bi mila eta hogeita lauko urtarrilaren hamabostean
1995/III/07  -> mila bederatziehun eta laurogeita hamabosteko martxoaren zazpian
```

Field order is resolved without a locale guess. The four-digit (or `>31`)
field is the year, and its position decides ISO `Y/M/D` versus European
`D/M/Y`. A Roman-numeral field is the month. A triple that does not validate
as a real calendar date is left untouched, so a ratio like `3/4` is never
mistaken for a date. A date already written with a month name
(`2024ko urtarrilaren 15ean`) needs nothing from this stage: its `2024ko`
and `15ean` are ordinary case-suffixed numerals the number stage verbalizes
on its own (see [`numbers.md`](numbers.md)).

## Sources

- Euskaltzaindia **Araua 18**: *Ordinalen eta banatzaileen idazkera*
- Euskaltzaindia **Araua 37**: *Data nola adierazi*
- Euskaltzaindia **Araua 196**: *Laburtzapenak: laburdurak eta siglak*
- Euskaltzaindia **Araua 197**: *Sinboloak*
- Euskaltzaindia, *Euskara Batuaren Eskuliburua* (dynastic Roman numerals)
- EIMA / Basque Government, J. R. Zubimendi, *Ortotipografia* (2004)

---
[← Numbers](numbers.md) · [Home](../README.md) · [Code-switch →](codeswitch.md)
