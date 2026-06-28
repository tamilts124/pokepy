"""Tester-role UX check: capture flow with multiple shakes, to see combined flavor+hint text."""
import sys, random
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from engine.core import Creature, ITEMS
from engine.battle import animated_capture

for seed in range(1, 8):
    random.seed(seed)
    lead = Creature("Aquapup", 20)
    lead.friendship = 100
    wild = Creature("Leafling", 10, is_player=False)
    wild.hp = max(1, wild.max_hp // 4)
    print(f"--- seed {seed} ---")
    caught, shakes = animated_capture(wild, "Ultra Ball", ITEMS["Ultra Ball"]["rate"], lead=lead)
    print(f"caught={caught} shakes={shakes}\n")
