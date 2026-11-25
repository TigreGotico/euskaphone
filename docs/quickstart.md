# Quickstart

<!-- agent-hint
covers: how to install euskaphone and phonemize a sentence in Batua, in a dialect, with numbers and with code-switching
source: pyproject.toml, euskaphone/__init__.py, euskaphone/lattice_core.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/quickstart.md
see: dialects.md, numbers.md, codeswitch.md, api.md
-->

Install euskaphone and turn a Basque sentence into IPA. Each step shows its real output.

```bash
pip install --pre euskaphone
```

The `--pre` flag selects the alpha line that these pages describe. The `langdetect` extra
(`pip install --pre "euskaphone[langdetect]"`) adds the statistical code-switch detector, and the
`test` extra adds the test dependencies. Create one phonemizer and call
`phonemize_sentence`. Without a dialect, it reads Standard Basque (Batua):

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
ph.phonemize_sentence("Kaixo, mundua.")
# 'kai̯ˈʃo munˈdua'
```

The output is space-separated IPA, one group per word. Pass a dialect as the second argument, by
lect code or by alias. Both names below select the same spec:

```python
ph.phonemize_sentence("Hotza egiten du.", "souletin")
# 'ˈhots̻a eˈɣiten ˈdu'
ph.phonemize_sentence("Hotza egiten du.", "eu-x-zuberera")
# 'ˈhots̻a eˈɣiten ˈdu'
```

A written `ü` selects `/y/` in Souletin, and Souletin keeps the aspirated `h`:

```python
ph.phonemize_sentence("Hotza egiten du gaur mendian.", "souletin")
# 'ˈhots̻a eˈɣiten ˈdu ˈɡau̯r menˈdian'
ph.phonemize_sentence("Hotza egiten dü.", "souletin")
# 'ˈhots̻a eˈɣiten ˈdy'
ph.phonemize_sentence("Zazpi katu zuri ikusi ditut.")
# 's̻as̻ˈpi kaˈtu s̻uˈɾi iˈkus̺i diˈtut'
```

Numbers become Basque words before the lattice runs. Here `31` reads as `hogeita hamaika`:

```python
ph.phonemize_sentence("31 katu.")
# 'oˈɣei̯ta aˈmai̯ka kaˈtu'
```

Code-switching is off by default, so a Spanish word reads as Basque. With `contact="auto"`,
euskaphone detects the embedded word, routes it to the Spanish lattice and nativizes the result:

```python
ph.phonemize_sentence("Plaza Mayor ikusi dut.", "eu")
# 'plaˈs̻a maˈor iˈkus̺i ˈdut'
ph.phonemize_sentence("Plaza Mayor ikusi dut.", "eu", contact="auto")
# 'plaˈs̻a majoɾ iˈkus̺i ˈdut'
```

---
[Index](index.md) · [Dialects →](dialects.md)
