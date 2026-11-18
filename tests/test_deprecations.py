"""The readers that text2spoken replaces keep working and warn.

Each name left the reading path of :func:`euskaphone.normalize.normalize_text`.
It keeps its behaviour, and a call gives a :class:`DeprecationWarning` that
names the release that removes it. The reading tests of text2spoken and of the
fallbacks check that the reading path calls none of them.
"""
import importlib

import pytest

from euskaphone.version import VERSION_MAJOR


@pytest.fixture
def removal_version():
    return importlib.import_module("euskaphone.deprecation").REMOVAL_VERSION


DEPRECATED = [
    ("number_utils", "normalize_numbers", ("31 katu",), "hogeita hamaika katu"),
    ("dates", "normalize_dates", ("2024-01-15",), "bi mila eta hogeita lauko urtarrilaren hamabostean"),
    ("dates", "compose_date", (1995, 3, 7), "mila bederatziehun eta laurogeita hamabosteko martxoaren zazpian"),
    ("abbreviations", "expand_abbreviations", ("katuak etab.",), "katuak eta abar"),
    ("romans", "normalize_romans", ("XX. mendea",), "hogeigarren mendea"),
    ("units", "normalize_units", ("5 km",), "bost kilometro"),
    ("numverbal", "spell_cardinal", (14,), "hamalau"),
    ("numverbal", "inessive", ("mendi",), "mendian"),
    ("numverbal", "locative_genitive", ("lau",), "lauko"),
]


@pytest.mark.parametrize("module,name,args,result", DEPRECATED)
def test_a_deprecated_reader_warns_and_keeps_working(removal_version, module, name, args, result):
    reader = getattr(importlib.import_module(f"euskaphone.{module}"), name)
    with pytest.warns(DeprecationWarning, match=rf"euskaphone\.{module}\.{name} .*removed in euskaphone {removal_version}"):
        assert reader(*args) == result


def test_the_month_table_warns_and_keeps_working(removal_version):
    from euskaphone import dates
    with pytest.warns(DeprecationWarning, match=f"removed in euskaphone {removal_version}"):
        assert dates.MONTHS_GENITIVE[3] == "martxoaren"


def test_the_removal_release_comes_after_this_one(removal_version):
    assert int(removal_version.split(".")[0]) > VERSION_MAJOR
