# Code-switch handling

Real Basque text is bilingual, and increasingly trilingual: peninsular
(Hegoalde) writing embeds Spanish, continental (Iparralde) writing embeds French,
and the modern tech/music/media register on both sides embeds English — proper
names, loans, quoted fragments, product and band names. euskaphone detects that
material at the word level, classifies each contact word among `es`/`fr`/`en`,
transcribes it through the orthography2ipa `es-ES`/`fr-FR`/`en-US` lattice, and
**nativizes** the result onto the Basque phoneme inventory.

## Total nativization

Following arbtok's principle — *never drop a segment, always project it* — every
foreign phone maps to its nearest Basque phone rather than being deleted.

Romance (Spanish/French):

```
θ → s̻    v → b    z → s̻    ʒ → ʃ    ɔ → o    ɛ → e    y → i (kept in Souletin)
ʁ,ʀ → r   χ → x    ø,œ,ə → e   nasal vowels → their oral counterpart
```

English (adapted through the same five-vowel, no-interdental phonology; the
mapping follows the documented loanword-adaptation pattern for Basque anglicisms
and, where the literature is silent, is stated as a convention):

```
θ → t    ð → d    w → u̯    ɫ → l    ɹ,ɻ → r    ŋ → n    dʒ → tʃ
æ,ʌ → a  ɒ → o    ɪ → i    ʊ → u    ɜ,ɝ,ə → e   eɪ→ei aɪ→ai aʊ→au oʊ→o
```

Length marks, stress and liaison are stripped, so a contact word comes out in the
same notation as the surrounding Basque.

## The `contact` parameter

| value | behaviour |
|-------|-----------|
| `"auto"` (default) | detect contact words and classify each **per word** among `es`/`fr`/`en`; unclassified words fall to the dialect's side (peninsular→`es`, continental→`fr`) |
| `"es"` / `"fr"` / `"en"` | force that contact lattice for detected words |
| `"none"` | disable switching; transcribe everything as Basque |

```python
ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu")       # es
ph.phonemize_sentence("Streaming plataforma berria erabili dugu.")   # en (auto)
ph.phonemize_sentence("Plaza Mayor eta le weekend.", "eu")           # es + fr + en
ph.phonemize_sentence("Maison Rouge etxean.", "souletin")            # fr (auto)
ph.phonemize_sentence("Plaza Mayor.", "eu", contact="none")          # all Basque
```

## The detection heuristic (and its limits)

A token is treated as contact-language if it carries a letter Basque does not use
natively (`c q v w y ñ ç` or a Romance accented vowel), an English digraph absent
from native spelling (`th sh wh ck gh oo ee aw`), or is one of a small set of
common Spanish/French/English function words. Per-word classification then routes
it (English signals first, then the Spanish/French accent split, then the
dialect's side). Sequences that occur natively in Basque (`ea` in *etxean*, `ing`
in *inguru*) are deliberately excluded so the signal never fires on a Basque word.
This is deliberately shallow and kept far simpler than arbtok. It is **not** a
language identifier — a loan spelled with only Basque-legal letters (e.g. `plaza`)
is not flagged and falls through to the Basque lattice, which would project it
onto the same inventory anyway. Nothing is ever dropped.

When the statistical detector below is available it drives the per-word
language choice and the heuristic serves as its backstop: for **short** tokens
(under six letters) the detector's foreign verdict needs orthographic
corroboration, so native forms like `jan` or `bada` are never misrouted. If
the detector cannot load, the heuristic alone routes.

## The statistical detector (default when models are present)

The orthographic heuristic misses the loans and internationalisms spelled with
Basque-legal letters (`plaza`, `general`, `estazio`) and cannot tell Spanish
embedding from French. euskaphone therefore ships a small statistical detector:
four **character-level Markov models** — one each for Basque, Spanish, French and
English — trained on Wikipedia and stored gzip-compressed under
`euskaphone/data/langdetect/` (about 40–50 KB each, ~180 KB for all four). A word
is scored under all four models and the model that assigns the lowest perplexity
wins. The detector is scored by [`markovonnx`](https://github.com/TigreGotico/markovonnx);
it is an optional dependency (`pip install euskaphone[langdetect]`). Without it,
the code falls back to the orthographic heuristic — the routing decision behind
`contact="auto"`/`"es"`/`"fr"` is unchanged, so there is no API break.

### Threshold policy — in-language default (null beats wrong)

Basque is the surrounding language, so it is the default. A word is routed **out**
of Basque only when a foreign model beats the Basque model by at least a fixed
margin (`DEFAULT_MARGIN = 0.25` nats-per-character of log-perplexity). Below that
margin the word stays `eu`: a weak, ambiguous signal never misroutes a native
word. Two extra guards keep the default honest:

* a short **allowlist of high-frequency Basque grammar words** (`dut`, `ditut`,
  `da`, `ez`, `kaixo`, …) is always kept Basque — encyclopedic training text
  underrepresents conversational grammar, so a char-model can misjudge a short
  function word on its letter shape alone;
* an empty or all-punctuation token is Basque by default.

The genuinely ambiguous shared-alphabet internationalisms (`hotel`, `general`,
`radio`, `hospital`) sit near the Basque boundary. Some fall inside the margin
band and stay Basque (`radio`); others are orthographically more Romance/English
and route to a contact language — where **total nativization** projects them back
onto the Basque inventory anyway, so either outcome is safe. The margin only
guarantees the decision is never taken on a weak signal.

```python
from euskaphone.langdetect import get_detector
d = get_detector()                 # None if markovonnx/models unavailable
d.detect("ayuntamiento")           # ('es', {...})  -> routed and nativized
d.detect("dut")                    # ('eu', {})     -> native grammar word, kept
d.detect("radio")                  # ('eu', {...})  -> inside the margin band
d.is_contact("monsieur")           # True
```

### How the models were built, and how they measure up

The models are character n-gram chains of **order 2** (evaluated against order 3;
order 2 both classifies better on this word-level task and is 5–8× smaller).
Training text is one Wikipedia shard per language (~3 M characters each),
normalized to NFC, lower-cased and stripped to alphabetic words wrapped with
word-boundary sentinels. `scripts/train_langdetect.py` reproduces them.

On a held-out set of 800 words per language (from Wikipedia articles disjoint
from training, each word absent from that language's training vocabulary), the
Basque-vs-contact routing decision compares as follows:

| detector | precision | recall | F1 | accuracy |
|----------|-----------|--------|----|----------|
| char-Markov (order 2, margin 0.20) | 0.919 | 0.690 | 0.788 | 0.722 |
| char-Markov (order 2, margin 0.30) | 0.922 | 0.618 | 0.740 | 0.674 |
| orthographic heuristic | 0.878 | 0.575 | 0.695 | 0.621 |

The detector's default margin (0.25) sits between the two Markov rows; the Basque
function-word guard lifts native retention further on conversational text than
this encyclopedic set shows. The Markov detector roughly halves the heuristic's
missed contact words (recall 0.69 vs 0.58) while keeping contact precision higher
(0.92 vs 0.88) — i.e. it catches many more real loans **and** misroutes fewer
native words. The four-way confusion is dominated by the expected
Spanish/French/English overlap (shared Romance/Latin alphabet); Basque separates
cleanly from all three.
