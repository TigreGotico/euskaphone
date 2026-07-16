"""OVOS G2P plugin wrapper for euskaphone.

Exposes the euskaphone pipeline behind the shared orthography2ipa G2P plugin
interface, so an OVOS TTS stack can select a Basque dialect by language code.
It is an engine built ON orthography2ipa, not a plugin discovered by it; the
:class:`~euskaphone.EuskaPhonemizer` API remains the stable entry point and this
class is the integration layer.
"""
from typing import List, Optional

from orthography2ipa import WordContext

from euskaphone.registry import list_dialects, resolve_lect


class EuskaphoneG2PPlugin:
    """Dialect-aware Basque G2P via the euskaphone pipeline."""

    def __init__(self, lang: str = "eu", contact: str = "auto") -> None:
        self.lang = lang
        self.contact = contact
        self._phonemizer = None

    @property
    def language_codes(self) -> List[str]:
        return list_dialects()

    def _engine(self):
        if self._phonemizer is None:
            from euskaphone import EuskaPhonemizer
            self._phonemizer = EuskaPhonemizer()
        return self._phonemizer

    def transcribe(self, text: str) -> str:
        return self._engine().phonemize_sentence(
            text, dialect=self.lang, contact=self.contact)

    def transcribe_word(
        self, word: str, context: Optional[WordContext] = None
    ) -> str:
        lang = (context.lang if context is not None and context.lang
                else self.lang)
        return self._engine().phonemize_sentence(
            word, dialect=lang, contact=self.contact)
