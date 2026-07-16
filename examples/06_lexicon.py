"""Register a proper-name/loan lexicon (empty by default)."""
import tempfile, os
from euskaphone import EuskaPhonemizer, register_lexicon

# a word<TAB>ipa table following the orthography2ipa lexicon contract
with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False,
                                 encoding="utf-8") as fh:
    fh.write("Gasteiz\tɡas̺teis̻\n")
    path = fh.name
register_lexicon("eu", path)
print(EuskaPhonemizer().phonemize_sentence("Gasteiz", "eu"))
os.unlink(path)
