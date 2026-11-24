# euskaphone

<!-- agent-hint
covers: what euskaphone does, how to install it, a first phonemization in each dialect and where each feature is documented
source: pyproject.toml, euskaphone/__init__.py, euskaphone/lattice_core.py, euskaphone/registry.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py README.md
see: docs/index.md, docs/quickstart.md, AGENTS.md
-->

euskaphone turns Basque (Euskara) text into IPA for eight dialects. It drives the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) pronunciation lattice and adds
the stages that orthography2ipa leaves to the caller: number and date reading, code-switch handling,
lexicons, pitch accent and accent forcing.

euskaphone is the Basque sibling of [tugaphone](https://github.com/TigreGotico/tugaphone)
(Portuguese). Every rule and every number form cites its source, so researchers and
speech-technology teams can inspect the pipeline.

A dialect is an orthography2ipa Basque lect spec. The spec's grapheme table,
allophony, and cross-word sandhi produce the dialect's phonology directly: the
apical/laminal sibilant contrast, the affricates, Souletin aspiration, and
`/y/`. The documentation starts at [docs/index.md](docs/index.md).

## Install

```bash
pip install --pre euskaphone
```

The `--pre` flag selects the alpha line that these pages describe. The `langdetect` extra
(`pip install --pre "euskaphone[langdetect]"`) adds the statistical code-switch detector, and the
`test` extra adds the test dependencies.

## Quickstart

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
ph.phonemize_sentence("Zazpi katu zuri ikusi ditut.")
# 's̻as̻ˈpi kaˈtu s̻uˈɾi iˈkus̺i diˈtut'
```

The [quickstart](docs/quickstart.md) walks through each option. Without a dialect, the phonemizer reads Standard Basque (Batua). Souletin keeps the aspirated
`h`, and a written `ü` gives `/y/`:

```python
ph.phonemize_sentence("Hotza egiten du gaur mendian.", "souletin")
# 'ˈhots̻a eˈɣiten ˈdu ˈɡau̯r menˈdian'
ph.phonemize_sentence("Hotza egiten dü.", "souletin")
# 'ˈhots̻a eˈɣiten ˈdy'
```

## Dialects

Eight lects, selectable by BCP-47 code or by a human-readable alias. The code
column is the code orthography2ipa keys the spec by, which `list_dialects()` and
`resolve_lect()` return. The older `eu-x-*` codes in the alias column still
resolve.

| code | dialect | aliases |
|------|---------|---------|
| `eu` | Standard Basque | `batua`, `standard` |
| `eu-biscayan` | Biscayan | `biscayan`, `western`, `eu-x-bizkaiera` |
| `eu-x-gipuzkoa` | Gipuzkoan | `guipuzcoan`, `central`, `eu-x-gipuzkera` |
| `eu-x-lapurdi` | Lapurdian | `labourdin`, `eu-x-lapurtera` |
| `eu-x-nafarra-garaia` | High Navarrese | `high-navarrese` |
| `eu-x-nafarra-beherea` | Low Navarrese | `low-navarrese` |
| `eu-x-zuberera` | Souletin | `souletin`, `xiberotarra` |
| `eu-x-roncal` | Roncalese (†) | `roncalese`, `eu-x-erronkariera` |

## What euskaphone adds

### 1. Vigesimal number normalization (the flagship)

Basque cardinals are **base-20**: `hogei` (20), `berrogei` (40 = 2×20),
`hirurogei` (60), `laurogei` (80). The numbers 30/50/70/90 are the preceding
twenty plus ten. The copulative `eta` ("and") contracts to `-ta` on the
twenties.

```python
from euskaphone.normalize import normalize_text
from euskaphone.number_utils import BasqueNumberParser

p = BasqueNumberParser("eu")
p.cardinal(31)
# 'hogeita hamaika'
p.cardinal(1936)
# 'mila bederatziehun eta hogeita hamasei'
p.ordinal(16)
# 'hamaseigarren'
```

In running text, the case ending goes on the last element of the numeral phrase:

```python
normalize_text("1936ko gerra", "eu")
# 'mila bederatziehun eta hogeita hamaseiko gerra'
normalize_text("20:00etan", "eu")
# 'arratsaldeko zortzietan'
```

Every base form is cited to **Euskaltzaindia Araua 7** (cardinals) and
**Araua 18** (ordinals). Araua 7 records `bost` (not `bortz`) for Zuberoa and
most of Low Navarre, so `BasqueNumberParser` keeps `bost` everywhere and spells
the `bortz` series only for Lapurdian. This avoids a wrong dialect swap.
text2spoken reads the numbers of running text, and it reads every lect as
Batua. See [`docs/numbers.md`](docs/numbers.md).

### 2. Code-switch handling

Real Basque text embeds Spanish (Hegoalde), French (Iparralde), and, in the
tech/music/media register, English. Word-level detection identifies the
embedded material, classifies each contact word **per word** among
`es`/`fr`/`en`, and routes it through the orthography2ipa
`es-ES`/`fr-FR`/`en-US` lattice. It then **nativizes** the result onto the
Basque inventory: every foreign phone projects onto its nearest Basque phone,
never dropped, always projected. The `contact` parameter is `none` (the
default, no switching), `auto` (per-word detection), `es`, `fr` or `en`.
Switching is opt-in: on the WikiPron Basque word list, `auto` scores PER
0.1271 against 0.1147 for `none` (see [`docs/benchmarks.md`](docs/benchmarks.md)).

Detection prefers a small bundled **char-Markov language detector** (Basque,
Spanish, French, English, about 180 KB total, scored by `markovonnx`, install
with `euskaphone[langdetect]`). It falls back to an orthographic heuristic
when the models are unavailable. Basque is the in-language default: a word
routes out of Basque only when a foreign model beats the Basque model by a
clear margin. Short, plausibly-native words also need orthographic
corroboration, so a weak signal never misroutes a native word.

Spanish `Mayor` is routed to the Spanish lattice and nativized, so it carries no stress mark.
English `Streaming` goes onto the five-vowel system. A continental dialect such as Souletin
routes to French by default.

```python
ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu", contact="auto")
# 'maˈðɾilen plaˈs̻a majoɾ iˈkus̺i ˈdut'
ph.phonemize_sentence("Streaming plataforma berria erabili dugu.", contact="auto")
# 'strimin platafoɾma beˈria eˈɾaβili duˈɣu'
ph.phonemize_sentence("Maison Rouge etxean.", "souletin", contact="auto")
# 'mes̻o ˈrowɣe eˈtʃean'
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

Before the lattice runs, everything written as a number, a symbol, an
abbreviation, a Roman numeral or a numeric date is spelled into Basque words
(`euskaphone.normalize.normalize_text`, wired in as the orthography2ipa
`expand` stage). [text2spoken](https://github.com/TigreGotico/text2spoken)
reads the text first, and euskaphone reads the forms it leaves as written:

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

text2spoken reads Roman-numeral ordinals (`XX.` → `hogeigarren`) and monarch
numerals (`Luis XIV.a` → `hamalaugarrena`), abbreviations (`etab.` →
`eta abar`), unit/currency/percent symbols with Basque word order and
declension (`%5` and `5%` both → `ehuneko bost`), clock times and numeric dates.
euskaphone reads what text2spoken leaves as written, such as `€5eko`,
`16garren`, `Karlos V` and the unit symbol `g`. Each reading is cited to
Euskaltzaindia (Araua 18/35/196/197/203). The abbreviation and unit tables are
data files (`euskaphone/data/*.tsv`). See
[`docs/normalization.md`](docs/normalization.md).

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
ph.phonemize_sentence("Amuma etxean dago.", "biscayan", contact="none", pitch_accent=True)
# 'aˈmuma etʃean daɣo'
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

## G2P wrapper

```python
from euskaphone.plugin import EuskaphoneG2PPlugin
EuskaphoneG2PPlugin("souletin").transcribe("kaixo mundua")
# 'ˈkai̯ʃo munˈdua'
EuskaphoneG2PPlugin("souletin", contact="auto").transcribe("Maison Rouge etxean.")
# 'mes̻o ˈrowɣe eˈtʃean'
```

`EuskaphoneG2PPlugin(lang="eu", contact="none")` is a class with the
orthography2ipa plugin shape. euskaphone declares no entry point, so neither
orthography2ipa nor an OVOS plugin manager discovers it: import and construct it
yourself.

## How it measures up

euskaphone drives the shared orthography2ipa lattice, so its accuracy is the
accuracy of that lattice. These numbers measure the lattice, labelled by
source. Run them with `python scripts/benchmark.py [--hitz]`.

| gold | kind | figure |
|------|------|--------|
| orthography2ipa eu gold (166 rows, 8 lects) | **regression fixture** (same lattice made it) | PER `0.0000` (confirms the lattice is untouched, not a measure of accuracy) |
| [WikiPron](https://github.com/CUNY-CL/wikipron) `eus_latn` broad | independent word gold | PER `0.1147`, word-acc `0.2802` (full set, 20,115 words, `contact="none"`) |
| [HiTZ/EHU](https://huggingface.co/datasets/HiTZ/wikipedia_basque_ipa) Wikipedia G2P | independent cross-engine (Univ. of the Basque Country) | PER `0.1474` folded (full set, 836,491 sentences) |

Much of the WikiPron error is notation. WikiPron writes no stress and no
spirants. The scorer strips stress, but the Basque spec writes the spirant
allophones `β ð ɣ` of `/b d g/`, and each one counts as an error. Bare
orthography2ipa `eu` scores PER `0.1146` and word accuracy `0.2802` on the
20,115 rows. With `β ð ɣ` folded to `b d ɡ`, the same output scores PER
`0.0749` and word accuracy `0.4563`.

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
