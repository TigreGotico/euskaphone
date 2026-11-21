"""Orthographic normalization: abbreviations, Roman numerals, units, dates.

Everything written as a symbol, abbreviation, Roman numeral or numeric date is
spelled into Basque words before the pronunciation lattice runs. text2spoken
reads these forms, and euskaphone reads the forms it leaves as written, such as
a currency symbol before the number.
"""
from euskaphone.normalize import normalize_text

samples = [
    "XX. mendea",                       # Roman ordinal-period -> hogeigarren mendea
    "Karlos V.a errege zen",            # monarch -> bosgarrena
    "Liburuak, aldizkariak, etab.",     # abbreviation -> eta abar.
    "Prezioa %20 igo da",               # percent -> ehuneko hogei
    "Sarrera €5eko da",                 # currency + declension -> bost euroko
    "Etxea 3 km-ra dago",               # unit -> hiru kilometrora
    "15/01/2024",                       # numeric date -> ...urtarrilaren hamabosta
]

for s in samples:
    print(f"{s:32s} -> {normalize_text(s, 'eu')}")
