"""Vigesimal (base-20) number verbalization, cited to Euskaltzaindia Araua 7/18."""
from euskaphone.normalize import normalize_text
from euskaphone.number_utils import BasqueNumberParser

p = BasqueNumberParser("eu")
for n in [21, 31, 75, 90, 1936]:
    print(f"{n:5d} -> {p.cardinal(n)}")
print("16th ->", p.ordinal(16))

# case-suffixed numerals and clock time in running text, read by text2spoken
print(normalize_text("1936ko gerra", "eu"))
print(normalize_text("Kontzertua 20:00etan hasiko da.", "eu"))
