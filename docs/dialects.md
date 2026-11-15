# Dialects

A euskaphone dialect is an orthography2ipa Basque lect spec. Selecting a
dialect selects that spec. The spec's grapheme table, allophony, and sandhi
produce the dialect's phonology directly, so there are no post-hoc accent
transforms.

| code | dialect (endonym) | side | aliases |
|------|-------------------|------|---------|
| `eu` | Euskara Batua (Standard) | n/a | `batua`, `standard` |
| `eu-biscayan` | Bizkaiera (Biscayan) | Hegoalde | `biscayan`, `western`, `vizcaino`, `eu-x-bizkaiera` |
| `eu-x-gipuzkoa` | Gipuzkera (Gipuzkoan) | Hegoalde | `guipuzcoan`, `central`, `eu-x-gipuzkera` |
| `eu-x-lapurdi` | Lapurtera (Lapurdian) | Iparralde | `labourdin`, `labortano`, `eu-x-lapurtera` |
| `eu-x-nafarra-garaia` | Goi-nafarrera (High Navarrese) | Hegoalde | `high-navarrese`, `alto-navarro` |
| `eu-x-nafarra-beherea` | Behe-nafarrera (Low Navarrese) | Iparralde | `low-navarrese`, `bajo-navarro` |
| `eu-x-zuberera` | Zuberera (Souletin) | Iparralde | `souletin`, `xiberotarra` |
| `eu-x-roncal` | Erronkariera (Roncalese, extinct) | Hegoalde | `roncalese`, `eu-x-erronkariera` |

The code column is the code orthography2ipa keys each spec by, and the one
`list_dialects()` and `resolve_lect()` return. The older `eu-x-*` codes in the
alias column still resolve to the same spec.

**Sides.** *Hegoalde* (peninsular, Spain) dialects default their code-switch
contact language to Spanish. *Iparralde* (continental, France) dialects
default to French. Resolution is case-insensitive and pops trailing subtags,
so an unknown `eu-x-*` falls back to Batua.

```python
from euskaphone.registry import resolve_lect, default_contact
resolve_lect("souletin")        # 'eu-x-zuberera'
default_contact("souletin")     # 'fr'
default_contact("biscayan")     # 'es'
```

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Numbers →](numbers.md)
