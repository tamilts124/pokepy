"""Scripted smoke test: drive new_game() far enough to exercise the Pokedex
lore display fix (textwrap) for both the buggy entries (Flamclaw, Infernox)
and confirm the overall game boots without crashing."""
import sys, io, builtins
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import main as M

# Build a Game and directly hit the pokedex entry view for Flamclaw/Infernox,
# the exact code path that was broken.
g = M.Game()
g.player_name = "Tester"
g.caught.add("Flamclaw")
g.caught.add("Infernox")
g.seen.add("Flamclaw")
g.seen.add("Infernox")

buf = io.StringIO()
old_stdout = sys.stdout
old_input = builtins.input
builtins.input = lambda *a, **k: ""
sys.stdout = buf
try:
    g._show_pokedex_entry("Flamclaw")
    g._show_pokedex_entry("Infernox")
finally:
    sys.stdout = old_stdout
    builtins.input = old_input

out = buf.getvalue()
assert "Its curved claws burn red-hot" in out, "Flamclaw lore missing from output"
assert "fearsome creature of living flame" in out, "Infernox lore missing from output"
assert "Its claws burn red-hot in battle." not in out, "stale short desc leaked through"
assert "A fearsome dragon of living flame." not in out, "stale short desc leaked through"
print("PASS: pokedex entry view renders new lore for Flamclaw and Infernox, no stale text")

# Confirm catch_rate/ability/evolution are intact (would KeyError/None otherwise)
from data.creatures import CREATURES
assert CREATURES["Flamclaw"]["catch_rate"] == 45
assert CREATURES["Flamclaw"]["ability"] == "Blaze"
assert CREATURES["Infernox"]["evolution"] == {}
print("PASS: catch_rate/ability/evolution restored correctly")

# Confirm no creature lore desc is printed unwrapped anywhere (regression check
# for the two extra display sites found: open_creatures() detail card, and the
# new_game() starter selection screen).
src = open("main.py", encoding="utf-8").read()
assert "for _line in _tw.wrap(CREATURES[c.name]['desc']" in src, "creature detail card desc not wrapped"
assert "for _line in _tw.wrap(d['desc']" in src, "starter selection desc not wrapped"
print("PASS: creature detail card and starter selection both wrap long lore text")
