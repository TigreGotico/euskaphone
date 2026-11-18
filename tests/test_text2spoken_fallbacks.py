"""The fallbacks that read what text2spoken leaves as written.

text2spoken reads first. A fallback reads only a form that text2spoken leaves
as written, and it goes when text2spoken reads that form. The guard tests below
turn red on the day text2spoken reads a fallback form: the fallback then comes
out, with its ``TODO(text2spoken issue: <CLASS>)`` marker.
"""
import warnings
from pathlib import Path

import pytest

from euskaphone import normalize

ROOT = Path(__file__).parent.parent
TODO = "TODO(text2spoken issue"

# Forms that text2spoken leaves as written, with the written part it keeps.
LEFT_AS_WRITTEN = [
    ("16garren postua", "16garren"),
    ("1 000 000 lagun", "1 000 000"),
    ("2.5", "2.5"),
    ("h.d. hori", "h.d."),
    ("kap. 3", "kap."),
    ("lib. 2", "lib."),
    ("orr. 5", "orr."),
    ("ETAB.", "ETAB."),
    ("k.a.", "k.a."),
    ("Karlos V", "Karlos V"),
    ("€5eko sarrera", "€5eko"),
    ("5g", "5g"),
    *[(f"5 {unit}", f" {unit}") for unit in ["dm", "g", "mg", "t", "ml", "cl", "h"]],
]


@pytest.mark.parametrize("text,kept", LEFT_AS_WRITTEN)
def test_text2spoken_still_leaves_the_fallback_form(text, kept):
    # Red here means text2spoken reads the form: remove its fallback.
    assert kept in normalize.text2spoken_reading(text)


# The reading euskaphone gives each form. The number words are those of
# test_number_utils (Araua 7 and Araua 18), the abbreviations those of
# data/abbreviations.tsv (Araua 196 p.40-42), the unit words those of
# data/units.tsv (Araua 197). A sentence-final abbreviation keeps one period
# (Araua 196 p.31).
FALLBACK_READINGS = [
    ("1garren", "lehenengo"),
    ("16garren postua", "hamaseigarren postua"),
    ("10garrena.", "hamargarrena."),
    ("1 000 000 lagun", "milioi bat lagun"),
    ("2 500 metro", "bi mila eta bostehun metro"),
    ("2.5", "bi koma bost"),
    ("h.d. hori", "hau da hori"),
    ("h.d.", "hau da."),
    ("kap. 3", "kapitulua hiru"),
    ("lib.", "liburua."),
    ("orr.", "orrialdeak."),
    ("ETAB.", "eta abar."),
    ("Katuak, ETAB., gero", "Katuak, eta abar, gero"),
    ("k.a.", "Kristo aurretik."),
    ("Karlos V", "Karlos bosgarrena"),
    ("Luis XIV", "Luis hamalaugarrena"),
    ("Karlos V.", "Karlos bosgarrena."),
    ("€5eko sarrera", "bost euroko sarrera"),
    ("Sarrera €5eko da", "Sarrera bost euroko da"),
    ("5 dm", "bost dezimetro"),
    ("5 g", "bost gramo"),
    ("5 mg", "bost miligramo"),
    ("5 t", "bost tona"),
    ("5 ml", "bost mililitro"),
    ("5 cl", "bost zentilitro"),
    ("5 h", "bost ordu"),
    ("5g", "bost gramo"),
    ("5 g-ko", "bost gramoko"),
    # "bat" (one) follows the unit word, as it does in text2spoken's "kilogramo bat".
    ("1 g", "gramo bat"),
    ("1 g.", "gramo bat."),
]


@pytest.mark.parametrize("text,spoken", FALLBACK_READINGS)
def test_the_fallback_reads_what_text2spoken_leaves(text, spoken):
    assert normalize.text2spoken_reading(text) != spoken
    with warnings.catch_warnings():
        # The reading path calls no deprecated reader.
        warnings.simplefilter("error", DeprecationWarning)
        assert normalize.normalize_text(text) == spoken
    # Text that is already spelled out comes through unchanged.
    assert normalize.normalize_text(spoken) == spoken


# A writing that the norm marks as wrong, or that text2spoken does not read,
# reads as text2spoken reads the norm's writing of the same thing.
@pytest.mark.parametrize("text,norm_writing", [
    # Araua 203 p.24: "(desegokia) bi. edo 2garren"; "(egokia) bigarren edo 2."
    ("16garren postua", "16. postua"),
    # Araua 203 p.12: "36 524; 256 089; 1 000 000"
    ("1 000 000 lagun", "1.000.000 lagun"),
    # Araua 203 p.14: "Euskaraz, koma da markatzaile dezimala"
    ("2.5", "2,5"),
    # Araua 196 p.27: the abbreviation follows the case of the words it stands for.
    ("ETAB.", "etab."),
    # Araua 203 p.7: "Olaizola II (irakurri: “olaizola bigarrena”)"
    ("Karlos V errege zen", "Karlos V.a errege zen"),
    # Araua 197 p.9: the number comes before the symbol.
    ("€5eko sarrera", "5 €-ko sarrera"),
])
def test_the_fallback_matches_text2spoken_on_the_norm_writing(text, norm_writing):
    assert normalize.normalize_text(text) == normalize.text2spoken_reading(norm_writing)


@pytest.mark.parametrize("text,form,reading", [
    ("16garren postua", "16garren", "hamaseigarren"),
    ("1 000 000 lagun", "1 000 000", "milioi bat"),
    ("2.5 kilo", "2.5", "bi koma bost"),
    ("h.d. hori", "h.d.", "hau da"),
    ("Karlos V errege zen", "Karlos V", "Karlos bosgarrena"),
    ("€5eko sarrera", "€5eko", "bost euroko"),
    ("5 g gatz", "5 g", "bost gramo"),
])
def test_text2spoken_reading_wins_over_a_fallback(monkeypatch, text, form, reading):
    # The day text2spoken reads a fallback form, its reading stands and the
    # fallback has nothing left to rewrite.
    read = normalize.text2spoken_reading

    def reads_the_form(text, dialect="eu"):
        return read(text.replace(form, reading), dialect)

    monkeypatch.setattr(normalize, "text2spoken_reading", reads_the_form)
    assert normalize.normalize_text(text) == text.replace(form, reading)


@pytest.mark.parametrize("text", ["g letra", "a, b eta g", "h hizkia", "5 metro eta g"])
def test_a_unit_symbol_with_no_number_before_it_stays(text):
    # A unit symbol is a unit only right after digits, so no fallback reads it.
    assert normalize.normalize_text(text) == normalize.text2spoken_reading(text)
    assert normalize.normalize_text(text) == text.replace("5", "bost")


@pytest.mark.parametrize("text,spoken", [
    ("ad. hori", "ad. hori"),
    ("e.a.", "e.a."),
    ("at.", "at."),
])
def test_no_fallback_for_a_wrong_or_uncited_abbreviation(text, spoken):
    # Araua 196 p.44: "ad. aditza", not "adibidez". No opened source defines
    # "e.a." or "at.".
    assert normalize.normalize_text(text) == spoken
    assert normalize.text2spoken_reading(text) == spoken


def test_every_fallback_names_its_text2spoken_issue():
    # Each fallback comment and each misreading xfail names the URL of its
    # text2spoken issue. Until then they carry the marker, and this test fails.
    files = [*sorted((ROOT / "euskaphone").glob("*.py")), ROOT / "tests" / "text2spoken_gaps.py"]
    marked = [f"{path.relative_to(ROOT)}:{n}" for path in files
              for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
              if TODO in line]
    assert marked == []
