"""Verification for the friendship/bond system (Session 10 task)."""
import random
from engine.core import Creature, BASE_FRIENDSHIP, MAX_FRIENDSHIP, BOND_THRESHOLD, calc_damage

failures = []

def check(cond, msg):
    if not cond:
        failures.append(msg)

# 1. Default friendship + clamping
c = Creature("Flambit", 10)
check(c.friendship == BASE_FRIENDSHIP, f"default friendship should be {BASE_FRIENDSHIP}, got {c.friendship}")
delta = c.gain_friendship(50)
check(c.friendship == MAX_FRIENDSHIP, f"should clamp at {MAX_FRIENDSHIP}, got {c.friendship}")
check(delta == MAX_FRIENDSHIP - BASE_FRIENDSHIP, f"delta should reflect actual clamped gain, got {delta}")
d2 = c.gain_friendship(-1000)
check(c.friendship == 0, f"should clamp at 0, got {c.friendship}")

# 2. Persistence via to_dict/from_dict
c2 = Creature("Aquapup", 12)
c2.gain_friendship(15)
d = c2.to_dict()
check(d.get("friendship") == c2.friendship, "friendship missing/incorrect in to_dict()")
restored = Creature.from_dict(d)
check(restored.friendship == c2.friendship, "friendship not restored via from_dict()")

# Old-save fallback (no friendship key)
d_old = c2.to_dict()
del d_old["friendship"]
restored_old = Creature.from_dict(d_old)
check(restored_old.friendship == BASE_FRIENDSHIP, "old saves without friendship key should default to BASE_FRIENDSHIP")

# 3. Level-up grants +1 friendship
c3 = Creature("Leafling", 5)
c3.friendship = 50
before = c3.friendship
c3.gain_exp(c3.exp_to_next + 1)  # force at least one level-up
check(c3.friendship == before + 1, f"level-up should add +1 friendship, got {before}->{c3.friendship}")

# 4. Bond-save proc only triggers at/above threshold, only once per battle
random.seed(1)
atk = Creature("Drakling", 50)
atk.friendship = BOND_THRESHOLD
atk.hp = atk.max_hp
saved_any = False
for _ in range(500):
    atk.hp = atk.max_hp
    atk._bond_save_used = False
    atk.take_damage(atk.max_hp * 5)  # guaranteed lethal
    if atk.hp == 1:
        saved_any = True
        break
check(saved_any, "maxed-bond creature never procced the bond-save in 500 lethal-hit trials")

# Below threshold should never proc
random.seed(2)
atk2 = Creature("Drakling", 50)
atk2.friendship = BOND_THRESHOLD - 1
never_saved = True
for _ in range(500):
    atk2.hp = atk2.max_hp
    atk2._bond_save_used = False
    atk2.take_damage(atk2.max_hp * 5)
    if atk2.hp > 0:
        never_saved = False
        break
check(never_saved, "below-threshold creature should never proc the bond-save")

# Only once per battle (reset_stages clears it on switch)
atk3 = Creature("Drakling", 50)
atk3.friendship = BOND_THRESHOLD
atk3._bond_save_used = True
atk3.hp = atk3.max_hp
atk3.take_damage(atk3.max_hp * 5)
check(atk3.hp == 0, "bond-save should not re-proc within the same battle once already used")
atk3.reset_stages()
check(atk3._bond_save_used is False, "reset_stages() should clear _bond_save_used on switch")

# 5. Crit denom shrinks at max bond (statistical check via calc_damage)
random.seed(3)
attacker = Creature("Flambit", 50)
attacker.friendship = 0
defender = Creature("Aquapup", 50)
crits_low = sum(1 for _ in range(20000) if calc_damage(attacker, defender, "Ember")[2])
attacker.friendship = BOND_THRESHOLD
crits_high = sum(1 for _ in range(20000) if calc_damage(attacker, defender, "Ember")[2])
check(crits_high > crits_low * 1.15, f"maxed bond should noticeably raise crit rate: low={crits_low} high={crits_high}")

if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    raise SystemExit(1)
else:
    print(f"PASS: all friendship checks ok. crits_low={crits_low} crits_high={crits_high}")
