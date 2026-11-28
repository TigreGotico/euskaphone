"""Readings where text2spoken differs from the value that a test cites.

Each mark names one class of misreading of a form that text2spoken reads, and
the text2spoken issue for it. euskaphone has no fallback for these: text2spoken
fixes them. A strict xfail turns red when text2spoken gives the cited reading,
so the mark comes off.
"""
import pytest


def _misreading(reason: str):
    return pytest.mark.xfail(strict=True, reason=reason, raises=AssertionError)


LAPURDI_LECT = _misreading(
    "text2spoken reads the Lapurdian lect 'eu-x-lapurdi' as Batua: '15' gives 'hamabost'. Araua 7: "
    "'Bost zenbakiaren aldaera bortz da, Iparraldeko zenbait hizkeratan erabilia.' "
    "https://github.com/TigreGotico/text2spoken/issues/262")

ROMAN_MONTH_DAY_FIRST = _misreading(
    "text2spoken reads the day and the year of '15-I-2024' and '7/III/1995' and keeps the Roman month as "
    "written: 'hamabost-I bi mila eta hogeita lau'. It reads '15-01-2024', '7/03/1995' and the year-first "
    "'2024-I-15' as dates. Araua 37 p.194 writes the Roman month in place of the month digits: "
    "'1995/03/07; 1995-03-27; 1995/III/07; 1995-III-27'. https://github.com/TigreGotico/text2spoken/issues/340")

TELEPHONE = _misreading(
    "text2spoken has no telephone reading, and leaves digit groups after 'Tel.' as written, so euskaphone reads "
    "'Tel. 943 123 456' as 943 million. Araua 203, footnote 12: 'Telefono-zenbakiak emateko [...] zenbakiak binaka "
    "edo hirunaka ere zatitu daitezke: Telefonoa: +34 944 15 81 55 / +34 944 158 155'. "
    "https://github.com/TigreGotico/text2spoken/issues/339")
