# Northern Bizkaian pitch accent

<!-- agent-hint
covers: what the Northern Bizkaian pitch accent layer marks and how to switch it on
source: euskaphone/pitch_accent.py, euskaphone/data/pitch_accent/northern_bizkaian.tsv
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/pitch_accent.md
see: dialects.md, api.md
-->

Standard Batua has predictable, post-lexical word prominence. The
**Northern Bizkaian** dialects of Biscayan, the varieties of
Getxo-Gernika and Lekeitio-Ondarroa-Markina, do not: they draw a *lexical*
distinction between **accented** and **unaccented** words, a system
typologically close to Japanese (a lexical accented/unaccented contrast, a
phrase-initial rise, no durational correlate of accent). This property is
studied in the prosodic-typology literature, and euskaphone annotates it as
an opt-in layer on top of the shared lattice.

## The two lexical classes

* **Accented** words contain an accented root or a pre-accenting affix, so
  one lexically fixed syllable carries a **H\*+L** pitch accent (a fall from
  a high tone). The accented class is populated by old Latin/Romance
  loanwords (`ántzar` < *ánser* 'goose', `kipúla` < *cepúlla* 'onion',
  `ganbára` < *cambra* 'attic'), opaque and transparent accented compounds
  (`bélarri` 'ear', `egúzki` 'sun', `burúgogor` 'stubborn', `begígorri`
  'red-eyed'), and words carrying pre-accenting suffixes (plural
  `-ak`/`-e-`, comparative `-ago`, and others).
* **Unaccented** words, most native stems and singular affixes, show no
  word-level prominence. They acquire only a *derived* accent on the final
  syllable when standing phrase-finally (immediately before the verb):
  `lagune` 'the friend' is unaccented, surfacing as `laguné` only in that
  position.

Sources: Hualde (1997, 1999), Hualde, Elordieta & Elordieta (1994, *The
Basque Dialect of Lekeitio*), and Egurtzegi & Elordieta, *A history of the
Basque prosodic systems* (section 3.1, the Western system). Every lexicon
entry names its source.

## Marking convention

The layer is **annotation-level, not synthesis**: it does not predict F0, it
marks *which* syllable bears the lexical accent.

* an **accented** word receives a single mark, U+02C8 `ˈ`, placed
  immediately before its lexically accented syllable (`amúma` → `aˈmuma`,
  `makíla` → `maˈkila`)
* an **unaccented** word returns **unmarked**
* an **unknown** word, not attested in the lexicon, is *also* unmarked, but
  its class is `AccentClass.UNKNOWN`, kept deliberately distinct from
  `UNACCENTED`. "Not in the lexicon" never masquerades as "known to bear no
  accent"

The mark denotes the accented syllable (the H\*+L target). It is not a
claim about stress or F0 shape.

## Usage

In the first example, `amuma` is accented and the other words stay unmarked. `mahaia` is not
attested, so its class is `UNKNOWN`.

```python
from euskaphone import EuskaPhonemizer, default_lexicon

ph = EuskaPhonemizer()
ph.phonemize_sentence("Amuma etxean dago.", "biscayan", contact="none", pitch_accent=True)
# 'aˈmuma etʃean daɣo'

lex = default_lexicon()
lex.lookup("kipula").accent_class.name
# 'ACCENTED'
lex.lookup("kipula").accent_syllable
# 2
lex.lookup("lagun").accent_class.name
# 'UNACCENTED'
lex.lookup("mahaia").accent_class.name
# 'UNKNOWN'
```

`pitch_accent=True` is defined **only** for Biscayan (`eu-biscayan`, also
reached as `eu-x-bizkaiera` or `biscayan`). Any other lect raises `ValueError`. Annotation is word-level,
so cross-word sandhi does not apply in this mode. That is the cost of
surfacing the lexical accent per word.

## Coverage

The shipped lexicon documents only attested, cited words of the Northern
Bizkaian sub-area: 76 entries (62 accented, 14 unaccented), each naming its
source:

```python
from euskaphone.pitch_accent import AccentClass

entries = default_lexicon().entries()
len(entries)
# 76
sum(e.accent_class is AccentClass.ACCENTED for e in entries)
# 62
sum(e.accent_class is AccentClass.UNACCENTED for e in entries)
# 14
```

The Getxo-Gernika items come from Egurtzegi & Elordieta and Hualde
(1997, 1999), and the Lekeitio items come from Hualde, Elordieta &
Elordieta (1994) section 2.8.1 (loanword accent, compounds, and the
singular/plural minimal pairs). Everything else is unmarked by default and
reported as `UNKNOWN`. The lexicon is a seed to extend from the primary
sources, not a claim of full coverage.

---
[← Lexicons](lexicons.md) · [Index](index.md) · [Accent forcing →](accent_forcing.md)
