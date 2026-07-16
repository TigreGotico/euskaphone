# Northern Bizkaian pitch accent

Standard Batua has predictable, post-lexical word prominence. The **Northern
Bizkaian** dialects of Biscayan — the varieties of Getxo–Gernika and
Lekeitio–Ondarroa–Markina — do not: they draw a *lexical* distinction between
**accented** and **unaccented** words, a system typologically close to Japanese
(a lexical accented/unaccented contrast, a phrase-initial rise, no durational
correlate of accent). This is the property that makes the sub-area a landmark in
the prosodic-typology literature, and euskaphone annotates it as an opt-in layer
on top of the shared lattice.

## The two lexical classes

* **Accented** words contain an accented root or a pre-accenting affix, so one
  lexically fixed syllable carries a **H\*+L** pitch accent (a fall from a high
  tone). The accented class is populated by old Latin/Romance loanwords
  (`ántzar` < *ánser* 'goose', `kipúla` < *cepúlla* 'onion', `ganbára` <
  *cambra* 'attic'), opaque and transparent accented compounds (`bélarri`
  'ear', `egúzki` 'sun', `burúgogor` 'stubborn', `begígorri` 'red-eyed'), and
  words carrying pre-accenting suffixes (plural `-ak`/`-e-`, comparative `-ago`,
  …).
* **Unaccented** words — most native stems and singular affixes — show no
  word-level prominence. They acquire only a *derived* accent on the final
  syllable when standing phrase-finally (immediately before the verb): `lagune`
  'the friend' is unaccented, surfacing as `laguné` only in that position.

Sources: Hualde (1997, 1999); Hualde, Elordieta & Elordieta (1994, *The Basque
Dialect of Lekeitio*); Egurtzegi & Elordieta, *A history of the Basque prosodic
systems* (§3.1, the Western system). Every lexicon entry names its source.

## Marking convention

The layer is **annotation-level, not synthesis**: it does not predict F0, it
marks *which* syllable bears the lexical accent.

* an **accented** word receives a single mark — U+02C8 `ˈ` — placed immediately
  before its lexically accented syllable (`amúma` → `aˈmuma`, `makíla` →
  `maˈkila`);
* an **unaccented** word is returned **unmarked**;
* an **unknown** word — not attested in the lexicon — is *also* unmarked, but its
  class is `AccentClass.UNKNOWN`, kept deliberately distinct from `UNACCENTED`.
  "Not in the lexicon" never masquerades as "known to bear no accent".

The mark denotes the accented syllable (the H\*+L target); it is not a claim
about stress or F0 shape.

## Usage

```python
from euskaphone import EuskaPhonemizer, default_lexicon, AccentClass

ph = EuskaPhonemizer()
ph.phonemize_sentence("Amuma etxean dago.", "biscayan",
                      contact="none", pitch_accent=True)
# 'aˈmuma etʃean daɡo'   (amúma accented; the rest unmarked)

lex = default_lexicon()
lex.lookup("kipula").accent_class        # AccentClass.ACCENTED
lex.lookup("kipula").accent_syllable     # 2
lex.lookup("lagun").accent_class         # AccentClass.UNACCENTED
lex.lookup("mahaia").accent_class        # AccentClass.UNKNOWN (not attested)
```

`pitch_accent=True` is defined **only** for Biscayan (`eu-x-bizkaiera` /
`biscayan`); any other lect raises `ValueError`. Annotation is word-level, so
cross-word sandhi is not applied in this mode — the honest cost of surfacing the
lexical accent per word.

## Coverage

Honest and small: the shipped lexicon documents only the attested, cited words
of the Northern Bizkaian sub-area (10 accented, 4 unaccented). Everything else
is unmarked-by-default and reported as `UNKNOWN`. The lexicon is a seed to be
extended from the primary sources, not a claim of full coverage.
