# -*- coding: utf-8 -*-
"""Session 13 — Test: Gym leader pre-battle type preview."""
import sys, py_compile, re
sys.path.insert(0, '.')

# ── 1: compile clean ────────────────────────────────────────────────────────
for f in ['main.py', 'data/creatures.py']:
    py_compile.compile(f, doraise=True)
print("PASS 1: py_compile clean on main.py and data/creatures.py")

# ── 2: all 7 gyms have a 'type' key ─────────────────────────────────────────
from data.creatures import TOWNS
EXPECTED = {
    "Greenpath":   "grass",
    "Stonepeak":   "rock",
    "Ashveil":     "fire",
    "Frostholm":   "ice",
    "Mistveil":    "psychic",
    "Shadowmere":  "ghost",
    "Dragonspire": "dragon",
}
for town, expected_type in EXPECTED.items():
    gym = TOWNS[town].get("gym", {})
    assert "type" in gym, f"FAIL: {town} gym missing 'type' key"
    assert gym["type"] == expected_type, (
        f"FAIL: {town} gym type={gym['type']!r}, expected {expected_type!r}"
    )
print("PASS 2: all 7 gyms have correct 'type' field")

# ── 3: TYPE_CHART imported at top level of main.py ──────────────────────────
src = open('main.py', encoding='utf-8').read()
assert 'TYPE_CHART' in src and 'from data.creatures import' in src, \
    "FAIL: TYPE_CHART not imported in main.py"
# Must appear on the data.creatures import block
dc_block = re.search(
    r'from data\.creatures import.*?(?=\nfrom |\Z)', src, re.DOTALL
)
assert dc_block and 'TYPE_CHART' in dc_block.group(), \
    "FAIL: TYPE_CHART not in data.creatures import block"
print("PASS 3: TYPE_CHART imported from data.creatures")

# ── 4: TYPE_COLORS imported from ui.display ─────────────────────────────────
ud_block = re.search(
    r'from ui\.display.*?import.*?(?=\n\n|\Z)', src, re.DOTALL
)
assert ud_block and 'TYPE_COLORS' in ud_block.group(), \
    "FAIL: TYPE_COLORS not imported from ui.display"
print("PASS 4: TYPE_COLORS imported from ui.display")

# ── 5: challenge_gym shows type preview ─────────────────────────────────────
assert 'gym_type = gym_data.get("type"' in src or "gym_type = gym_data.get('type'" in src, \
    "FAIL: gym_type not extracted in challenge_gym"
assert 'Specialist type' in src, \
    "FAIL: 'Specialist type' label not in challenge_gym"
assert 'Weak to' in src, \
    "FAIL: 'Weak to' label not in challenge_gym"
assert 'Team size' in src or 'n_creatures' in src, \
    "FAIL: team size not shown in challenge_gym"
print("PASS 5: challenge_gym shows type preview, weaknesses, team size")

# ── 6: TYPE_CHART used to compute weaknesses (not hard-coded) ───────────────
assert 'TYPE_CHART[atk].get(gym_type' in src or "TYPE_CHART.get(atk" in src, \
    "FAIL: weaknesses not computed live from TYPE_CHART"
print("PASS 6: weaknesses computed live from TYPE_CHART")

# ── 7: town_loop gym option includes type tag ────────────────────────────────
assert 'gtype' in src and 'type_tag' in src, \
    "FAIL: type_tag not added to gym option in town_loop"
assert (
    "gym'].get(\"type\"" in src
    or "gym'].get('type'" in src
    or 'gym"].get("type"' in src
    or "gym\"].get('type'" in src
), "FAIL: gtype not read from gym dict in town_loop"
print("PASS 7: town_loop gym menu option includes colored type tag")

# ── 8: gym handler still uses startswith("Gym") ─────────────────────────────
assert 'label.startswith("Gym")' in src or "label.startswith('Gym')" in src, \
    "FAIL: gym handler lost its startswith check"
print("PASS 8: gym label handler still uses startswith check (routing unbroken)")

# ── 9: weaknesses are capped at 4 ───────────────────────────────────────────
assert 'weaknesses[:4]' in src, \
    "FAIL: weaknesses not capped at 4 in challenge_gym"
print("PASS 9: weakness list capped at 4 entries")

# ── 10: spot-check computed weaknesses for fire gym ─────────────────────────
from data.creatures import TYPE_CHART
fire_weaknesses = sorted(
    atk for atk in TYPE_CHART if TYPE_CHART[atk].get("fire", 1.0) >= 2.0
)
assert "water" in fire_weaknesses, "FAIL: water not a weakness of fire"
assert "rock" in fire_weaknesses,  "FAIL: rock not a weakness of fire"
print(f"PASS 10: fire gym weaknesses computed correctly: {fire_weaknesses}")

print("\nAll gym type preview tests passed.")
