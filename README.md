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
lexicons, pitch accent and accent forcing. The documentation starts at [docs/index.md](docs/index.md).

## Install

```bash
pip install --pre euskaphone
```

## Quickstart

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
print(ph.phonemize_sentence("Zazpi katu zuri ikusi ditut."))
# s̻as̻ˈpi kaˈtu s̻uˈɾi iˈkus̺i diˈtut
print(ph.phonemize_sentence("Hotza egiten dü.", "souletin"))
# ˈhots̻a eˈɣiten ˈdy
```

## Documentation

| Page | Content |
|------|---------|
| [Quickstart](docs/quickstart.md) | Install, extras, a first call in each dialect |
| [Dialects](docs/dialects.md) | The eight lects, their aliases and contact sides |
| [Numbers](docs/numbers.md) | The base-20 number system, ordinals and case endings |
| [Normalization](docs/normalization.md) | Numbers, dates, abbreviations, Roman numerals and symbols as words |
| [Code-switch](docs/codeswitch.md) | Spanish, French and English words in Basque text |
| [Lexicons](docs/lexicons.md) | Your own lexicon, the toponym seed and the HiTZ overlay |
| [Pitch accent](docs/pitch_accent.md) | Northern Bizkaian lexical accent marks |
| [Accent forcing](docs/accent_forcing.md) | Batua text as another dialect, as IPA or respelled text |
| [API](docs/api.md) | Every public name, including the G2P wrapper |
| [Architecture](docs/architecture.md) | The pipeline stages and the module map |
| [Benchmarks](docs/benchmarks.md) | The gold sets, the figures and the commands |

## License

Apache-2.0.
