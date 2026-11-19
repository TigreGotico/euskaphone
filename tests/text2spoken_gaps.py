"""Readings where text2spoken differs from the value that a test cites.

Each mark names one class of misreading of a form that text2spoken reads, and
the text2spoken issue for it. euskaphone has no fallback for these: text2spoken
fixes them. A strict xfail turns red when text2spoken gives the cited reading,
so the mark comes off.
"""
import pytest


def _misreading(reason: str):
    return pytest.mark.xfail(strict=True, reason=reason)


LAPURDI_LECT = _misreading(
    "text2spoken reads the Lapurdian lect 'eu-x-lapurdi' as Batua: '15' gives 'hamabost'. Araua 7: "
    "'Bost zenbakiaren aldaera bortz da, Iparraldeko zenbait hizkeratan erabilia.' "
    "https://github.com/TigreGotico/text2spoken/issues/262")

ROMAN_MONTH_DAY_FIRST = _misreading(
    "text2spoken reads the day and the year of '15-I-2024' and keeps the Roman month as written: "
    "'hamabost-I bi mila eta hogeita lau'. It reads '15-01-2024' and the year-first '2024-I-15' as dates. "
    "Araua 37 p.194 writes the Roman month in place of the month digits: '1995/03/07; 1995-03-27; 1995/III/07; "
    "1995-III-27'. https://github.com/TigreGotico/text2spoken/issues/340")

ROMAN_MONTH_SLASH = _misreading(
    "text2spoken reads the day and the year of '7/III/1995' and keeps the Roman month as written: "
    "'zazpi/III/mila bederatziehun eta laurogeita hamabost'. It reads '7/03/1995' and the year-first "
    "'1995/III/07' as dates. Araua 37 p.194 writes the Roman month in place of the month digits: "
    "'1995/03/07; 1995-03-27; 1995/III/07; 1995-III-27'. TODO(text2spoken issue: ROMAN_MONTH_SLASH)")
