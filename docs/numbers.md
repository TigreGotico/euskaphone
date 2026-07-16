# Number verbalization (vigesimal)

Basque cardinals are **base-20**. euskaphone spells digit tokens into Basque
words *before* the pronunciation lattice runs (the orthography2ipa `normalize`
stage), so spelled-out numbers flow through allophony, sandhi and stress like any
other word.

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
follows the hundreds (`mila eta berrehun` 1200 vs `mila berrehun eta bi` 1202) —
the rule stated verbatim in Araua 7.

## Ordinals

The suffix is `-garren`, attached to the last element; 1st is suppletive
(`lehen`/`lehenengo`), and 5th drops the `t` (`bosgarren`, not `*bostgarren`).

```
1  lehenengo   2  bigarren   5  bosgarren   16 hamaseigarren   20 hogeigarren
```

## Case-suffixed numerals and clock time

Basque declines a numeral phrase on its **final element** only. euskaphone
appends the surface case ending the writer wrote onto the pronounced last word
(it does not re-derive Basque numeral morphophonology):

```
1936ko gerra   -> mila bederatziehun eta hogeita hamaseiko gerra   (year = cardinal)
20:00etan      -> hogeietan                                        (plural inessive)
```

## Dialect variants and the `bost`/`bortz` correction

Araua 7 (point 3) states that `bortz` (5) is used in *some* Iparralde varieties,
but that **most of Low Navarre and Zuberoa say `bost`** — contradicting the
common belief that Souletin is the `bortz` dialect. euskaphone therefore keeps
Batua `bost` for every coded lect by default and offers the `bortz` series
(`hamabortz`, `bortzehun`) for **Lapurdian only**. An unattested dialect swap is
worse than the attested standard form.

## Separators

The written form of a digit token is mapped onto an integer or decimal by the
European/Basque convention: the **comma is the decimal separator** and the
**period and space are thousands separators**. So `2,5` is 2.5, `1.000.000` and
`1 000 000` are one million, and the ambiguous `2.500` (period + exactly three
digits) reads as the thousands grouping 2500 rather than 2.5. A period that does
not form a 1–3 + 3-digit grouping (`2.5`, `2.53`) falls back to a decimal point.

## Where the composition lives

The vigesimal cardinal/ordinal composition is delegated to `ovos-number-parser`
(`pronounce_number` / `pronounce_ordinal`, `lang="eu"`), which carries the
Euskaltzaindia **Araua 7** ("Zenbakien idazkeraz", cardinals: the `-ehun`
hundreds, the `eta`-drop rule) and **Araua 18** ("Ordinalen … idazkera",
ordinals: the `-garren` suffix, the `bost` → `bos` drop) tables. euskaphone
keeps only the layer that needs orthographic context — separator handling,
case-suffix attachment, clock times, and the Lapurdian `bortz` substitution.

Both arauak are deposited in the papers library
(`papers/iberian/euskaltzaindia_araua07_*.pdf`, `…araua18_*.pdf`).
