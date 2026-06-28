"""Test weather ability verbal feedback: Swift Swim on_entry + Blaze/Overgrow/Torrent notices."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from engine.core import Creature
from engine.battle import fire_on_entry, fire_end_of_turn, _starter_ability_notice

strip = lambda s: re.sub(r'\x1b\[[0-9;]*m', '', s)

# ── Test 1: Swift Swim on_entry in rain ──
class FakeC:
    ability = "Swift Swim"; name = "Wavefin"; nickname = None; _battle_tag = "Your"

c = FakeC(); foe = FakeC(); foe.name = "Rockshell"
msgs = fire_on_entry(c, foe, "Rainy")
assert len(msgs) == 1 and "Swift Swim" in msgs[0], f"FAIL: {msgs}"
print(f"PASS 1: Swift Swim fires in rain: {strip(msgs[0]).strip()}")

# ── Test 2: Swift Swim silent outside rain ──
assert fire_on_entry(c, foe, "Sunny") == []
assert fire_on_entry(c, foe, None)    == []
print("PASS 2: Swift Swim silent when not raining")

# ── Test 3: Blaze one-shot notice when HP drops to 1/3 ──
flambit = Creature("Flambit", 10)
flambit._battle_tag = "Your"
flambit.reset_stages()                 # ensures flag initialized
flambit.hp = flambit.max_hp            # full HP — should NOT notify
msgs = fire_end_of_turn(flambit, None)
assert msgs == [], f"FAIL: should be silent at full HP, got {msgs}"

flambit.hp = flambit.max_hp // 3      # exactly 1/3 — threshold
msgs = fire_end_of_turn(flambit, None)
assert len(msgs) == 1, f"FAIL: expected 1 notice, got {len(msgs)}"
assert "Blaze" in msgs[0], f"FAIL: message should mention Blaze: {msgs[0]}"
print(f"PASS 3: Blaze notice fires at 1/3 HP: {strip(msgs[0]).strip()}")

# ── Test 4: Blaze fires ONLY ONCE (flag prevents repeat) ──
msgs2 = fire_end_of_turn(flambit, None)
assert msgs2 == [], f"FAIL: should not fire again, got {msgs2}"
print("PASS 4: Blaze notice fires only once per battle (flag suppresses repeat)")

# ── Test 5: Blaze flag resets on switch (reset_stages) ──
flambit.reset_stages()
msgs3 = fire_end_of_turn(flambit, None)   # still at low HP
assert len(msgs3) == 1, f"FAIL: should fire again after switch, got {msgs3}"
print("PASS 5: Blaze re-fires after switch-in (reset_stages clears flag)")

# ── Test 6: Overgrow and Torrent also work ──
for species, ability in [("Leafling", "Overgrow"), ("Aquapup", "Torrent")]:
    cr = Creature(species, 10)
    cr._battle_tag = "Your"
    cr.reset_stages()
    cr.hp = cr.max_hp   # full HP, no msg
    assert fire_end_of_turn(cr, None) == []
    cr.hp = cr.max_hp // 4   # well below 1/3
    msgs = fire_end_of_turn(cr, None)
    assert len(msgs) == 1 and ability in msgs[0], f"FAIL {ability}: {msgs}"
    print(f"PASS 6: {ability} notice fires correctly: {strip(msgs[0]).strip()}")

print()
print("All weather-ability feedback tests passed.")
