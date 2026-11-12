"""Northern Bizkaian lexical pitch-accent annotation (opt-in, Biscayan only)."""
from euskaphone import EuskaPhonemizer, default_lexicon, AccentClass

ph = EuskaPhonemizer()

# Accented words carry a mark on their lexically accented syllable; unaccented
# (and unknown) words are left unmarked.
for sentence in [
    "Amuma etxean dago.",       # amúma 'grandmother' — accented
    "Kipula eta makila.",       # kipúla, makíla — accented loanwords
    "Lagun bat etorri da.",     # lagun 'friend' — unaccented
]:
    marked = ph.phonemize_sentence(
        sentence, "biscayan", contact="none", pitch_accent=True)
    print(f"{sentence:<24} -> {marked}")

# The lexicon is small and fully cited; unknown words are a distinct class.
lex = default_lexicon()
print(f"\naccent lexicon: {len(lex)} attested Northern Bizkaian words")
print("amuma  ->", lex.lookup("amuma").accent_class.value,
      "| source:", lex.lookup("amuma").source[:40], "...")
print("mahaia ->", lex.lookup("mahaia").accent_class.value, "(not attested)")
assert lex.lookup("mahaia").accent_class is AccentClass.UNKNOWN
