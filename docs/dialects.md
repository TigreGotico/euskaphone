# Dialects

A euskaphone dialect is an orthography2ipa Basque lect spec. Selecting a
dialect selects that spec. The spec's grapheme table, allophony, and sandhi
produce the dialect's phonology directly, so there are no post-hoc accent
transforms.

| code | dialect (endonym) | side | aliases |
|------|-------------------|------|---------|
| `eu` | Euskara Batua (Standard) | n/a | `batua`, `standard` |
| `eu-x-bizkaiera` | Bizkaiera (Biscayan) | Hegoalde | `biscayan`, `western`, `vizcaino` |
| `eu-x-gipuzkera` | Gipuzkera (Gipuzkoan) | Hegoalde | `guipuzcoan`, `central` |
| `eu-x-lapurtera` | Lapurtera (Lapurdian) | Iparralde | `labourdin`, `labortano` |
| `eu-x-nafarra-garaia` | Goi-nafarrera (High Navarrese) | Hegoalde | `high-navarrese`, `alto-navarro` |
| `eu-x-nafarra-beherea` | Behe-nafarrera (Low Navarrese) | Iparralde | `low-navarrese`, `bajo-navarro` |
| `eu-x-zuberera` | Zuberera (Souletin) | Iparralde | `souletin`, `xiberotarra` |
| `eu-x-erronkariera` | Erronkariera (Roncalese, extinct) | Hegoalde | `roncalese` |

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
