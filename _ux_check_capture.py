"""Tester-role UX check: render the actual capture+bag flow text as a player would see it."""
import sys, random
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from engine.core import Creature, ITEMS
from engine.battle import animated_capture
from ui.display import C

random.seed(5)

print("=== Scenario A: maxed-bond lead, Great Ball ===")
lead = Creature("Flambit", 20)
lead.friendship = 100
wild = Creature("Aquapup", 8, is_player=False)
wild.hp = max(1, wild.max_hp // 5)
caught, shakes = animated_capture(wild, "Great Ball", ITEMS["Great Ball"]["rate"], lead=lead)
print(f"--> caught={caught} shakes={shakes}\n")

print("=== Scenario B: low-friendship lead (no flavor line expected), same ball ===")
random.seed(5)
lead2 = Creature("Flambit", 20)
lead2.friendship = 70
wild2 = Creature("Aquapup", 8, is_player=False)
wild2.hp = max(1, wild2.max_hp // 5)
caught2, shakes2 = animated_capture(wild2, "Great Ball", ITEMS["Great Ball"]["rate"], lead=lead2)
print(f"--> caught={caught2} shakes={shakes2}\n")

print("=== Scenario C: bag menu listing with a mixed inventory ===")
usable = {"Potion": 3, "Great Ball": 5, "Full Heal": 1, "Rare Candy": 2, "X Speed": 1}
bag_opts = [f"{item} x{qty}  {C.GRAY}({ITEMS[item]['desc']}){C.RESET}" for item, qty in usable.items()]
bag_opts.append("\u2190 Back")
for i, opt in enumerate(bag_opts):
    print(f"  {i+1}. {opt}")
