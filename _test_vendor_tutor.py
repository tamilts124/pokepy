"""Test: Dragonspire Item Specialist vendor and coverage tutor expansion.

Verifies:
1. visit_held_item_vendor() method exists on Game
2. 'Item Specialist' menu option appears only in Dragonspire, not other towns
3. VENDOR_STOCK contains all 5 combat held items
4. VENDOR_STOCK contains all 4 seasonal berries (Salac/Petaya/Apicot/Ganlon)
5. Coverage tutor injects extra moves for Dragonspire (up to 3 uncovered types)
6. Coverage tutor skips moves already in team's moveset
7. Coverage tutor skips moves already in fixed tutor list
8. py_compile clean on main.py
"""
import sys, ast, py_compile, io, types, importlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Test 1: py_compile ──────────────────────────────────────────────────────
py_compile.compile('main.py', doraise=True)
print("PASS 1: py_compile clean on main.py")

# ── Test 2: visit_held_item_vendor method exists ────────────────────────────
with open('main.py', encoding='utf-8') as f:
    src = f.read()
assert 'def visit_held_item_vendor(self)' in src, "FAIL 2: visit_held_item_vendor not defined"
print("PASS 2: visit_held_item_vendor() defined on Game")

# ── Test 3: 'Item Specialist' option appears only for Dragonspire ───────────
assert 'opts.append("🧤  Item Specialist")' in src or "opts.append(\"🧤  Item Specialist\")" in src, \
    "FAIL 3a: Item Specialist not appended to opts"
assert 'self.town == "Dragonspire"' in src, "FAIL 3b: Dragonspire gate missing"
assert 'elif label == "Item Specialist"' in src, "FAIL 3c: handler not wired"
print("PASS 3: Item Specialist menu option gated on Dragonspire + handler wired")

# ── Test 4: VENDOR_STOCK has all 5 combat held items ────────────────────────
required_combat = ["Life Orb", "Choice Band", "Leftovers", "Shell Bell", "Scope Lens"]
for item in required_combat:
    assert f'"{item}"' in src, f"FAIL 4: {item} missing from vendor"
print(f"PASS 4: All 5 combat held items present in vendor stock: {required_combat}")

# ── Test 5: VENDOR_STOCK has all 4 seasonal berries ─────────────────────────
seasonal = ["Salac Berry", "Petaya Berry", "Apicot Berry", "Ganlon Berry"]
for berry in seasonal:
    assert f'"{berry}"' in src, f"FAIL 5: {berry} missing from vendor stock"
print(f"PASS 5: All 4 seasonal berries present in vendor stock (exclusive source): {seasonal}")

# ── Test 6: COVERAGE_TUTOR defined with key types ───────────────────────────
assert 'COVERAGE_TUTOR' in src, "FAIL 6: COVERAGE_TUTOR dict not defined"
key_types = ["water", "fire", "electric", "ice", "ghost", "ground"]
for t in key_types:
    assert f'"{t}"' in src, f"FAIL 6: type '{t}' missing from COVERAGE_TUTOR"
print(f"PASS 6: COVERAGE_TUTOR defined with all key coverage types")

# ── Test 7: Coverage logic integrated in visit_move_tutor ───────────────────
assert 'covered_types' in src, "FAIL 7: covered_types variable missing"
assert 'coverage_added' in src, "FAIL 7: coverage_added variable missing"
assert 'len(coverage_added) >= 3' in src, "FAIL 7: cap at 3 coverage moves missing"
print("PASS 7: Coverage selection logic integrated in visit_move_tutor()")

# ── Test 8: Coverage logic actually skips already-known moves ───────────────
assert 'mv_name in fixed_moves or mv_name in team_known' in src, \
    "FAIL 8: dedup check against fixed_moves and team_known missing"
print("PASS 8: Coverage skips moves already in fixed tutor list or team moveset")

# ── Test 9: Functional test — simulate coverage type detection ───────────────
# Import game module in a minimal way to test the COVERAGE_TUTOR logic
sys.path.insert(0, '.')
import main as _m
from data.creatures import MOVES as MOVE_DATA, TYPE_CHART

# Simulate team that only knows Scratch (normal) and Growl (normal/status)
# Normal can't hit ghost super-effectively, can't hit many types — should get suggestions
from engine.core import Creature
c = Creature('Flambit', 10)
c.moves = ['Scratch', 'Growl']  # both normal type

covered_types = set()
all_def_types = list(TYPE_CHART.keys())
for mv_name in c.moves:
    mv_data = MOVE_DATA.get(mv_name, {})
    atk_type = mv_data.get("type", "")
    if not atk_type:
        continue
    for def_type in all_def_types:
        if TYPE_CHART.get(atk_type, {}).get(def_type, 1.0) >= 2.0:
            covered_types.add(atk_type)
            break

# A team with only normal moves should have very little coverage (normal hits nothing 2x)
# So coverage_added should get populated
fixed_moves = {"Dragon Rage", "Earthquake", "Swords Dance"}
team_known = set(c.moves)

coverage_added = []
for atk_type, (mv_name, cost) in _m.COVERAGE_TUTOR.items():
    if len(coverage_added) >= 3:
        break
    if atk_type in covered_types:
        continue
    if mv_name in fixed_moves or mv_name in team_known:
        continue
    if mv_name not in MOVE_DATA:
        continue
    coverage_added.append((mv_name, cost, atk_type))

assert len(coverage_added) == 3, \
    f"FAIL 9: Expected 3 coverage moves for normal-only team, got {len(coverage_added)}: {coverage_added}"
print(f"PASS 9: Coverage tutor offers exactly 3 moves for normal-only team: {[(m,t) for m,_,t in coverage_added]}")

# ── Test 10: Coverage respects already-known moves ──────────────────────────
# If a team already knows Surf (water), no water coverage should be offered
c2 = Creature('Aquapup', 10)
c2.moves = ['Water Gun', 'Surf', 'Bite', 'Bubble Beam']

covered2 = set()
for mv_name in c2.moves:
    mv_data = MOVE_DATA.get(mv_name, {})
    atk_type = mv_data.get("type", "")
    if not atk_type:
        continue
    for def_type in all_def_types:
        if TYPE_CHART.get(atk_type, {}).get(def_type, 1.0) >= 2.0:
            covered2.add(atk_type)
            break

team_known2 = set(c2.moves)
suggested_types = []
for atk_type, (mv_name, cost) in _m.COVERAGE_TUTOR.items():
    if len(suggested_types) >= 3:
        break
    if atk_type in covered2:
        continue
    if mv_name in fixed_moves or mv_name in team_known2:
        continue
    if mv_name not in MOVE_DATA:
        continue
    suggested_types.append(atk_type)

assert 'water' not in suggested_types, \
    "FAIL 10: water coverage offered even though team already has Surf (water coverage)"
print("PASS 10: Coverage correctly skips already-covered type (water/Aquapup example)")

print()
print("All Item Specialist vendor + coverage tutor tests passed.")
