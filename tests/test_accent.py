"""Accent forcing: IPA mode and the verification-gated respeller."""
import csv
import os

import pytest

import orthography2ipa as o2i
from euskaphone.accent import (
    RESPELL_RULES, force_accent, respell_report,
)

_GOLD = os.path.join(
    os.path.dirname(o2i.__file__), "data", "gold", "spain_romance_tts", "eu.tsv")


def _sentences():
    with open(_GOLD, encoding="utf-8") as fh:
        return [row["sentence"] for row in csv.DictReader(fh, delimiter="\t")]


def test_ipa_mode_returns_target_transcription():
    from orthography2ipa import G2P
    got = force_accent("Zazpi katu zuri", "biscayan", mode="ipa")
    assert got == G2P("eu-x-bizkaiera").transcribe("Zazpi katu zuri")


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        force_accent("etxe", "biscayan", mode="wat")


def test_respell_never_increases_distance():
    # The gate keeps an edit only if it strictly lowers PER, so per_after can
    # never exceed per_before for any lect/sentence.
    for s in _sentences():
        for lect in ["eu-x-bizkaiera", "eu-x-zuberera", "eu-x-lapurtera",
                     "eu-x-gipuzkera"]:
            r = respell_report(s, lect)
            assert r.per_after <= r.per_before + 1e-12
            assert r.gain >= -1e-12


def test_biscayan_seseo_respell_wins():
    # z -> s makes a Batua reading match Biscayan's apical /s̺/.
    r = respell_report("Zazpi katu zuri", "biscayan")
    assert "seseo_z_to_s" in r.accepted
    assert r.respelled == "Zaspi katu suri"
    assert r.gain > 0


def test_continental_aspiration_is_not_recoverable():
    # Batua has a silent h and no ü, so the gate rejects h-insertion / front
    # rounding: the honest ceiling for these features is ~0 gain.
    total = 0.0
    for s in _sentences():
        total += respell_report(s, "souletin").gain
    assert total == pytest.approx(0.0, abs=1e-9)


def test_gipuzkoan_identical_to_batua_needs_no_edit():
    # eu-x-gipuzkera transcribes identically to eu on this gold, so nothing is
    # accepted and gain is exactly zero.
    for s in _sentences():
        r = respell_report(s, "eu-x-gipuzkera")
        assert r.accepted == []
        assert r.gain == pytest.approx(0.0, abs=1e-12)


def test_force_accent_respell_matches_report():
    assert (force_accent("Zazpi katu", "biscayan", mode="respell")
            == respell_report("Zazpi katu", "biscayan").respelled)


def test_every_rule_has_a_rationale():
    for rule in RESPELL_RULES:
        assert rule.rationale.strip()
        assert rule.name.strip()
