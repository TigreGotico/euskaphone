"""Accent forcing: IPA delta and verification-gated respelling."""
from euskaphone.accent import force_accent, respell_report

# mode="ipa": the target lect's own transcription (the IPA delta vs Batua).
print("ipa   :", force_accent("Zazpi katu zuri", "biscayan", mode="ipa"))

# mode="respell": Batua orthography rewritten so a Batua reader approaches the
# target. For Biscayan, seseo (z -> s) survives the verification gate.
print("respell:", force_accent("Zazpi katu zuri", "biscayan", mode="respell"))

# The report shows the gate's accounting: what the base reading scored before,
# after, which edits survived, and the honest gain.
r = respell_report("Zazpi katu zuri", "biscayan")
print(f"\naccepted edits : {r.accepted}")
print(f"PER before/after: {r.per_before:.4f} -> {r.per_after:.4f} "
      f"(gain {r.gain:.4f})")

# Continental aspiration is NOT recoverable through Batua (silent h), so the gate
# rejects h-insertion and the gain is ~0 — the honest ceiling.
c = respell_report("Hotza da gaur", "souletin")
print(f"souletin gain  : {c.gain:.4f} (aspiration/front-rounding unrecoverable)")
