# Quickstart

```bash
pip install euskaphone
```

```python
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()

# Standard Batua (default)
ph.phonemize_sentence("Kaixo, mundua.")            # 'kaiʃo mundua'

# a dialect, by code or alias
ph.phonemize_sentence("Hotza egiten du.", "souletin")
ph.phonemize_sentence("Hotza egiten du.", "eu-x-zuberera")   # same thing

# numbers are verbalized before the lattice runs
ph.phonemize_sentence("31 katu.")                  # 'hogeita hamaika katu'

# embedded Spanish/French is detected, routed and nativized
ph.phonemize_sentence("Plaza Mayor ikusi dut.", "eu")
```

Output is space-separated IPA, one group per word.

See [dialects.md](dialects.md), [numbers.md](numbers.md),
[codeswitch.md](codeswitch.md), [api.md](api.md),
[architecture.md](architecture.md), [benchmarks.md](benchmarks.md).
