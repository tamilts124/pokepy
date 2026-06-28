"""Verify Swift Swim on_entry fires in rain, not in other weather."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from engine.core import Creature
from engine.battle import fire_on_entry

# Find a creature with Swift Swim
class FakeC:
    ability = "Swift Swim"
    name = "Wavefin"
    nickname = None
    _battle_tag = "Your"

c = FakeC()
foe = FakeC()
foe.name = "Rockshell"

msgs_rain  = fire_on_entry(c, foe, "Rainy")
msgs_sunny = fire_on_entry(c, foe, "Sunny")
msgs_none  = fire_on_entry(c, foe, None)

import re
strip = lambda s: re.sub(r'\x1b\[[0-9;]*m', '', s)

assert len(msgs_rain)  == 1, f"Expected 1 msg in rain, got {len(msgs_rain)}"
assert len(msgs_sunny) == 0, f"Expected 0 msgs in sunny, got {len(msgs_sunny)}"
assert len(msgs_none)  == 0, f"Expected 0 msgs with no weather, got {len(msgs_none)}"
assert "Swift Swim" in msgs_rain[0], "Message should mention Swift Swim"
assert "Speed" in msgs_rain[0] or "speed" in msgs_rain[0], "Message should mention Speed"

print("PASS 1: Swift Swim on_entry fires exactly once in Rainy weather")
print(f"  Message: {strip(msgs_rain[0])}")
print("PASS 2: Swift Swim on_entry silent in Sunny and no-weather")
print("PASS 3: Message mentions ability name and speed effect")
print()
print("All Swift Swim feedback tests passed.")
