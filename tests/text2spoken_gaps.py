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

TELEPHONE = _misreading(
    "text2spoken has no telephone reading, and leaves digit groups after 'Tel.' as written, so euskaphone reads "
    "'Tel. 943 123 456' as 943 million. Araua 203, footnote 12: 'Telefono-zenbakiak emateko [...] zenbakiak binaka "
    "edo hirunaka ere zatitu daitezke: Telefonoa: +34 944 15 81 55 / +34 944 158 155'. "
    "TODO(text2spoken issue: TELEPHONE)")
