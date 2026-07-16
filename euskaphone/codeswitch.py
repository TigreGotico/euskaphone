"""Code-switch handling: embedded Spanish / French / English routed and nativized.

Real Basque text is bilingual, and increasingly trilingual. On the peninsular
side (Hegoalde) it embeds Spanish; on the continental side (Iparralde) it embeds
French — proper names, loans, quoted fragments. On both sides the modern
tech/music/media register embeds **English** (``streaming``, ``software``,
``feedback``, band and product names). A TTS frontend that hands such a word to
the Basque lattice mispronounces it, and one that hands it to the raw
Spanish/French/English lattice emits phones outside the Basque inventory the
voice was trained on.

euskaphone takes arbtok's **total-nativization** stance — *never drop a segment,
always project it onto the target inventory* — but keeps the machinery far
simpler than arbtok. A word-level step decides whether a token is Basque or
contact-language and, if contact, which language; a detected contact word is
transcribed through the orthography2ipa ``es-ES`` / ``fr-FR`` / ``en-US`` lattice,
and every phone in that result is projected onto the Basque phoneme inventory.
There is no sub-word alignment.

Per-word language identification prefers the statistical char-Markov detector
(:mod:`euskaphone.langdetect`, models for ``eu``/``es``/``fr``/``en``) when its
bundled models are importable, with the orthographic heuristic below as a
backstop that catches Basque-legal-letter loans the detector misses; when the
detector is unavailable the orthographic heuristic decides on its own.

The contact language is chosen by the ``contact`` parameter:

* ``"auto"`` (default) — detect contact words and classify each *per word* as
  English, French or Spanish; an unclassified contact word falls to the
  dialect's default side (peninsular → Spanish, continental → French; see
  :func:`euskaphone.registry.default_contact`);
* ``"es"`` / ``"fr"`` / ``"en"`` — force that contact lattice for detected
  contact words;
* ``"none"`` — disable code-switching; every token is transcribed as Basque.

Orthographic heuristic
----------------------
Basque orthography does not natively use ``c q v w y ñ ç`` or the Romance
accented vowels, and native spelling never carries the English digraphs
``th sh wh ck gh oo ee aw``. A token carrying any of those (or a common
Spanish/French/English function word) is treated as contact material. This is a
deliberately shallow, well-documented backstop; sequences that occur natively in
Basque (``ea`` in *etxean*, ``ing`` in *inguru*) are excluded so it never fires
on a Basque word, and it never *drops* a word.

English → Basque projection
---------------------------
Basque has a five-vowel system, no phonemic interdentals, no ``/v/``, no ``/w/``
consonant, no ``/ŋ/`` and no ``/ɹ/``. English anglicisms in Basque are adapted
through Spanish/French phonology, which lacks the same set; the projection
follows the loanword-adaptation pattern documented for Basque anglicisms
(interdental stopping, glide vocalisation, rhotic and velar substitution) and,
where the literature is silent, states the mapping as a convention: ``θ→t``,
``ð→d``, ``w→u̯``, dark ``ɫ→l``, ``ɹ/ɻ→r``, ``ŋ→n``, ``dʒ→tʃ`` and the vowels onto
``a e i o u`` (see :data:`_NATIVIZE_ENGLISH`).
"""
from __future__ import annotations

import functools
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Orthographic detection (backstop when the char-Markov detector is absent).
# ---------------------------------------------------------------------------

#: Letters not used natively in Basque orthography (loans/proper names only).
_NON_BASQUE_LETTERS = set("cqvwyñçáíóúàâèêîïôùäëö")

#: Letters/accents that point specifically at Spanish.
_SPANISH_LETTERS = set("ñáíóú")

#: Letters/accents that point specifically at French.
_FRENCH_LETTERS = set("çàâèêëîïôùûœ")

#: English orthographic digraphs absent from native Basque spelling. Excludes
#: sequences that occur natively in Basque — ``ea`` (etxean), ``ou``, ``au`` and
#: ``ing`` (inguru) — so the signal never fires on a Basque word.
_ENGLISH_DIGRAPHS = ("th", "sh", "wh", "ck", "gh", "ght", "oo", "ee", "aw")

#: Very common Spanish function words (no non-Basque letter of their own).
_SPANISH_STOPWORDS = {
    "el", "la", "los", "las", "del", "por", "para", "con", "una", "que",
    "más", "muy", "pero", "como", "este", "esta", "de", "en", "y",
}

#: Very common French function words.
_FRENCH_STOPWORDS = {
    "le", "les", "des", "du", "et", "un", "une", "dans", "pour", "avec",
    "sur", "pas", "plus", "très", "mais", "cette", "au", "aux",
}

#: Very common English function/register words (tech, music, media).
_ENGLISH_STOPWORDS = {
    "the", "of", "and", "to", "in", "is", "it", "for", "with", "this",
    "that", "on", "at", "as", "by", "live", "new", "best", "feat", "remix",
    "online", "web", "app", "software", "hardware", "streaming", "stream",
    "download", "upload", "email", "startup", "feedback", "password",
    "weekend", "rock", "pop", "jazz", "band", "single", "album",
}

#: Union of all contact stopwords, for the language-agnostic contact test.
_CONTACT_STOPWORDS = _SPANISH_STOPWORDS | _FRENCH_STOPWORDS | _ENGLISH_STOPWORDS


def _strip(token: str) -> str:
    """Lower-case a token and strip surrounding punctuation for testing."""
    return token.strip("".join(
        c for c in token if not (c.isalpha() or c == "-"))).lower()


def _has_english_signal(core: str) -> bool:
    """Whether *core* (a stripped lower-case token) looks English.

    ``w`` is not a native Basque letter and, outside a French cedilla/accent
    context, points overwhelmingly at English/Germanic material; the English
    digraphs never occur in native Basque spelling. ``k`` is native to Basque,
    so it is never a signal on its own.
    """
    if core in _ENGLISH_STOPWORDS:
        return True
    if any(dg in core for dg in _ENGLISH_DIGRAPHS):
        return True
    return "w" in core and not any(ch in _FRENCH_LETTERS for ch in core)


def is_contact_word(token: str) -> bool:
    """Heuristically decide whether *token* is embedded contact-language text."""
    core = _strip(token)
    if not core:
        return False
    if any(ch in _NON_BASQUE_LETTERS for ch in core):
        return True
    if _has_english_signal(core):
        return True
    return core in _CONTACT_STOPWORDS


def contact_language(token: str, default_side: str = "es") -> str:
    """Classify a *contact* token as ``"en"``, ``"fr"`` or ``"es"`` (orthographic).

    Only meaningful for a token that :func:`is_contact_word` already flagged, and
    used as the fallback when the char-Markov detector is unavailable or returns
    the Basque default. English is checked first (its signals are the most
    specific), then the Spanish/French accent-and-cedilla split; a token with no
    language-specific signal falls back to ``default_side``.
    """
    core = _strip(token)
    if _has_english_signal(core):
        return "en"
    if any(ch in _FRENCH_LETTERS for ch in core) or core in _FRENCH_STOPWORDS:
        return "fr"
    if any(ch in _SPANISH_LETTERS for ch in core) or core in _SPANISH_STOPWORDS:
        return "es"
    return default_side


# ---------------------------------------------------------------------------
# Nativization: project a contact-language IPA string onto Basque phones.
# ---------------------------------------------------------------------------

#: Combining/length marks dropped before projection (nasal tilde, stress,
#: liaison, length).
_DROP = ("̃", "ˈ", "ˌ", "‿", "ː", "ˑ")

#: Phones shared by every contact language: the extra Romance/English vowels and
#: the voiced obstruents Basque lacks.
_NATIVIZE_COMMON = {
    "v": "b",    # /v/ → /b/ (Basque has no /v/)
    "z": "s̻",   # voiced sibilant → laminal (Basque has no voiced sibilant)
    "ʒ": "ʃ",    # postalveolar fricative devoiced
    "ɔ": "o", "ɛ": "e", "ɑ": "a", "ə": "e",
    "ø": "e", "œ": "e",
    "ɥ": "j",
}

#: Romance-specific projection (Spanish + French).
_NATIVIZE_ROMANCE = {
    **_NATIVIZE_COMMON,
    "θ": "s̻",   # Castilian interdental → laminal sibilant
    "ʝ": "j",    # Spanish yeísmo fricative → glide
    "ɟʝ": "j",   # Spanish affricated /ʝ/ → glide
    "ʁ": "r", "ʀ": "r", "χ": "x",   # French uvulars/velars
    "y": "i",    # French /y/ (Souletin keeps it; overridden per lect)
    # denasalized French nasal vowels (tilde dropped; catch bare marks)
    "æ̃": "e", "ɑ̃": "a", "ɔ̃": "o", "ɛ̃": "e", "œ̃": "e", "õ": "o",
}

#: English-specific projection. See the module docstring for rationale.
_NATIVIZE_ENGLISH = {
    **_NATIVIZE_COMMON,
    # diphthongs (longest-first matching also handles this)
    "eɪ": "ei", "aɪ": "ai", "ɔɪ": "oi", "aʊ": "au", "oʊ": "o", "əʊ": "o",
    # interdentals → stops (TH-stopping)
    "θ": "t", "ð": "d",
    # glide / rhotic / velar-nasal substitutions
    "w": "u̯", "ʍ": "u̯", "ɫ": "l", "ɹ": "r", "ɻ": "r", "ŋ": "n",
    # affricate: English /dʒ/ → Basque tx /tʃ/
    "dʒ": "tʃ",
    # vowels to the 5-vowel system
    "æ": "a", "ʌ": "a", "ɐ": "a", "ɒ": "o",
    "ɪ": "i", "ʊ": "u", "ɜ": "e", "ɝ": "e",
}


def _nativize(ipa: str, keep_y: bool = False, english: bool = False) -> str:
    """Project a contact-language IPA string onto the Basque inventory.

    ``english`` selects the English projection table; otherwise the Romance
    (Spanish/French) table is used. ``keep_y`` preserves ``/y/`` for the
    Souletin lect (Romance route only).
    """
    table = _NATIVIZE_ENGLISH if english else _NATIVIZE_ROMANCE
    for d in _DROP:
        ipa = ipa.replace(d, "")
    for src in sorted(table, key=len, reverse=True):
        if keep_y and src == "y":
            continue
        ipa = ipa.replace(src, table[src])
    return ipa


# ---------------------------------------------------------------------------
# The contact transcriber.
# ---------------------------------------------------------------------------

_CONTACT_CODE = {"es": "es-ES", "fr": "fr-FR", "en": "en-US"}

#: Below this length the char-Markov detector's foreign verdict needs
#: orthographic corroboration (short native Basque words score foreign easily).
_MIN_DETECTOR_LEN = 6


@functools.lru_cache(maxsize=None)
def _contact_engine(contact: str):
    """A cached orthography2ipa engine for the contact lattice."""
    from orthography2ipa import G2P
    return G2P(_CONTACT_CODE[contact])


def transcribe_contact(word: str, contact: str, keep_y: bool = False) -> str:
    """Transcribe a contact *word* and nativize it onto the Basque inventory."""
    ipa = _contact_engine(contact).transcribe(word)
    return _nativize(ipa, keep_y=keep_y, english=(contact == "en"))


# ---------------------------------------------------------------------------
# Per-word detection and language routing.
# ---------------------------------------------------------------------------

def detect_contact_word(token: str) -> bool:
    """Whether *token* is embedded contact-language material.

    Prefers the statistical char-Markov detector
    (:mod:`euskaphone.langdetect`) when its bundled models are available, and
    falls back to (or is backstopped by) the orthographic
    :func:`is_contact_word` heuristic. The detector catches Basque-legal-letter
    loans the heuristic misses while keeping Basque the in-language default; the
    orthographic backstop catches loans the detector scores as Basque
    (e.g. ``software``).
    """
    from euskaphone.langdetect import get_detector

    detector = get_detector()
    if detector is not None:
        return detector.is_contact(token) or is_contact_word(token)
    return is_contact_word(token)


def route_token(token: str, contact: str,
                default_side: str = "es") -> Optional[str]:
    """The contact language to route *token* through, or ``None`` for Basque.

    * ``contact == "none"`` → always ``None``.
    * ``contact`` in ``es``/``fr``/``en`` → that language when *token* is
      contact material (by detector or heuristic), else ``None``.
    * ``contact == "auto"`` → the char-Markov detector's per-word language
      (``es``/``fr``/``en``) when it beats the Basque default; otherwise the
      orthographic backstop (:func:`is_contact_word` +
      :func:`contact_language`); ``None`` for a Basque token.
    """
    if contact == "none":
        return None
    if contact in _CONTACT_CODE:  # forced es / fr / en
        return contact if detect_contact_word(token) else None

    from euskaphone.langdetect import get_detector
    detector = get_detector()
    if detector is not None:
        lang = detector.detect(token)[0]
        # The char-Markov detector is over-eager on *short* words — "jan",
        # "bada" and other native forms score foreign on 3-4 characters. Accept
        # its foreign verdict only when the token is long enough to be reliable
        # or the orthographic heuristic corroborates it; short, plausibly-native
        # words stay Basque (null beats wrong).
        if lang != "eu" and (len(_strip(token)) >= _MIN_DETECTOR_LEN
                             or is_contact_word(token)):
            return lang
        # detector says Basque (or was gated) — orthographic backstop for loans
        if is_contact_word(token):
            return contact_language(token, default_side)
        return None
    if is_contact_word(token):
        return contact_language(token, default_side)
    return None


def split_runs(text: str, contact: str,
               default_side: str = "es") -> List[Tuple[Optional[str], str]]:
    """Split *text* into ``(contact_lang, token)`` pairs by the word router.

    ``contact_lang`` is ``None`` for a Basque token, or the contact language
    (``"es"`` / ``"fr"`` / ``"en"``) to route the token through (see
    :func:`route_token`). ``contact == "none"`` marks every token as Basque.
    """
    return [(route_token(token, contact, default_side), token)
            for token in text.split()]
