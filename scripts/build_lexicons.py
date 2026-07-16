"""Regenerate euskaphone's shipped lexicons.

Two lexicons are produced, both validated with
:func:`orthography2ipa.lexicon.validate_lexicon_text` before writing:

1. ``euskaphone/data/lexicons/eu_toponyms.tsv`` — a curated seed of the most
   important Basque toponyms and respelled exonyms in their Euskaltzaindia
   normative forms. For a regular normative spelling the IPA is taken from the
   Batua lattice on that spelling (the entry pins the normative
   pronunciation); for an irregular / foreign-spelled entry an explicit IPA is
   given in ``_EXPLICIT``.

   Source of the normative forms: Euskaltzaindiaren Onomastikaren Datu-Basea
   (EODA, https://www.euskaltzaindia.eus/eoda), the Academy's onomastics
   database, and the Academy's exonym recommendations (arau 145/163). EODA is a
   query-only public web service with no bulk-download endpoint and no explicit
   open-data licence, so nothing is scraped: only the normative spellings — the
   Academy's official, non-copyrightable facts about place names — are
   transcribed here, each recoverable from the EODA search UI.

2. ``euskaphone/data/lexicons/eu_hitz_overlay.tsv`` — an OPT-IN overlay whose
   keys are proper nouns drawn from the HiTZ/EHU ``wikipedia_basque_ipa`` set.
   Because that set is also euskaphone's independent cross-engine benchmark
   (``scripts/benchmark.py``), any benchmark row containing an overlay key MUST
   be excluded from the benchmark when the overlay is active — otherwise the
   lexicon would be graded against the very data it was drawn from. The
   benchmark harness reads this file to build that exclusion set.

Run: ``python scripts/build_lexicons.py [--hitz]`` (``--hitz`` rebuilds the
overlay, which needs network access to the HiTZ dataset).
"""
import argparse
import os

from orthography2ipa.lexicon import validate_lexicon_text
from euskaphone import EuskaPhonemizer

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "..", "euskaphone", "data", "lexicons")

# --- Toponym seed ---------------------------------------------------------

#: Regular normative Basque place names — IPA comes from the Batua lattice.
#: Grouped only for readability; order within the file is alphabetical.
_REGULAR = [
    # Capitals / cities (Hego Euskal Herria)
    "Bilbo", "Gasteiz", "Donostia", "Iruñea", "Tutera", "Lizarra",
    # Territories and regions
    "Bizkaia", "Gipuzkoa", "Araba", "Nafarroa", "Lapurdi", "Zuberoa",
    "Euskadi", "Euskal Herria", "Iparralde", "Hegoalde",
    # Bizkaia
    "Barakaldo", "Portugalete", "Santurtzi", "Getxo", "Leioa", "Basauri",
    "Galdakao", "Durango", "Bermeo", "Gernika", "Lekeitio", "Ondarroa",
    "Mungia", "Sopela", "Plentzia", "Gorliz", "Balmaseda", "Sestao",
    "Amorebieta", "Erandio", "Arrigorriaga",
    # Gipuzkoa
    "Errenteria", "Irun", "Eibar", "Arrasate", "Bergara", "Tolosa",
    "Hondarribia", "Zarautz", "Beasain", "Zumarraga", "Legazpi", "Hernani",
    "Lasarte", "Andoain", "Pasaia", "Oiartzun", "Elgoibar", "Mutriku",
    "Deba", "Zumaia", "Getaria", "Orio", "Usurbil", "Azpeitia", "Azkoitia",
    "Oñati", "Bergara",
    # Araba / Nafarroa
    "Laudio", "Amurrio", "Agurain", "Laguardia",
    "Zangoza", "Agoitz", "Altsasu", "Bera", "Leitza", "Elizondo",
    # Iparralde
    "Baiona", "Angelu", "Miarritze", "Hendaia", "Uztaritze", "Kanbo",
    "Maule", "Atharratze", "Donibane Garazi", "Donapaleu", "Hazparne",
    "Ziburu", "Donibane Lohizune", "Sara", "Ainhoa",
    # Natural features
    "Gorbeia", "Aizkorri", "Anboto", "Aralar", "Jaizkibel", "Ernio",
    "Nerbioi", "Ibaizabal", "Urumea", "Bidasoa", "Aiako Harria",
    # Respelled exonyms (Basque orthography, lattice-regular)
    "Madril", "Bartzelona", "Iruña", "Errioxa", "Kantabria", "Gaztela",
    "Frantzia", "Espainia", "Erresuma Batua", "Alemania", "Italia",
    "Erroma", "Lisboa", "Bordele", "Paue", "Tolosa Okzitania",
]

#: Irregular / foreign-spelled entries — explicit nativized IPA (word<TAB>ipa).
#: These keep a non-Basque spelling in running Basque text, so the lattice would
#: mis-read them; the IPA is the accepted Basque-adapted pronunciation.
_EXPLICIT = {
    "new": "niu",          # "New York" etc. (first element; whole-word key)
    "york": "jork",
    "washington": "u̯asinton",
    "münchen": "muntʃen",
    "zürich": "s̻uɾik",
    "wall": "u̯al",
    "street": "estɾit",
    "liverpool": "libeɾpul",
    "cambridge": "kambɾitʃ",
    "hollywood": "oliu̯ud",
}


def _build_toponyms() -> str:
    ph = EuskaPhonemizer()
    entries = {}
    for name in _REGULAR:
        # Multi-word normative forms are pinned per whole surface word: a
        # lexicon is word-keyed, so split and pin each Basque word.
        for word in name.split():
            key = word.lower()
            if key in entries:
                continue
            ipa = ph.phonemize_sentence(word, "eu", contact="none").strip()
            if ipa:
                entries[key] = ipa
    for key, ipa in _EXPLICIT.items():
        entries.setdefault(key, ipa)
    lines = [f"{k}\t{entries[k]}" for k in sorted(entries)]
    return "\n".join(lines) + "\n"


# --- HiTZ overlay ---------------------------------------------------------

def _build_hitz_overlay(sample: int = 40) -> str:
    """Curated proper-noun overlay drawn from HiTZ wikipedia_basque_ipa.

    Keys are the most frequent capitalised (proper-noun) tokens in the set; the
    IPA is the Batua lattice reading of the token. The point of the overlay is
    the OPT-IN + benchmark-exclusion mechanism, not accuracy: because the keys
    come from the benchmark set, the harness drops every benchmark row that
    contains one when the overlay is active (see the module docstring).
    """
    from collections import Counter
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq

    path = hf_hub_download("HiTZ/wikipedia_basque_ipa",
                           "data/train-00000-of-00002.parquet",
                           repo_type="dataset")
    rows = pq.read_table(path).slice(0, 40000).to_pylist()
    # A proper noun stays capitalised *mid-sentence*; a sentence-initial
    # capital is just orthography. Count only tokens at position > 0, and keep a
    # word only if it is (almost) never seen lowercased — i.e. genuinely a name.
    cap: Counter = Counter()
    low: Counter = Counter()
    for r in rows:
        toks = [t.strip(".,;:()\"'«»¿?!—").strip() for t in r["text"].split()]
        for i, core in enumerate(toks):
            if len(core) <= 3 or not core.isalpha():
                continue
            if core[0].isupper() and core[1:].islower():
                if i > 0:
                    cap[core] += 1
            elif core.islower():
                low[core] += 1
    counts: Counter = Counter({
        w: n for w, n in cap.items() if low.get(w.lower(), 0) <= n // 4
    })
    ph = EuskaPhonemizer()
    entries = {}
    for word, _ in counts.most_common():
        key = word.lower()
        if key in entries:
            continue
        ipa = ph.phonemize_sentence(word, "eu", contact="none").strip()
        if ipa:
            entries[key] = ipa
        if len(entries) >= sample:
            break
    lines = [f"{k}\t{entries[k]}" for k in sorted(entries)]
    return "\n".join(lines) + "\n"


def _write(name: str, text: str) -> None:
    problems = validate_lexicon_text(text)
    if problems:
        raise SystemExit(f"{name}: invalid lexicon\n" +
                         "\n".join(f"  line {n}: {why}" for n, why in problems))
    os.makedirs(_DATA, exist_ok=True)
    dest = os.path.join(_DATA, name)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {dest} ({text.count(chr(10))} entries)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hitz", action="store_true",
                    help="also rebuild the HiTZ overlay (needs network)")
    args = ap.parse_args()
    _write("eu_toponyms.tsv", _build_toponyms())
    if args.hitz:
        _write("eu_hitz_overlay.tsv", _build_hitz_overlay())


if __name__ == "__main__":
    main()
