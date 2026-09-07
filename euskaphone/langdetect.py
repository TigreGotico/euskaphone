"""Word-level language detection for code-switch routing.

The code-switch stage needs one decision per token: is this word Basque, or is
it embedded contact-language material to route through the ``es``/``fr`` lattice
and nativize? The orthographic heuristic in :mod:`euskaphone.codeswitch` answers
that from spelling alone — it flags a word only when it carries a letter Basque
does not use natively (``c q v w y ñ ç`` or a Romance accented vowel) or is a
known function word. That misses the loans and internationalisms spelled with
Basque-legal letters (``plaza``, ``general``, ``estazio``) and cannot tell
Spanish from French embedding.

This module adds a statistical detector: four character-level Markov models —
one each for Basque, Spanish, French and English — trained on Wikipedia and
serialized as small JSON artifacts under ``euskaphone/data/langdetect/``. A word
is scored under all four models; the model that assigns it the lowest
perplexity wins.

In-language default (null beats wrong)
--------------------------------------
Basque is the surrounding language, so it is the default: a word is only routed
out of Basque when a foreign model beats the Basque model by at least
:data:`DEFAULT_MARGIN` nats-per-character. Below that margin the word stays
``eu`` — a weak, ambiguous signal never misroutes a native word. The genuinely
ambiguous shared-alphabet internationalisms (``hotel``, ``general``, ``radio``)
sit inside that margin band and therefore stay Basque, which is exactly the
conservative behaviour a TTS frontend wants.

The detector is optional. It is used only when :mod:`markovonnx` is importable
and the bundled models are present; otherwise the caller falls back to the
orthographic heuristic. Loading is lazy and cached, so importing euskaphone
never pays the cost unless code-switching actually runs.
"""
from __future__ import annotations

import functools
import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: Languages the detector scores. ``eu`` is the in-language default.
LANGS: List[str] = ["eu", "es", "fr", "en"]

#: Boundary sentinels wrapping each word, matching the training pipeline so
#: word-initial and word-final character statistics are modelled.
_BOS, _EOS = "\x02", "\x03"

#: A foreign model must beat the Basque model by at least this many
#: nats-per-character (log-perplexity units) before a word is routed out of
#: Basque. Tuned on held-out Wikipedia words to favour never misrouting a native
#: word over catching every contact word (null beats wrong): a higher margin
#: keeps more words Basque.
DEFAULT_MARGIN: float = 0.25

#: High-frequency Basque wordforms that are always kept Basque, regardless of
#: the models. Encyclopedic training text underrepresents conversational
#: grammar, so a char-model can rate a short function word like ``dut`` or
#: ``ditut`` as English on its letter shape alone — and the auxiliary paradigms
#: are exactly the forms a Spanish or French model also fits well. They are
#: unambiguously native here and must never be routed to a contact lattice, so
#: the statistical decision is bypassed for them entirely. Both code-switch
#: classifiers consult this set: the orthographic backstop in
#: :mod:`euskaphone.codeswitch` checks it before its own contact stopword lists,
#: so the invariant holds whether or not the detector is installed.
#:
#: Membership criterion: a Basque closed-class form — determiner, demonstrative,
#: pronoun, postposition, question word, conjunction, particle — or a finite
#: form of the auxiliaries and high-frequency irregular verbs belongs here
#: regardless of what a model scores it. Open-class vocabulary still goes
#: through the models. The paradigms of *izan, ukan/edun, egon, joan, etorri,
#: egin, ibili, eraman* and the *nor* / *nork-nor* / *nork-nori-nor* auxiliary
#: series are listed by paradigm cell: a whole cell goes in as soon as any of
#: its members is one a foreign model outscores Basque on (the transitive
#: auxiliary ``du``, which French claims, is the motivating case). A cell no
#: foreign model claims anywhere is left out rather than padding the set.
#:
#: The familiar second-person pronoun ``hi`` is deliberately absent: it is
#: marked in standard usage and collides with the English greeting, which does
#: occur as embedded material. Its verb forms (``haiz``, ``hago``, ``habil``)
#: carry no such ambiguity and are listed.
BASQUE_KEEP = frozenset("""
da dira den dena dute du dut ditut ditu dituzte dizu diot dio zaio zait
zen zuen ziren zituen naiz gara zara zarete dira dago daude nago nengoen
izan izango izaten egin egiten egingo eman eta edo ez ezta bai baina baino
bat batzuk hau hori hura horiek hauek berau bera beraiz zein non nor zer nola
noiz nondik nora zergatik zenbat zeren hemen hor han bertan gaur bihar atzo
orain gero lehen oso asko gutxi ere are gehiago dagoeneko honela horrela
guztia guztiak denak elkar norbait zerbait inor ezer beti inoiz batzuetan
kaixo agur eskerrik mesedez barkatu bai ez
nire zure bere gure zuen haien niri zuri hari guri honi horri
haiz zaizu zaigu zaizue zaie duzu dugu duzue dituzu ditugu dituzue
nau gaitu zaitu naute gaituzte zaituzte zaituztet nuen zenuen genuen
zenuten zuten diozu diogu diozue diote dit didazu digu didazue didate
dizut dizugu dizuet nion zenion zion genion zenioten zioten zidan zizun
zigun zidaten ziguten nizun hago gaude zaude zaudete hengoen zegoen
geunden zeunden zeundeten zeuden noa hoa doa goaz zoaz zoazte doaz joan
joaten joango nator hator dator gatoz zatoz zatozte datoz eginda eginik
egitea egiteko nabil habil dabil gabiltza zabiltza dabiltza daramat
daramazu darama daramate behar nahi ahal ari ohi omen ote bide honek
horrek hark hauei horiei haiei honen horren haren hauen horien haietan
honetan horretan hartan hauetan horietan hala ni gu zu zuek nik hik guk
zuk zuei neu heu geu zeu geuk zeuk hire beren neure heure geure zeure
noren zertan zertaz nortzuk zeintzuk edota beraz halere hain hainbeste
gainera ordea alegia baizik gainean azpian aurrean atzean ondoan artean
barruan kanpoan aldean inguruan arte gabe bidez buruz kontra ordez aurka
alde ostean aldera berriz agian akaso apika noski ba ezin inon deus
nonbait noizbait aupa egun on arratsalde gabon
""".split())

#: Where the bundled JSON models live.
_MODEL_DIR = Path(__file__).parent / "data" / "langdetect"


def _load_gz(markov_chain_cls, path: Path):
    """Load a gzip-compressed markovonnx JSON model via a temporary file."""
    import gzip
    import tempfile

    with gzip.open(path, "rb") as fh:
        data = fh.read()
    with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return markov_chain_cls.load(tmp_path)
    finally:
        import os
        os.unlink(tmp_path)


def _normalize(word: str) -> str:
    """NFC + lowercase + keep only alphabetic characters (training parity)."""
    word = unicodedata.normalize("NFC", word).lower()
    return "".join(ch for ch in word if ch.isalpha())


def is_keep_word(word: str) -> bool:
    """Whether *word* is a Basque wordform on :data:`BASQUE_KEEP`."""
    core = _normalize(word)
    return bool(core) and core in BASQUE_KEEP


def _wrap(word: str) -> List[str]:
    return [_BOS] + list(word) + [_EOS]


class MarkovLangDetector:
    """Four char-Markov models scoring a word as eu / es / fr / en."""

    def __init__(self, models: Dict[str, "object"]):
        self._models = models

    # -- construction ---------------------------------------------------------

    @classmethod
    def from_dir(cls, model_dir: Path = _MODEL_DIR) -> Optional["MarkovLangDetector"]:
        """Load the bundled models, or return ``None`` if unavailable.

        Returns ``None`` when :mod:`markovonnx` is not installed or any of the
        four model files is missing — the caller then falls back to the
        orthographic heuristic. Models are shipped gzip-compressed
        (``<lang>.json.gz``, a few tens of KB each); a plain ``<lang>.json`` is
        also accepted.
        """
        try:
            from markovonnx import MarkovChain
        except Exception:
            return None
        models = {}
        for lang in LANGS:
            gz = model_dir / f"{lang}.json.gz"
            plain = model_dir / f"{lang}.json"
            try:
                if gz.is_file():
                    models[lang] = _load_gz(MarkovChain, gz)
                elif plain.is_file():
                    models[lang] = MarkovChain.load(str(plain))
                else:
                    return None
            except Exception:
                return None
        return cls(models)

    # -- scoring --------------------------------------------------------------

    def score(self, word: str) -> Dict[str, float]:
        """Length-normalized log-perplexity per language (lower = better fit)."""
        seq = _wrap(_normalize(word))
        out: Dict[str, float] = {}
        for lang, mc in self._models.items():
            ppx = mc.perplexity([seq])
            out[lang] = math.log(max(ppx, 1e-30))
        return out

    def detect(self, word: str, margin: float = DEFAULT_MARGIN
               ) -> Tuple[str, Dict[str, float]]:
        """Return ``(lang, scores)`` with the in-language default applied.

        The best-fitting foreign language is returned only if it beats ``eu`` by
        at least ``margin``; otherwise the word stays ``eu``.
        """
        core = _normalize(word)
        if not core:
            return "eu", {}
        if is_keep_word(core):
            # Unambiguously native wordform: never route out of Basque.
            return "eu", {}
        scores = self.score(word)
        best = min(scores, key=scores.get)
        if best == "eu":
            return "eu", scores
        if (scores["eu"] - scores[best]) < margin:
            return "eu", scores
        return best, scores

    def is_contact(self, word: str, margin: float = DEFAULT_MARGIN) -> bool:
        """Whether *word* is embedded contact-language material (not Basque)."""
        return self.detect(word, margin)[0] != "eu"


@functools.lru_cache(maxsize=1)
def get_detector() -> Optional[MarkovLangDetector]:
    """The cached bundled detector, or ``None`` if unavailable."""
    return MarkovLangDetector.from_dir()
