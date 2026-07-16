"""Basic Basque phonemization (Standard Batua)."""
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
for sentence in [
    "Kaixo, mundua.",
    "Gaur egia esan dut.",
    "Zazpi katu zuri ikusi ditut.",
]:
    print(f"{sentence!r:40s} -> {ph.phonemize_sentence(sentence)}")
