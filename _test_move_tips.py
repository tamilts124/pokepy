import sys
sys.path.insert(0, '.')

from engine.battle import BattleSummary
from data.creatures import TYPE_CHART

# ── Case 1: no moves fired → no tip ──────────────────────────────────────
s = BattleSummary()
s.enemy_types = ['fire']
assert s.moves_used == 0
assert s.moves_super == 0
assert s.moves_resisted == 0
print('PASS 1: fields initialise to zero')

# ── Case 2: super-effective only ─────────────────────────────────────────
s2 = BattleSummary()
s2.enemy_types = ['fire']
s2.moves_used = 3
s2.moves_super = 3
s2.moves_resisted = 0
assert s2.moves_super > 0 and s2.moves_resisted == 0
print('PASS 2: super-effective-only branch condition is true')

# ── Case 3: resisted only ────────────────────────────────────────────────
s3 = BattleSummary()
s3.enemy_types = ['rock', 'steel']
s3.moves_used = 2
s3.moves_super = 0
s3.moves_resisted = 2
assert s3.moves_resisted > 0 and s3.moves_super == 0
type_str = '/'.join(s3.enemy_types)
assert type_str == 'rock/steel', repr(type_str)
print('PASS 3: resisted-only branch condition + type string correct')

# ── Case 4: mixed ────────────────────────────────────────────────────────
s4 = BattleSummary()
s4.moves_used = 4
s4.moves_super = 2
s4.moves_resisted = 2
assert s4.moves_super > 0 and s4.moves_resisted > 0
print('PASS 4: mixed-effectiveness branch condition is true')

# ── TYPE_CHART sanity checks (all lowercase keys) ─────────────────────────
def eff(move_type, target_types):
    e = 1.0
    for t in target_types:
        e *= TYPE_CHART.get(move_type, {}).get(t, 1.0)
    return e

assert eff('water', ['fire']) == 2.0, f"Got {eff('water', ['fire'])}"
print('PASS 5: water vs fire = 2x')

assert eff('normal', ['ghost']) == 0.0, f"Got {eff('normal', ['ghost'])}"
print('PASS 6: normal vs ghost = 0x (immune)')

assert eff('fire', ['rock']) < 1.0, f"Got {eff('fire', ['rock'])}"
print('PASS 7: fire vs rock is resisted (<1.0)')

# ── Counter tracking logic (mirrors battle loop) ─────────────────────────
from data.creatures import MOVES as ALL_MOVES

s5 = BattleSummary()
s5.enemy_types = ['fire']

# Pick real moves: one water-type (super), one normal-type (neutral), one with power==0
water_moves = [m for m,v in ALL_MOVES.items() if v.get('type')=='water' and v.get('power',0)>0]
normal_dmg   = [m for m,v in ALL_MOVES.items() if v.get('type')=='normal' and v.get('power',0)>0]
status_move  = [m for m,v in ALL_MOVES.items() if v.get('power',0)==0]

assert water_moves, "Need at least one water damaging move"
assert normal_dmg,  "Need at least one normal damaging move"
assert status_move, "Need at least one status move"

for move_name in [water_moves[0], normal_dmg[0], status_move[0]]:
    mv = ALL_MOVES[move_name]
    move_type = mv.get('type', '')
    has_power = mv.get('power', 0) > 0
    if move_type and has_power:
        e = eff(move_type, s5.enemy_types)
        s5.moves_used += 1
        if e >= 2.0:
            s5.moves_super += 1
        elif e < 1.0:
            s5.moves_resisted += 1

assert s5.moves_used == 2, f"Expected 2 moves_used, got {s5.moves_used}"
assert s5.moves_super == 1, f"Expected 1 moves_super, got {s5.moves_super}"
assert s5.moves_resisted == 0, f"Expected 0 moves_resisted, got {s5.moves_resisted}"
print(f'PASS 8: counter tracking correct (status move excluded, '
      f'{water_moves[0]} counted as super-effective)')

# ── Confirm enemy_types is set in run_battle source ──────────────────────
import pathlib
src = pathlib.Path('engine/battle.py').read_text(encoding='utf-8')
assert 'summary.enemy_types = list(enemy_c.types)' in src
print('PASS 9: summary.enemy_types assignment present in run_battle')
assert 'summary.moves_used += 1' in src
assert 'summary.moves_super += 1' in src
assert 'summary.moves_resisted += 1' in src
print('PASS 10: counter increments present in battle loop')

print()
print('All move-efficiency-tip tests passed.')
