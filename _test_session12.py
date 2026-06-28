# -*- coding: utf-8 -*-
"""Session 12 feature verification tests.
   - Battle performance rating (_grade logic, player_start_hp wiring, show integration)
   - Money penalty on trainer loss (apply_loss_penalty, all call sites, break fix)
   - Fight menu: move category column (_cat_tag, wired in move_opts)
"""
import sys, re
sys.path.insert(0, '.')

# ── Test 1: _grade() boundary values ──────────────────────────────────────────
from engine.battle import BattleSummary

def make_s(turns, items, switches, dmg_taken, start_hp=100):
    s = BattleSummary()
    s.player_start_hp = start_hp
    s.turns = turns
    s.items_used = items
    s.switches = switches
    s.player_dmg_taken = dmg_taken
    return s

assert make_s(2, 0, 0, 5)._grade()[0]   == 'S', "FAIL: perfect run should be S"
assert make_s(5, 0, 0, 20)._grade()[0]  == 'A', "FAIL: 5-turn clean run should be A (82 pts)"
assert make_s(5, 1, 1, 20)._grade()[0]  == 'B', "FAIL: decent run should be B"
assert make_s(12, 3, 2, 80)._grade()[0] == 'C', "FAIL: rough run should be C"
print("PASS 1: _grade() returns S/A/B/C for perfect/clean/decent/rough runs")

# ── Test 2: grade shown in BattleSummary.show() ───────────────────────────────
battle_src = open('engine/battle.py', encoding='utf-8').read()
assert 'Performance' in battle_src,           "FAIL: 'Performance' label not in show()"
assert 'grade_color' in battle_src,           "FAIL: grade_color not in show()"
assert 'summary.player_start_hp = player_c.hp' in battle_src, "FAIL: player_start_hp not wired in run_battle"
print("PASS 2: grade shown in show(), player_start_hp wired")

# ── Test 3: apply_loss_penalty definition and formula ─────────────────────────
main_src = open('main.py', encoding='utf-8').read()
assert 'def apply_loss_penalty' in main_src,  "FAIL: method not defined"
assert 'max(100, min(1000, self.money // 10))' in main_src, "FAIL: penalty formula wrong"
print("PASS 3: apply_loss_penalty defined with correct formula")

# ── Test 4: call sites — gym, explore-trainer, E4, rival ──────────────────────
rival_src = open('engine/rival.py', encoding='utf-8').read()
main_calls = main_src.count('self.apply_loss_penalty()')
assert main_calls >= 3, f"FAIL: expected >=3 call sites in main.py, found {main_calls}"
assert 'game.apply_loss_penalty()' in rival_src, "FAIL: penalty not called on rival loss"
print(f"PASS 4: apply_loss_penalty called at {main_calls} site(s) in main.py + rival.py")

# ── Test 5: break after lost=True in trainer for-loop ─────────────────────────
# The pattern must have 'break' immediately after 'lost = True' in the trainer inner loop
pattern = r'elif result == "lose":\s+lost = True\s+break'
assert re.search(pattern, main_src), "FAIL: trainer for-loop missing break after lost=True"
print("PASS 5: trainer for-loop breaks after lost=True (no phantom battles)")

# ── Test 6: _cat_tag helper present and correct ────────────────────────────────
assert '_cat_tag' in battle_src,               "FAIL: _cat_tag helper not in battle.py"
assert 'cat == "physical"' in battle_src,      "FAIL: physical branch missing"
assert 'cat == "special"' in battle_src,       "FAIL: special branch missing"
assert 'Phys' in battle_src,                   "FAIL: Phys label missing"
assert 'Spec' in battle_src,                   "FAIL: Spec label missing"
assert 'Stat' in battle_src,                   "FAIL: Stat label missing"
print("PASS 6: _cat_tag helper defined with all three branches")

# ── Test 7: _cat_tag used in move_opts f-string ───────────────────────────────
assert "_cat_tag(MOVES[m].get('category'" in battle_src, "FAIL: _cat_tag not used in move_opts"
print("PASS 7: _cat_tag used in move_opts f-string")

# ── Test 8: compile clean ─────────────────────────────────────────────────────
import py_compile
for f in ['engine/battle.py', 'engine/rival.py', 'main.py']:
    py_compile.compile(f, doraise=True)
print("PASS 8: py_compile clean on all three touched files")

print()
print("All session-12 tests passed.")
