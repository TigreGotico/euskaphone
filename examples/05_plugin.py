"""The OVOS G2P plugin wrapper."""
from euskaphone.plugin import EuskaphoneG2PPlugin

plug = EuskaphoneG2PPlugin("eu")
print("codes:", plug.language_codes)
print(plug.transcribe("kaixo mundua"))
