# euskaphone documentation

<!-- agent-hint
covers: the reading order of every documentation page of euskaphone
source: docs/
generated: no
verify: diff <(ls docs/*.md | xargs -n1 basename | grep -v '^index.md$' | sort) <(grep -oP '^\| \[[^]]*\]\(\K[a-z_]+\.md' docs/index.md | sort)
see: README.md, AGENTS.md
-->

euskaphone turns Basque text into IPA for eight dialects. Start with the quickstart.
The pages below follow the reading order, from the first call to the internals and the benchmarks.

| Page | What you get from it |
|---|---|
| [Quickstart](quickstart.md) | Install the package and phonemize a first sentence in each dialect |
| [Dialects](dialects.md) | The eight lect codes, their aliases and the contact side of each |
| [Numbers](numbers.md) | How Basque numbers read: the base-20 system, ordinals, case endings and clock times |
| [Normalization](normalization.md) | How numbers, dates, abbreviations, Roman numerals and symbols become Basque words |
| [Code-switch](codeswitch.md) | How Spanish, French and English words inside Basque text get detected and nativized |
| [Lexicons](lexicons.md) | Register a pronunciation table, and the toponym seed and HiTZ overlay that ship |
| [Pitch accent](pitch_accent.md) | The opt-in Northern Bizkaian lexical accent marks |
| [Accent forcing](accent_forcing.md) | Turn Batua text into a target dialect as IPA or as respelled text |
| [API](api.md) | Every public name with its signature and default |
| [Architecture](architecture.md) | The stages of the pipeline and the module that owns each |
| [Benchmarks](benchmarks.md) | The gold sets, the figures, and the commands that reproduce them |
