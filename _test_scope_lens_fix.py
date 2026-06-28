"""Verification: Scope Lens crit-chance bug fix.

held_item_crit_bonus() in engine/battle.py existed and was documented (item
desc + README) to double crit chance for a creature holding Scope Lens, but
was never actually called from calc_damage() -- a real, silent gameplay bug.
This test confirms it is now wired in and produces the documented ~2x rate.
"""
import sys, random
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from engine.core import Creature, calc_damage

attacker = Creature("Flambit", 20)
defender = Creature("Aquapup", 20)
move_name = "Scratch"

# Test 1: without Scope Lens, crit rate should be close to 1/16 (~6.25%)
random.seed(12345)
attacker.held_item = None
trials = 20000
crits = sum(1 for _ in range(trials) if calc_damage(attacker, defender, move_name)[2])
rate_no_item = crits / trials
assert 0.045 < rate_no_item < 0.085, f"baseline crit rate off: {rate_no_item}"
print(f"PASS 1: baseline crit rate ~{rate_no_item:.3f} (expected ~0.0625)")

# Test 2: with Scope Lens, crit rate should be close to 1/8 (~12.5%) -- roughly double
random.seed(12345)
attacker.held_item = "Scope Lens"
crits2 = sum(1 for _ in range(trials) if calc_damage(attacker, defender, move_name)[2])
rate_item = crits2 / trials
assert 0.10 < rate_item < 0.155, f"Scope Lens crit rate off: {rate_item}"
print(f"PASS 2: Scope Lens crit rate ~{rate_item:.3f} (expected ~0.125)")

assert rate_item > rate_no_item * 1.5, "Scope Lens should roughly double the crit rate"
print(f"PASS 3: Scope Lens rate ({rate_item:.3f}) is meaningfully higher than baseline ({rate_no_item:.3f})")

print("\nAll Scope Lens crit-bonus tests passed.")
