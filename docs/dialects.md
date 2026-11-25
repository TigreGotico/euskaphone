# Dialects

<!-- agent-hint
covers: which dialects euskaphone selects and how a name resolves to a lect code
source: euskaphone/registry.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/dialects.md
see: quickstart.md, codeswitch.md, api.md
-->

A euskaphone dialect is an orthography2ipa Basque lect spec. Selecting a
dialect selects that spec. The grapheme table, the allophony and the sandhi of the spec
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

```python
from euskaphone.registry import list_dialects, resolve_lect

list_dialects()
# ['eu', 'eu-biscayan', 'eu-x-gipuzkoa', 'eu-x-lapurdi', 'eu-x-nafarra-beherea', 'eu-x-nafarra-garaia', 'eu-x-roncal', 'eu-x-zuberera']
resolve_lect("vizcaino")
# 'eu-biscayan'
resolve_lect("eu-x-lapurtera")
# 'eu-x-lapurdi'
```

**Sides.** *Hegoalde* (peninsular, Spain) dialects default their code-switch
contact language to Spanish. *Iparralde* (continental, France) dialects
default to French. Resolution is case-insensitive and takes the nearest lect,
so an unknown `eu-x-*` falls back to Batua.

```python
from euskaphone.registry import default_contact

default_contact("souletin")
# 'fr'
default_contact("biscayan")
# 'es'
```

---
[← Quickstart](quickstart.md) · [Index](index.md) · [Numbers →](numbers.md)
