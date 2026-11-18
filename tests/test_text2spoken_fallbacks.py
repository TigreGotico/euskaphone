"""The fallbacks that read what text2spoken leaves as written.

text2spoken reads first. A fallback reads only a form that text2spoken leaves
as written, and it goes when text2spoken reads that form. The guard tests below
turn red on the day text2spoken reads a fallback form: the fallback then comes
out, with its ``TODO(text2spoken issue: <CLASS>)`` marker.
"""
import importlib
import inspect
import re
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
    ("1 g-ko", "g-ko"),
    ("12:00", "12:00"),
    ("Bilera 10:30 da", "10:30"),
    ("100dik gora", "100dik"),
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
    # Araua 196 p.27: "K.a. (Kristo aurreko; Kristo aurretik)". The fallback
    # gives the form text2spoken reads for "K.a.", so the case changes nothing.
    ("k.a.", "Kristo aurreko."),
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
    # Araua 197 p.13: "1 s-eko iraupena (segundo bateko iraupena); Zenbat balio
    # du 1 kg-ek? (zenbat balio du kilogramo batek?)": the ending goes on "bat".
    ("1 g-ko", "gramo bateko"),
    ("1 h-ko iraupena", "ordu bateko iraupena"),
    ("1 g-k", "gramo batek"),
    ("1g-ko", "gramo bateko"),
    # Araua 203 p.49: "12:15 dira (hamabiak eta hamabost ...)": the hour takes
    # the plural article and "eta" joins the minutes. Note 34 on the same page
    # puts the part of the day first: "Arratsaldeko zazpiak eta hamar (7:10
    # p.m.)". text2spoken reads a time with a case ending in the same way.
    ("12:00", "eguerdiko hamabiak"),
    ("08:15", "goizeko zortziak eta hamabost"),
    ("7:05", "goizeko zazpiak eta bost"),
    ("23:59", "gaueko hamaikak eta berrogeita hemeretzi"),
    ("1:15", "goizeko ordu bata eta hamabost"),
    ("Hasiera: 18:30", "Hasiera: arratsaldeko seiak eta hogeita hamar"),
    ("Bilera 10:30 da", "Bilera goizeko hamarrak eta hogeita hamar da"),
    # Araua 203 p.38, note 32: "Ehun hitzaren kasuan, ehunetik da forma
    # estandarra, baina ehundik ere erabiltzen da, batez ere ehundik gora / 100dik
    # gora esapidean". text2spoken reads "100etik"; "100dik" keeps its "d".
    ("100dik gora", "ehundik gora"),
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
    ("k.a.", "K.a."),
    # Araua 203 p.7: "Olaizola II (irakurri: “olaizola bigarrena”)"
    ("Karlos V errege zen", "Karlos V.a errege zen"),
    # Araua 197 p.9: the number comes before the symbol.
    ("€5eko sarrera", "5 €-ko sarrera"),
    # Araua 197 p.13 writes "1 kg-ek" and "1 s-eko"; text2spoken reads "kg".
    ("1 kg-ko", "1 kg-ko"),
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


def test_one_gram_with_an_ending_has_the_shape_of_one_kilogram():
    # text2spoken reads "1 kg-ko" as "kilogramo bateko"; "g" must give the same shape.
    for ending in ["ko", "ek", "tik", "ra"]:
        assert (normalize.normalize_text(f"1 g-{ending}").replace("gramo", "kilogramo")
                == normalize.text2spoken_reading(f"1 kg-{ending}"))


CLOCK = re.compile(r"\d{1,2}:\d{2}")


@pytest.mark.parametrize("text", [
    "12:00", "08:15", "7:05", "23:59", "00:00", "24:00", "Hasiera: 18:30",
    "Bilera 10:30 da", "Ordutegia: 08:15.", "10:30-12:00", "(09:45)", "goizeko 10:30",
    "Bilera 10:30ean da", "20:00etan",
])
@pytest.mark.parametrize("lect", ["eu", "eu-x-lapurdi", "eu-x-bizkaiera"])
def test_no_clock_time_stays_unread(text, lect):
    # The lattice deletes digits, so a clock time left as written is silent.
    assert CLOCK.search(normalize.normalize_text(text, lect)) is None


# Araua 196 section 12 (p. 30): "Laburdura-puntua ez da puntuazio-marka bat;
# beraz, haren ondoren datorren hitza letra xehez hasita idazten da, non eta ez
# den izen berezi bat edo esaldiaren hasierako hitza." A capital after the stop
# starts a name or a sentence. Section 12.1 (p. 31) ends a sentence with "etab.":
# "musika klasikoa, etab." text2spoken keeps the stop before a capital for
# "etab." only, and the fallback reads each abbreviation in the same way.
@pytest.mark.parametrize("text,spoken", [
    ("h.d. Euskal Herrian", "hau da Euskal Herrian"),
    ("Ikus lib. Bilbon", "Ikus liburua Bilbon"),
    ("Ikus kap. Lehenengoa", "Ikus kapitulua Lehenengoa"),
    ("orr. Bilbon", "orrialdeak Bilbon"),
    ("Bilbo, ETAB. Gero", "Bilbo, eta abar. Gero"),
    # The end of the text ends the sentence.
    ("Ikus h.d.", "Ikus hau da."),
])
def test_an_abbreviation_keeps_its_stop_before_a_capital_only_where_a_sentence_ends(text, spoken):
    assert normalize.normalize_text(text) == spoken


@pytest.mark.parametrize("text,norm_writing", [
    ("Bilbo, ETAB. Gero", "Bilbo, etab. Gero"),
    ("k.a. Erroman", "K.a. Erroman"),
])
def test_the_stop_before_a_capital_matches_text2spoken(text, norm_writing):
    assert normalize.normalize_text(text) == normalize.text2spoken_reading(norm_writing)


@pytest.mark.parametrize("text,spoken", [
    ("Karlos V\neta", "Karlos bosgarrena\neta"),
    ("Karlos  V", "Karlos  bosgarrena"),
    ("Karlos\tV", "Karlos\tbosgarrena"),
    # A capital after the stop of "lib." starts a name, so no stop stays.
    ("lib.\nBilbon", "liburua\nBilbon"),
    ("h.d.\thori", "hau da\thori"),
    ("kap.\n3", "kapitulua\nhiru"),
    ("5 g\ngatz", "bost gramo\ngatz"),
    ("5\tg", "bost\tgramo"),
    ("1  g-ko", "gramo  bateko"),
])
def test_the_fallbacks_read_across_any_whitespace_and_keep_it(text, spoken):
    assert normalize.normalize_text(text) == spoken


# The mixed tokens of the review probe. text2spoken leaves a code as a name,
# and the lattice deletes the digits it cannot read, so euskaphone reads them.
PROBE_TOKENS = [
    "5G sarea", "4K bideoa", "MP3 fitxategia", "A4 orria", "F1 lasterketa",
    "COVID-19 gaixotasuna", "G7 bilera", "3D inprimagailua", "B12 bitamina", "3rd",
    "80ko hamarkada", "90eko hamarkadan", "1990eko hamarkadan", "2an", "3ak", "5ekoa",
    "10etik 20ra", "100dik gora", "3x3", "2+2", "5-10 urte", "10-15", "1/2", "50%",
    "%50", "5km", "5kg", "5 €", "€5", "5€", "24/7", "+34 943 123 456", "943123456",
    "2024ko", "1936an", "3. mailan", "2.a", "1.go", "H2O", "CO2", "N-1 errepidea",
    "AP-8 autobidea", "BI-631", "Euskal Herria 2030", "4x4 autoa", "1:0 irabazi",
    "2-1 galdu", "21:30ean", "12:00", "7.30etan", "0,5", "-5 gradu", "5º", "5ª", "1ºC",
    "25 °C", "10 m2", "5 m³", "x2", "v1.0", "iPhone 15", "Windows 11", "Bizkaia 2030ean",
]


def test_the_probe_has_all_63_tokens():
    assert len(PROBE_TOKENS) == len(set(PROBE_TOKENS)) == 63


@pytest.mark.parametrize("text", PROBE_TOKENS)
def test_no_digit_is_lost(text):
    assert re.search(r"\d", normalize.normalize_text(text)) is None


@pytest.mark.parametrize("text,spoken", [
    # The readings of the previous number stage: the digits read as a number in
    # their place, and the letters around them stay.
    ("5G sarea", "bostG sarea"),
    ("B12 bitamina", "Bhamabi bitamina"),
    ("H2O", "HbiO"),
    ("MP3 fitxategia", "MPhiru fitxategia"),
    ("v1.0", "vbat koma zero"),
    ("5º", "bostº"),
    # A hyphen in a code is no minus sign: text2spoken reads "N-1" as "N bat".
    ("AP-8 autobidea", "AP-zortzi autobidea"),
    ("BI-631", "BI-seiehun eta hogeita hamaika"),
    ("24/7", "hogeita lau/zazpi"),
    ("1:0 irabazi", "bat:zero irabazi"),
])
def test_the_digits_of_a_code_read_in_place(text, spoken):
    assert normalize.text2spoken_reading(text) == text
    assert normalize.normalize_text(text) == spoken


# Araua 196 p.32-33 (section 13) lets a sentence open with an abbreviation,
# which then takes a capital: "Testu normaletan, hobe litzateke esaldia laburdura
# batez ez hastea. Dena dela, estilo-hobespen bat besterik ez da".
CAPITALIZED = ["Adib.", "And.", "Etorb.", "Hurr.", "Id.", "Ik.", "Jn.", "K.", "Or.", "Pl.",
               "Tel.", "Zenb.", "Zk."]


@pytest.mark.parametrize("abbreviation", CAPITALIZED)
def test_a_capitalized_abbreviation_reads_as_text2spoken_reads_the_lower_case(abbreviation):
    lower = normalize.text2spoken_reading(f"{abbreviation.lower()} etxea")
    assert normalize.text2spoken_reading(f"{abbreviation} etxea") == f"{abbreviation} etxea"
    assert normalize.normalize_text(f"{abbreviation} etxea") == lower[0].upper() + lower[1:]


@pytest.mark.parametrize("text,spoken", [
    ("Jn. Agirre etorri da.", "Jauna Agirre etorri da."),
    ("Adib. etxea handia da.", "Adibidez etxea handia da."),
    ("Zk. 5", "Zenbakia bost"),
    ("Hori ikusi dugu. Ik. 25. orrialdea.", "Hori ikusi dugu. Ikus hogeita bosgarren orrialdea."),
    ("Tel.: 943", "Telefonoa: bederatziehun eta berrogeita hiru"),
    ("Hurr. orrialdean", "Hurrengoak orrialdean"),
    ("Jn.\nAgirre", "Jauna\nAgirre"),
    ("(Jn. Agirre)", "(Jauna Agirre)"),
])
def test_a_sentence_can_open_with_an_abbreviation(text, spoken):
    assert normalize.normalize_text(text) == spoken


@pytest.mark.parametrize("text", ["E.a. hori", "At. hori"])
def test_no_reading_for_an_uncited_abbreviation_with_a_capital(text):
    assert normalize.normalize_text(text) == text


def test_every_fallback_names_its_text2spoken_issue():
    # Each fallback comment and each misreading xfail names the URL of its
    # text2spoken issue. Until then they carry the marker, and this test fails.
    files = [*sorted((ROOT / "euskaphone").glob("*.py")), ROOT / "tests" / "text2spoken_gaps.py"]
    marked = [f"{path.relative_to(ROOT)}:{n}" for path in files
              for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
              if TODO in line]
    assert marked == []


ISSUE_URL = "https://github.com/TigreGotico/text2spoken/issues/"

# Each fallback and the text2spoken issue that holds the form it reads.
FALLBACK_ISSUES = [
    ("abbreviations", "LEFT_BY_TEXT2SPOKEN", 265),
    ("normalize", "read_bare_clock_times", 267),
    ("normalize", "read_capitalized_abbreviations", 265),
    ("number_utils", "read_space_grouped_numbers", 148),
    ("number_utils", "read_garren_ordinals", 263),
    ("number_utils", "read_dot_decimals", 264),
    ("number_utils", "read_glued_case_endings", 273),
    ("romans", "read_bare_monarch_numerals", 266),
    ("units", "read_currency_before_number", 268),
    ("units", "LEFT_BY_TEXT2SPOKEN", 269),
]


def _documentation(module_name, name):
    # A function carries the URL in its docstring, a constant in the "#:" lines
    # right above its assignment.
    module = importlib.import_module(f"euskaphone.{module_name}")
    obj = getattr(module, name)
    if callable(obj):
        return inspect.getdoc(obj) or ""
    lines = inspect.getsource(module).splitlines()
    start = next(n for n, line in enumerate(lines) if re.match(rf"{name}\b\s*[:=]", line))
    comments = []
    for line in reversed(lines[:start]):
        if not line.startswith("#:"):
            break
        comments.append(line)
    return "\n".join(comments)


@pytest.mark.parametrize("module_name,name,issue", FALLBACK_ISSUES)
def test_a_fallback_cites_its_text2spoken_issue(module_name, name, issue):
    urls = re.findall(rf"{re.escape(ISSUE_URL)}(\d+)", _documentation(module_name, name))
    assert urls == [str(issue)]


def test_every_issue_url_in_the_package_has_a_fallback_row():
    found = sorted((path.stem, int(number))
                   for path in (ROOT / "euskaphone").glob("*.py")
                   for number in re.findall(rf"{re.escape(ISSUE_URL)}(\d+)",
                                            path.read_text(encoding="utf-8")))
    assert found == sorted((module_name, issue) for module_name, _, issue in FALLBACK_ISSUES)
