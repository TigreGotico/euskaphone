# Quickstart

```bash
pip install euskaphone
```

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()

# Standard Batua (default)
ph.phonemize_sentence("Kaixo, mundua.")            # 'kai̯ˈʃo munˈdua'

# a dialect, by code or alias
ph.phonemize_sentence("Hotza egiten du.", "souletin")
ph.phonemize_sentence("Hotza egiten du.", "eu-x-zuberera")   # same thing

# numbers are verbalized (hogeita hamaika) before the lattice runs
ph.phonemize_sentence("31 katu.")                  # 'oˈɣei̯ta aˈmai̯ka kaˈtu'

# code-switching is opt-in: contact="auto" detects, routes and nativizes
# embedded Spanish/French/English words
ph.phonemize_sentence("Plaza Mayor ikusi dut.", "eu", contact="auto")
# 'plaˈs̻a majoɾ iˈkus̺i ˈdut'   (Mayor routed to Spanish)
```

Output is space-separated IPA, one group per word.

See [dialects.md](dialects.md), [numbers.md](numbers.md),
[normalization.md](normalization.md), [codeswitch.md](codeswitch.md),
[lexicons.md](lexicons.md), [pitch_accent.md](pitch_accent.md),
[accent_forcing.md](accent_forcing.md), [api.md](api.md),
[architecture.md](architecture.md), [benchmarks.md](benchmarks.md).

---
[Home](../README.md) · [Dialects →](dialects.md)
