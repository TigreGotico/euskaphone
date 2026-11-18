"""The readers that text2spoken replaces keep working and warn.

Each name left the reading path of :func:`euskaphone.normalize.normalize_text`.
It keeps its behaviour, and a call gives a :class:`DeprecationWarning` that
names the release that removes it. The reading tests of text2spoken and of the
fallbacks check that the reading path calls none of them.
"""
import importlib
import re

import pytest

from euskaphone.version import VERSION_MAJOR


@pytest.fixture
def removal_version():
    return importlib.import_module("euskaphone.deprecation").REMOVAL_VERSION


DEPRECATED = [
    ("number_utils", "normalize_numbers", ("31 katu",), "hogeita hamaika katu"),
    ("number_utils", "read_space_grouped_numbers", ("1 000 000 lagun",), "milioi bat lagun"),
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


# Names that a module imported and so exported, before text2spoken read the text.
REEXPORTED = [
    ("normalize", "expand_abbreviations", "abbreviations"),
    ("normalize", "normalize_dates", "dates"),
    ("normalize", "normalize_numbers", "number_utils"),
    ("normalize", "normalize_romans", "romans"),
    ("normalize", "normalize_units", "units"),
    ("dates", "spell_cardinal", "numverbal"),
    ("dates", "inessive", "numverbal"),
    ("dates", "locative_genitive", "numverbal"),
]


@pytest.mark.parametrize("module,name,home", REEXPORTED)
def test_a_reexported_name_warns_and_gives_the_reader_of_its_home_module(removal_version, module, name, home):
    with pytest.warns(DeprecationWarning, match=rf"euskaphone\.{module}\.{name} .*removed in euskaphone {removal_version}"):
        reader = getattr(importlib.import_module(f"euskaphone.{module}"), name)
    assert reader is getattr(importlib.import_module(f"euskaphone.{home}"), name)


@pytest.mark.parametrize("module", ["normalize", "dates"])
def test_an_unknown_name_is_still_an_attribute_error(module):
    with pytest.raises(AttributeError):
        getattr(importlib.import_module(f"euskaphone.{module}"), "no_such_reader")


def test_the_removal_release_comes_after_this_one(removal_version):
    assert int(removal_version.split(".")[0]) > VERSION_MAJOR


DEPRECATED_NAMES = sorted({f"{module}.{name}" for module, name, *_ in DEPRECATED + REEXPORTED}
                          | {"dates.MONTHS_GENITIVE"})


def _replacement(module, name):
    # The text after "is deprecated:" names what to use in place of the name.
    with pytest.warns(DeprecationWarning) as record:
        getattr(importlib.import_module(f"euskaphone.{module}"), name)
    return str(record[0].message).split(" is deprecated: ", 1)[1]


@pytest.mark.parametrize("module,name,home", REEXPORTED)
def test_a_reexported_name_points_to_a_replacement_that_is_not_deprecated(module, name, home):
    use = _replacement(module, name)
    # The home module holds the same deprecated reader, so it is no replacement.
    assert re.search(rf"euskaphone\.{home}(?![.\w])", use) is None
    assert [deprecated for deprecated in DEPRECATED_NAMES if deprecated in use] == []


@pytest.mark.parametrize("module,name,args,result", DEPRECATED)
def test_a_deprecated_reader_points_to_a_replacement_that_is_not_deprecated(module, name, args, result):
    reader = getattr(importlib.import_module(f"euskaphone.{module}"), name)
    with pytest.warns(DeprecationWarning) as record:
        reader(*args)
    use = str(record[0].message).split(" is deprecated: ", 1)[1]
    assert [deprecated for deprecated in DEPRECATED_NAMES if deprecated in use] == []
