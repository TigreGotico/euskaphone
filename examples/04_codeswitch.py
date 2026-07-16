"""Embedded Spanish/French routed through the contact lattice and nativized."""
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
# peninsular dialect -> Spanish contact by default
print(ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu"))
# continental dialect -> French contact by default
print(ph.phonemize_sentence("Maison Rouge etxean.", "souletin"))
# disable code-switching entirely
print(ph.phonemize_sentence("Plaza Mayor.", "eu", contact="none"))
