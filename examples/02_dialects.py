"""The eight Basque dialects, by code and by human-readable alias."""
from euskaphone import EuskaPhonemizer, list_dialects, resolve_lect

ph = EuskaPhonemizer()
print("dialects:", list_dialects())
print("souletin ->", resolve_lect("souletin"), " biscayan ->", resolve_lect("biscayan"))

sentence = "Hotza egiten du gaur mendian."
for name in ["batua", "gipuzkera", "souletin", "biscayan"]:
    print(f"{name:12s} -> {ph.phonemize_sentence(sentence, name)}")
