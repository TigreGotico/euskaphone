# Accent forcing

<!-- agent-hint
covers: how force_accent turns Batua text into a target dialect, and where the respeller stops
source: euskaphone/accent.py, scripts/respell_gains.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/accent_forcing.md && diff <(.venv/bin/python scripts/respell_gains.py 2>/dev/null | grep -oP '^eu\S*\s+\K[0-9.]+\s+[0-9.]+\s+[0-9.]+' | tr -s ' ' | sort) <(grep -oP '^\| \x60eu[^\x60]*\x60 \| \K[0-9.]+ \| [0-9.]+ \| \**[0-9.]+' docs/accent_forcing.md | tr -d '*|' | tr -s ' ' | sort)
see: dialects.md, api.md
-->

`force_accent(text, dialect, mode=...)` pushes Batua text toward a target
lect in one of two modes.

## `mode="ipa"`: the direct view

The text is transcribed straight through the target lect's lattice, so the
return is the target dialect's own IPA, the "IPA delta" against Batua.

In Biscayan seseo, the laminal `/s̻/` has merged into the apical `/s̺/`:

```python
from euskaphone.accent import force_accent

force_accent("Zazpi katu zuri", "biscayan", mode="ipa")
# 's̺as̺pi katu s̺uɾi'
```

## `mode="respell"`: the verification-gated respeller

The same verification-gated respeller architecture tugaphone uses for
Portuguese. It rewrites the **Batua orthography** using Basque spelling
conventions that push a *Batua reader* toward the target pronunciation
(`z`→`s` for the peninsular seseo merger, `il`→`ill` for palatalisation,
`h`-insertion for continental aspiration, `u`→`ü` for Souletin front
rounding). Every candidate edit is **verification-gated**:

> an edit is kept only if re-transcribing the respelled text *through the
> base (Batua) lattice* moves the result measurably closer (lower PER) to
> the target lect's own IPA.

The edit `z` to `s` survives the gate, because a Batua reading of the respelled text
matches Biscayan:

```python
force_accent("Zazpi katu zuri", "biscayan", mode="respell")
# 'Zaspi katu suri'
```

The `respell_report(...)` call exposes the full accounting, `per_before`,
`per_after`, `gain`, and which rules the gate `accepted`, for benchmarking:

```python
from euskaphone.accent import respell_report

report = respell_report("Zazpi katu zuri", "biscayan")
report.accepted
# ['seseo_z_to_s']
round(report.per_before, 4), round(report.per_after, 4)
# (0.1875, 0.0625)
```

## Why the gate matters: the honest ceiling

The gate is what keeps respelling honest. It never invents an orthography
whose Batua reading does not actually approximate the target. Batua has a
**silent `h`** and **no `ü`**, so continental aspiration and Souletin front
rounding are simply **not recoverable** through the Batua lattice. The gate
rejects those edits, and the measured gain for those features is about 0.
That is a real ceiling, reported rather than hidden.

The `scripts/respell_gains.py` benchmark runs the respeller over the 26
Batua gold sentences of the orthography2ipa `eu` gold for every lect. One run
gives:

| dialect | PER before | PER after | gain | surviving rules |
|---------|-----------:|----------:|-----:|-----------------|
| `eu-biscayan` | 0.0522 | 0.0166 | **0.0356** | `seseo_z_to_s` |
| `eu-x-gipuzkoa` | 0.0000 | 0.0000 | 0.0000 | none (identical to Batua) |
| `eu-x-lapurdi` | 0.0191 | 0.0191 | 0.0000 | none (aspiration unrecoverable) |
| `eu-x-nafarra-garaia` | 0.0191 | 0.0191 | 0.0000 | none |
| `eu-x-nafarra-beherea` | 0.0191 | 0.0191 | 0.0000 | none |
| `eu-x-zuberera` | 0.0191 | 0.0191 | 0.0000 | none (aspiration + front rounding) |
| `eu-x-roncal` | 0.0191 | 0.0191 | 0.0000 | none |

The one clear win is peninsular **seseo**, where respelling `z`→`s` cuts the
Batua-reading PER against Biscayan to about a third. The continental dialects sit at
their honest ceiling: the delta from Batua is aspiration and front
rounding, neither of which the Batua orthography can carry, so the gate
keeps nothing. Regenerate the table with:

```bash
python scripts/respell_gains.py
```

---
[← Pitch accent](pitch_accent.md) · [Index](index.md) · [API →](api.md)
