# Code-switch handling

Real Basque text is bilingual: peninsular (Hegoalde) writing embeds Spanish,
continental (Iparralde) writing embeds French — proper names, loans, quoted
fragments. euskaphone detects that material at the word level, transcribes it
through the orthography2ipa `es-ES`/`fr-FR` lattice, and **nativizes** the result
onto the Basque phoneme inventory.

## Total nativization

Following arbtok's principle — *never drop a segment, always project it* — every
foreign phone maps to its nearest Basque phone rather than being deleted:

```
θ → s̻    v → b    z → s̻    ʒ → ʃ    ɔ → o    ɛ → e    y → i (kept in Souletin)
ʁ,ʀ → r   χ → x    ø,œ,ə → e   nasal vowels → their oral counterpart
```

Stress marks and liaison are stripped, so a contact word comes out in the same
notation as the surrounding Basque.

## The `contact` parameter

| value | behaviour |
|-------|-----------|
| `"auto"` (default) | detect contact words, route through the dialect's side (peninsular→`es`, continental→`fr`) |
| `"es"` / `"fr"` | force that contact lattice for detected words |
| `"none"` | disable switching; transcribe everything as Basque |

```python
ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu")     # es
ph.phonemize_sentence("Maison Rouge etxean.", "souletin")          # fr (auto)
ph.phonemize_sentence("Plaza Mayor.", "eu", contact="none")        # all Basque
```

## The detection heuristic (and its limits)

A token is treated as contact-language if it carries a letter Basque does not use
natively (`c q v w y ñ ç` or a Romance accented vowel) or is one of a small set
of very common Spanish/French function words. This is deliberately shallow and
kept far simpler than arbtok: it catches the proper names and loans that actually
break a Basque TTS voice. It is **not** a language identifier — a Spanish loan
spelled with only Basque-legal letters (e.g. `plaza`) is not flagged and falls
through to the Basque lattice, which would project it onto the same inventory
anyway. Nothing is ever dropped.
