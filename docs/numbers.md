# Number verbalization (vigesimal)

Basque cardinals are **base-20**. Numbers become Basque words *before* the
pronunciation lattice runs, so spelled-out numbers flow through allophony,
sandhi and stress like any other word. text2spoken reads the numbers of running
text, and `BasqueNumberParser` spells the number forms that text2spoken leaves
as written (see [normalization.md](normalization.md)).

## The vigesimal system

The tens are built on the four "twenty" heads, and 30/50/70/90 are the preceding
twenty **plus ten**:

| | | | |
|---|---|---|---|
| 20 `hogei` | 40 `berrogei` | 60 `hirurogei` | 80 `laurogei` |
| 30 `hogeita hamar` | 50 `berrogeita hamar` | 70 `hirurogeita hamar` | 90 `laurogeita hamar` |

The copulative `eta` ("and") contracts to `-ta` on the twenty head, but the
"ten" component always stays a **separate word** (Araua 7: `hogeita hamar`,
never `*hogeitamar`):

```
21  hogeita bat          31  hogeita hamaika       75  hirurogeita hamabost
100 ehun                 101 ehun eta bat          200 berrehun
1000 mila                1200 mila eta berrehun    1202 mila berrehun eta bi
1936 mila bederatziehun eta hogeita hamasei
```

`eta` links only the last two chunks and **drops** when a lower remainder
follows the hundreds (`mila eta berrehun` 1200 vs `mila berrehun eta bi` 1202).
This is the rule Araua 7 states verbatim.

## Ordinals

The suffix is `-garren`, attached to the last element. 1st is suppletive
(`lehen`/`lehenengo`), and 5th drops the `t` (`bosgarren`, not `*bostgarren`).

```
1  lehenengo   2  bigarren   5  bosgarren   16 hamaseigarren   20 hogeigarren
```

The norm writes an ordinal in digits with a period (Araua 203: `2.`, `3.a`).
text2spoken reads it: `16. kapitulua` gives `hamaseigarren kapitulua`, and
`1. kapitulua` gives `lehen kapitulua`. Araua 203 marks the writing `2garren` as
wrong, but its reading is clear, so a fallback reads it with
`BasqueNumberParser`: `16garren` gives `hamaseigarren`, and `1garren` gives
`lehenengo`.

## Case-suffixed numerals and clock time

Basque declines a numeral phrase on its **final element** only:

```
1936ko gerra   -> mila bederatziehun eta hogeita hamaseiko gerra   (year = cardinal)
20:00etan      -> arratsaldeko zortzietan
20:10ean       -> arratsaldeko zortziak eta hamarrean
20:10          -> arratsaldeko zortziak eta hamar
```

A clock time reads with the part of the day, the everyday reading of Araua 35.
The hour takes the article (`zortziak`), and the case ending goes on the last
word. With no case ending, the hour keeps the article (Araua 203, p. 49).

## Dialect variants and the `bost`/`bortz` correction

Araua 7 (point 3) states that `bortz` (5) is used in *some* Iparralde
varieties, but that **most of Low Navarre and Zuberoa say `bost`**. This
contradicts the common belief that Souletin is the `bortz` dialect.
`BasqueNumberParser` therefore keeps Batua `bost` for every coded lect and
spells the `bortz` series (`hamabortz`, `bortzehun`) for **Lapurdian only**. An
unattested dialect swap is worse than the attested standard form.

text2spoken reads every Basque lect as Batua, so running text in Lapurdian
reads `bost`. A strict xfail test holds the `bortz` reading until text2spoken
reads it.

## Separators

The written form of a digit token is mapped onto an integer or decimal by the
European/Basque convention: the **comma is the decimal separator** and the
**period and space are thousands separators**. So `2,5` is 2.5, `1.000.000` and
`1 000 000` are one million, and the ambiguous `2.500` (period + exactly three
digits) reads as the thousands grouping 2500 rather than 2.5. A period that does
not form a 1–3 + 3-digit grouping (`2.5`, `2.53`) falls back to a decimal point.

text2spoken reads `2,5`, `1.000.000`, `1 000 000` and `2.500`. It leaves `2.5`
as written, and two space-grouped numbers joined by a hyphen, an en dash or a
slash (`10 000-20 000`). The fallbacks read them by this convention.

A Basque decimal has one comma. Two commas or more, each before three digits,
are the English writing that Araua 203 (p. 11) names, where the comma groups
thousands: `1,000,000` reads `milioi bat`, as `1 000 000` does. text2spoken
leaves that writing as written, so euskaphone groups the digits by spaces before
text2spoken reads the text. The currency beside the number then reads too:
`€1,000,000` reads `milioi bat euro`.

## Where the composition lives

text2spoken reads the numbers of running text. `BasqueNumberParser` delegates
the vigesimal cardinal/ordinal composition to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`), which carries the
Euskaltzaindia **Araua 7** ("Zenbakien idazkeraz", cardinals: the `-ehun`
hundreds, the `eta`-drop rule) and **Araua 18** ("Ordinalen … idazkera",
ordinals: the `-garren` suffix, the `bost` → `bos` drop) tables. euskaphone
adds the layer that needs orthographic context: separator handling,
case-suffix attachment and the Lapurdian `bortz` substitution.
`normalize_numbers`, the number stage that text2spoken replaces, is
deprecated.

Both arauak are deposited in the papers library
(`papers/iberian/euskaltzaindia_araua07_*.pdf`, `…araua18_*.pdf`).

---
[← Dialects](dialects.md) · [Home](../README.md) · [Normalization →](normalization.md)
