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
    "TODO(text2spoken issue: LAPURDI_LECT)")
