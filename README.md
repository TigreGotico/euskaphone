# euskaphone

euskaphone is a dialect-aware Basque (Euskara) text-to-IPA phonemizer. It is a
TTS frontend built on the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) pronunciation
lattice. euskaphone is the Basque sibling of
[tugaphone](https://github.com/TigreGotico/tugaphone) (Portuguese) and
[mwl_phonemizer](https://github.com/TigreGotico/mwl_phonemizer) (Mirandese). It
is an open, inspectable, source-cited pipeline for the Basque research and
speech-technology community.

A dialect is an orthography2ipa Basque lect spec. The spec's grapheme table,
allophony, and cross-word sandhi produce the dialect's phonology directly: the
apical/laminal sibilant contrast, the affricates, Souletin aspiration, and
`/y/`. euskaphone adds only the stages orthography2ipa leaves to the caller.

## Install

```bash
pip install euskaphone
```

## Quickstart

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
ph.phonemize_sentence("Zazpi katu zuri ikusi ditut.")          # Batua (default)
# 's̻as̻pi katu s̻uɾi ikus̺i ditut'

ph.phonemize_sentence("Hotza egiten du gaur mendian.", "souletin")
# 'hots̻a eɡiten dy ɡauɾ mendian'   (Souletin: aspiration, /y/)
```

## Dialects

Eight lects, selectable by BCP-47 code or by a human-readable alias:

| code | dialect | aliases |
|------|---------|---------|
| `eu` | Standard Basque | `batua`, `standard` |
| `eu-x-bizkaiera` | Biscayan | `biscayan`, `western` |
| `eu-x-gipuzkera` | Gipuzkoan | `guipuzcoan`, `central` |
| `eu-x-lapurtera` | Lapurdian | `labourdin` |
| `eu-x-nafarra-garaia` | High Navarrese | `high-navarrese` |
| `eu-x-nafarra-beherea` | Low Navarrese | `low-navarrese` |
| `eu-x-zuberera` | Souletin | `souletin`, `xiberotarra` |
| `eu-x-erronkariera` | Roncalese (†) | `roncalese` |

## What euskaphone adds

### 1. Vigesimal number normalization (the flagship)

Basque cardinals are **base-20**: `hogei` (20), `berrogei` (40 = 2×20),
`hirurogei` (60), `laurogei` (80). The numbers 30/50/70/90 are the preceding
twenty plus ten. The copulative `eta` ("and") contracts to `-ta` on the
twenties.

```python
from euskaphone.number_utils import BasqueNumberParser, normalize_numbers

p = BasqueNumberParser("eu")
p.cardinal(31)     # 'hogeita hamaika'   (20-and-11)
p.cardinal(1936)   # 'mila bederatziehun eta hogeita hamasei'
p.ordinal(16)      # 'hamaseigarren'

# case-suffixed numerals and clock time in running text (declension on the
# last element of the numeral phrase)
normalize_numbers("1936ko gerra", "eu")   # '… hogeita hamaseiko gerra'
normalize_numbers("20:00etan", "eu")      # 'hogeietan'
```

Every base form is cited to **Euskaltzaindia Araua 7** (cardinals) and
**Araua 18** (ordinals). Each is tagged attested-in-source vs derived-by-rule
in `euskaphone.number_utils` (the `ATTESTED` / `DERIVED` sets). Araua 7 records
`bost` (not `bortz`) for Zuberoa and most of Low Navarre, so euskaphone keeps
`bost` everywhere by default and offers the `bortz` series only for Lapurdian.
This avoids a wrong dialect swap. See [`docs/numbers.md`](docs/numbers.md).

### 2. Code-switch handling

Real Basque text embeds Spanish (Hegoalde), French (Iparralde), and, in the
tech/music/media register, English. Word-level detection identifies the
embedded material, classifies each contact word **per word** among
`es`/`fr`/`en`, and routes it through the orthography2ipa
`es-ES`/`fr-FR`/`en-US` lattice. It then **nativizes** the result onto the
Basque inventory: every foreign phone projects onto its nearest Basque phone,
never dropped, always projected. The `contact` parameter is `auto` (per-word
detection), `es`, `fr`, `en`, or `none`.

Detection prefers a small bundled **char-Markov language detector** (Basque,
Spanish, French, English, about 180 KB total, scored by `markovonnx`, install
with `euskaphone[langdetect]`). It falls back to an orthographic heuristic
when the models are unavailable. Basque is the in-language default: a word
routes out of Basque only when a foreign model beats the Basque model by a
clear margin. Short, plausibly-native words also need orthographic
corroboration, so a weak signal never misroutes a native word.

```python
ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu")
# '… plas̻a majoɾ …'  (Spanish routed + nativized: no θ, no stress)

ph.phonemize_sentence("Streaming plataforma berria erabili dugu.")
# 'strimin platafoɾma …'  (English routed + nativized onto the 5-vowel system)

ph.phonemize_sentence("Maison Rouge etxean.", "souletin")
# continental dialect → French contact by default
```

See [`docs/codeswitch.md`](docs/codeswitch.md).

### 3. Lexicon hook + shipped lexicons

`register_lexicon(dialect, source)` registers a proper-name/loan pronunciation
table (the orthography2ipa lexicon contract: a `word<TAB>ipa` path, URL, or
`hf://` id). A covered word bypasses the lattice.

Two lexicons ship built in: a curated **Euskaltzaindia toponym seed** (on by
default, `EuskaPhonemizer(toponyms=False)` to opt out) and an opt-in **HiTZ
proper-noun overlay** (`EuskaPhonemizer(lexicon="hitz")`) that carries a
benchmark circularity caveat. A caller's own lexicon always wins.
See [`docs/lexicons.md`](docs/lexicons.md).

### 4. Orthographic normalization

Before the lattice runs, everything written as a symbol, abbreviation, Roman
numeral or numeric date is spelled into Basque words
(`euskaphone.normalize.normalize_text`, wired in as the orthography2ipa
`normalize` stage):

```python
from euskaphone.normalize import normalize_text

normalize_text("XX. mendean %20 igo da", "eu")
# 'hogeigarren mendean ehuneko hogei igo da'
normalize_text("Luis XIV.a errege zen", "eu")     # '… hamalaugarrena …'
normalize_text("Sarrera €5eko da", "eu")          # '… bost euroko …'
normalize_text("15/01/2024", "eu")   # 'bi mila eta hogeita lauko urtarrilaren hamabostean'
```

The stage covers Roman-numeral ordinals (`XX.` → `hogeigarren`) and monarch
numerals (`Luis XIV.a` → `hamalaugarrena`), a cited abbreviation list
(`etab.` → `eta abar`), unit/currency/percent symbols with Basque word order
and declension (`%5` and `5%` both → `ehuneko bost`), and numeric dates. Each
is cited to Euskaltzaindia (Araua 18/37/196/197) and the EIMA *Ortotipografia*
guide. The abbreviation and unit tables are expandable data files
(`euskaphone/data/*.tsv`). See [`docs/normalization.md`](docs/normalization.md).

### 5. Northern Bizkaian pitch accent (opt-in)

The Getxo-Gernika and Lekeitio-Ondarroa varieties of Biscayan draw a *lexical*
accented/unaccented contrast, a system typologically close to Japanese and
studied in the prosodic-typology literature. `pitch_accent=True` (Biscayan
only) marks the lexically accented syllable of every attested word from a
76-entry lexicon cited to Hualde, to Egurtzegi & Elordieta, and to Hualde,
Elordieta & Elordieta (1994). Unknown words stay unmarked and are reported as
a distinct class: "not in the lexicon" never masquerades as "known
unaccented".

```python
ph.phonemize_sentence("Amuma etxean dago.", "biscayan",
                      contact="none", pitch_accent=True)
# 'aˈmuma etʃean daɡo'
```

See [`docs/pitch_accent.md`](docs/pitch_accent.md).

### 6. Accent forcing

`force_accent(text, dialect)` returns a target lect's own IPA for Batua text
(`mode="ipa"`), or a **verification-gated respelling** (`mode="respell"`) that
rewrites Batua orthography toward the target pronunciation and keeps an edit
only if the respelled text, read through the Batua lattice, measurably
approaches the target lect's IPA. Features Batua spelling cannot carry
(continental aspiration, Souletin front rounding) are rejected by the gate and
reported as a measured ceiling. See
[`docs/accent_forcing.md`](docs/accent_forcing.md).

### No homograph subsystem, by design

Basque orthography is near-phonemic: a grapheme's reading is essentially fixed
and sense-independent. Unlike tugaphone's Portuguese, which needs `bifonia` to
resolve heterophonic homographs, euskaphone ships **no** homograph stage. This
is a scope decision, documented so it is not mistaken for a gap.

## OVOS plugin

```python
from euskaphone.plugin import EuskaphoneG2PPlugin
EuskaphoneG2PPlugin("souletin").transcribe("kaixo mundua")
```

Registered under the `opm.g2p` entry-point group as `euskaphone`.

## How it measures up

euskaphone drives the shared orthography2ipa lattice, so its accuracy is the
accuracy of that lattice. These numbers measure the lattice, labelled by
source. Run them with `python scripts/benchmark.py [--hitz]`.

| gold | kind | figure |
|------|------|--------|
| orthography2ipa eu gold (166 rows, 8 lects) | **regression fixture** (same lattice made it) | PER `0.0000` (confirms the lattice is untouched, not a measure of accuracy) |
| [WikiPron](https://github.com/CUNY-CL/wikipron) `eus_latn` broad | independent word gold | PER `0.0749`, word-acc `0.4563` (full set, 20,115 words) |
| [HiTZ/EHU](https://huggingface.co/datasets/HiTZ/wikipedia_basque_ipa) Wikipedia G2P | independent cross-engine (Univ. of the Basque Country) | PER `0.1474` folded (full set, 836,491 sentences) |

The WikiPron and HiTZ figures are the informative ones: a pure lattice with no
lexicon, run on proper-name-heavy and raw-Wikipedia text, where transcription
conventions and multiple valid pronunciations account for much of the gap.
That gap is what the lexicon hook exists to close. Measured against
comparable open tools on the same full WikiPron set (segment-level protocol,
stress stripped, see `docs/benchmarks.md`): euskaphone scores PER `0.1009` /
word-acc `0.4298`, espeak-ng `eu` scores `0.1704` / `0.1750` (espyak, the
pure-Python espeak port, scores identically), and ahotts-g2p scores `0.3360` /
`0.0003` (ahotts's figure is dominated by its non-IPA symbol conventions).
**AhoTTS** covers Standard Batua only. **espeak-ng**'s `eu` voice is
single-dialect and rule-thin. euskaphone's contribution is the eight-lect
coverage, the sourced vigesimal numerals, and the code-switch nativization,
over a lattice shared across the whole Iberian family.

## License

Apache-2.0.
