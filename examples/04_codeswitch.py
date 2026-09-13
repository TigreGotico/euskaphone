"""Embedded Spanish/French/English routed through the contact lattice and nativized."""
from euskaphone import EuskaPhonemizer

ph = EuskaPhonemizer()
# peninsular dialect -> Spanish contact by default
print(ph.phonemize_sentence("Madrilen Plaza Mayor ikusi dut.", "eu"))
# continental dialect -> French contact by default
print(ph.phonemize_sentence("Maison Rouge etxean.", "souletin"))
# English tech/media register, detected per word
print(ph.phonemize_sentence("Streaming plataforma berria erabili dugu."))
# disable code-switching entirely
print(ph.phonemize_sentence("Plaza Mayor.", "eu", contact="none"))
