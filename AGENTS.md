# euskaphone: agent guide

`euskaphone` is a Python package that turns Basque (Euskara) text into IPA for eight dialects. It drives the orthography2ipa lattice, and it adds number and date reading, code-switch handling, lexicons, pitch accent and accent forcing.

The documentation starts at [docs/index.md](docs/index.md).

## Repository map

| Path | Holds |
|---|---|
| `euskaphone/lattice_core.py`, `euskaphone/__init__.py` | The orthography2ipa engine wiring, `EuskaPhonemizer` and `register_lexicon` |
| `euskaphone/registry.py` | Lect codes, aliases and the contact side of each lect |
| `euskaphone/normalize.py` | `normalize_text`: text2spoken first, then the fallbacks |
| `euskaphone/number_utils.py`, `units.py`, `romans.py`, `abbreviations.py` | The fallbacks for forms that text2spoken leaves as written |
| `euskaphone/dates.py`, `numverbal.py` | Deprecated stages and spelled-number helpers |
| `euskaphone/codeswitch.py`, `langdetect.py` | Contact-word routing, nativization and the char-Markov detector |
| `euskaphone/lexicons.py`, `pitch_accent.py`, `accent.py`, `plugin.py` | The toponym seed and HiTZ overlay, pitch accent, accent forcing and the G2P wrapper |
| `euskaphone/data/` | Abbreviation and unit tables, lexicons, detector models, the pitch accent lexicon |
| `docs/`, `examples/`, `tests/`, `scripts/` | Documentation, runnable scripts, tests, benchmarks and `check_docs_examples.py` |

## Setup and tests

```bash
unset VIRTUAL_ENV
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

Use uv, never pip. The `test` extra installs `markovonnx`, and the `langdetect` extra installs it for users. `tests/test_examples.py` runs every script in `examples/`.

## Hard rules

1. A dialect is an orthography2ipa lect spec. Dialect phonology comes from the spec, and euskaphone adds no accent transform after transcription ([architecture.md](docs/architecture.md)).
2. text2spoken reads the text first. A fallback reads only a form that text2spoken leaves as written, and `tests/test_text2spoken_fallbacks.py` requires each fallback to name its text2spoken issue ([normalization.md](docs/normalization.md#how-the-text-is-read)).
3. A misreading by text2spoken gets a strict xfail mark in `tests/text2spoken_gaps.py`, never a fallback. The mark comes off when text2spoken reads the form as cited ([normalization.md](docs/normalization.md#lapurdian-bortz)).
4. The stages that text2spoken replaces are deprecated. They keep their behaviour and give a `DeprecationWarning` that names the replacement ([normalization.md](docs/normalization.md#deprecated-stages)).
5. A code-switch rule holds under both classifiers, the detector and the orthographic fallback. `tests/conftest.py` runs such a test twice ([codeswitch.md](docs/codeswitch.md)).
6. Abbreviations and units live in `euskaphone/data/abbreviations.tsv` and `units.tsv`, not in code. The header of each file names its sources ([normalization.md](docs/normalization.md#the-data-tables)).
7. The benchmarks run with `EuskaPhonemizer(toponyms=False)`, so each figure measures the pure lattice ([benchmarks.md](docs/benchmarks.md)).
8. The HiTZ overlay is opt-in, and the benchmark drops every row that holds an overlay key ([lexicons.md](docs/lexicons.md)).
9. A page example carries its output in the comment under it, and `scripts/check_docs_examples.py` compares the two.
10. The release workflow writes `euskaphone/version.py` and `CHANGELOG.md`. Do not edit either.

## Before you push

1. Run the full test suite.
2. If you changed `README.md` or `docs/`, run the example check:

```bash
.venv/bin/python scripts/check_docs_examples.py README.md docs/*.md
```

3. A page you add goes in the table of `docs/index.md`, gets an `agent-hint` comment after its H1, and ends with a footer that links the previous page, the index and the next page.

`dev` is the work branch and `master` is the stable branch.
