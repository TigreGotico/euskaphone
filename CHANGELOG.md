# Changelog

## Unreleased

- Code-switch: statistical char-Markov word-level language detector (Basque,
  Spanish, French, English), bundled as ~180 KB gzip-compressed models and used
  by default behind the unchanged `contact` API; the orthographic heuristic
  remains the fallback when the models or `markovonnx` are unavailable. Basque is
  the in-language default (margin threshold plus a high-frequency Basque
  function-word guard) so a weak signal never misroutes a native word.
  `scripts/train_langdetect.py` reproduces the models.

## 0.1.0a1

Initial release. Dialect-aware Basque (Euskara) text-to-IPA phonemizer over the
orthography2ipa lattice.

- Eight Basque lects (`eu` + seven `eu-x-*`), selectable by code or
  human-readable alias (`souletin`, `biscayan`, …).
- Vigesimal (base-20) cardinal/ordinal verbalization cited to Euskaltzaindia
  Araua 7/18, with an attested/derived provenance split; case-suffixed numerals
  and clock time in running text.
- Code-switch handling: Spanish/French embedded material detected, routed
  through the `es-ES`/`fr-FR` lattice and nativized onto the Basque inventory,
  with per-dialect-side defaults (`contact=auto|es|fr|none`).
- Lexicon hook (`register_lexicon`) for proper names/loans, empty by default.
- OVOS G2P plugin (`opm.g2p` entry point).
- No homograph subsystem — Basque orthography is near-phonemic (documented
  scope decision).
