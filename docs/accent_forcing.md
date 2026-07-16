# Accent forcing

`force_accent(text, dialect, mode=...)` pushes Batua text toward a target lect in
one of two modes.

## `mode="ipa"` — the direct view

The text is transcribed straight through the target lect's lattice, so the return
is the target dialect's own IPA — the "IPA delta" against Batua.

```python
from euskaphone.accent import force_accent
force_accent("Zazpi katu zuri", "biscayan", mode="ipa")
# 's̺as̺pi katu s̺uɾi'   (Biscayan seseo: laminal /s̻/ has merged into apical /s̺/)
```

## `mode="respell"` — the verification-gated respeller

Ported from tugaphone's accent-forcing architecture. It rewrites the **Batua
orthography** using Basque spelling conventions that push a *Batua reader* toward
the target pronunciation (`z`→`s` for the peninsular seseo merger, `il`→`ill` for
palatalisation, `h`-insertion for continental aspiration, `u`→`ü` for Souletin
front rounding). Every candidate edit is **verification-gated**:

> an edit is kept only if re-transcribing the respelled text *through the base
> (Batua) lattice* moves the result measurably closer (lower PER) to the target
> lect's own IPA.

```python
force_accent("Zazpi katu zuri", "biscayan", mode="respell")
# 'Zaspi katu suri'   (z→s survives the gate: a Batua reading now matches Biscayan)
```

The `respell_report(...)` call exposes the full accounting — `per_before`,
`per_after`, `gain`, and which rules the gate `accepted` — for benchmarking.

## Why the gate matters: the honest ceiling

The gate is what keeps respelling honest. It never invents an orthography whose
Batua reading does not actually approximate the target. Batua has a **silent `h`**
and **no `ü`**, so continental aspiration and Souletin front rounding are simply
**not recoverable** through the Batua lattice — the gate rejects those edits, and
the measured gain for those features is ~0. That is a real ceiling, reported
rather than hidden.

The `scripts/respell_gains.py` benchmark runs the respeller over the 20 Batua
gold sentences for every lect. A representative run:

| dialect | PER before | PER after | gain | surviving rules |
|---------|-----------:|----------:|-----:|-----------------|
| `eu-x-bizkaiera` | 0.0373 | 0.0185 | **0.0188** | `seseo_z_to_s` |
| `eu-x-gipuzkera` | 0.0000 | 0.0000 | 0.0000 | — (identical to Batua) |
| `eu-x-lapurtera` | 0.0212 | 0.0212 | 0.0000 | — (aspiration unrecoverable) |
| `eu-x-nafarra-garaia` | 0.0212 | 0.0212 | 0.0000 | — |
| `eu-x-nafarra-beherea` | 0.0212 | 0.0212 | 0.0000 | — |
| `eu-x-zuberera` | 0.0212 | 0.0212 | 0.0000 | — (aspiration + front rounding) |
| `eu-x-erronkariera` | 0.0212 | 0.0212 | 0.0000 | — |

The one clear win is peninsular **seseo**, where respelling `z`→`s` halves the
Batua-reading PER against Biscayan. The continental dialects sit at their honest
ceiling: the delta from Batua is aspiration and front rounding, neither of which
the Batua orthography can carry, so the gate keeps nothing. Regenerate the table
with:

```bash
python scripts/respell_gains.py
```
