"""Deprecation of the readers that text2spoken replaces.

text2spoken reads numbers, dates, abbreviations, Roman numerals and units for
:func:`euskaphone.normalize.normalize_text`. The euskaphone readers that left the
reading path keep their names and their behaviour until :data:`REMOVAL_VERSION`,
and each call gives a :class:`DeprecationWarning`.
"""
import warnings

from euskaphone.version import VERSION_MAJOR

#: The release that removes the deprecated readers.
REMOVAL_VERSION = f"{VERSION_MAJOR + 1}.0.0"


def warn_deprecated(name: str, use: str) -> None:
    """Warn that ``euskaphone.<name>`` is deprecated, and name what to ``use``."""
    warnings.warn(
        f"euskaphone.{name} is deprecated: {use}. It will be removed in "
        f"euskaphone {REMOVAL_VERSION}.", DeprecationWarning, stacklevel=3)
