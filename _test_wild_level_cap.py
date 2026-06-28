# -*- coding: utf-8 -*-
"""Session 13 — Test: hard cap on badge-boosted wild encounter levels."""
import sys, py_compile, re, random
sys.path.insert(0, '.')

# ── 1: compile clean ────────────────────────────────────────────────────────
for f in ['main.py', 'engine/core.py']:
    py_compile.compile(f, doraise=True)
print("PASS 1: py_compile clean on main.py and engine/core.py")

from engine.core import capped_wild_level, random_wild, WILD_AREAS

# ── 2: no badge bonus -> behaves exactly like the original randint(lo, hi) ────
random.seed(42)
seen = set()
for _ in range(500):
    seen.add(capped_wild_level(3, 8, badge_bonus=0))
assert seen == set(range(3, 9)), f"FAIL: zero-bonus range wrong, got {sorted(seen)}"
print("PASS 2: badge_bonus=0 reproduces the original [lo, hi] range exactly")

# ── 3: moderate bonus shifts the whole range up, no cap engaged ───────────
random.seed(42)
seen = set()
for _ in range(500):
    seen.add(capped_wild_level(3, 8, badge_bonus=5))
assert seen == set(range(8, 14)), f"FAIL: +5 bonus range wrong, got {sorted(seen)}"
print("PASS 3: moderate badge_bonus shifts range up uncapped (cap not yet reached)")

# ── 4: hard cap engages at 2x hi for an extreme bonus on an early area ───────
random.seed(42)
seen = set()
for _ in range(1000):
    seen.add(capped_wild_level(3, 8, badge_bonus=15))  # max possible bonus (7 badges)
assert max(seen) == 16, f"FAIL: cap should be 2*hi=16, got max {max(seen)}"
assert min(seen) >= 1, f"FAIL: level dropped below 1, got min {min(seen)}"
print(f"PASS 4: max badge_bonus (15) on Lv.3-8 area caps at 16 (2x hi), got range {sorted(seen)}")

# ── 5: extreme bonus on a single-level pool (lo==hi) never crashes ───────────
for _ in range(200):
    lv = capped_wild_level(8, 8, badge_bonus=15)
    assert lv == 16, f"FAIL: single-level pool with extreme bonus should pin at 16, got {lv}"
print("PASS 5: single-level pool (lo==hi) with extreme bonus pins at cap, no crash")

# ── 6: late-game area (high hi) is barely affected by the cap ────────────────
random.seed(1)
seen = set()
for _ in range(500):
    seen.add(capped_wild_level(40, 48, badge_bonus=15))
assert max(seen) <= 96, "FAIL: late-game cap (2*48=96) should never be exceeded"
assert max(seen) == 63, f"FAIL: late-game range should reach 63 (48+15) uncapped, got {max(seen)}"
print("PASS 6: late-game area (hi=48) unaffected by cap at max badge_bonus (63 < 96 cap)")

# ── 7: random_wild() in core.py actually uses the capped helper (real area data) ───
name_lo_hi = []
for area, pool in WILD_AREAS.items():
    for name, lo, hi in pool:
        name_lo_hi.append((area, name, lo, hi))
assert name_lo_hi, "FAIL: WILD_AREAS appears empty"
worst = max(name_lo_hi, key=lambda t: t[3] - t[2] if t[3] == min(h for _,_,_,h in name_lo_hi) else -1)
# Pick the area with the smallest base hi (most exposed to the cap) and hammer it.
min_hi_entry = min(name_lo_hi, key=lambda t: t[3])
area, name, lo, hi = min_hi_entry
for _ in range(300):
    wild = random_wild(area, badge_bonus=15)
    if wild and wild.name == name:
        assert wild.level <= hi * 2, (
            f"FAIL: random_wild produced Lv.{wild.level} for {name} in {area}, "
            f"exceeding cap of {hi*2} (base hi={hi})"
        )
print(f"PASS 7: random_wild() on the most-exposed area ({area}, base hi={hi}) "
      f"never exceeds the {hi*2} cap even at max badge_bonus")

# ── 8: all 4 main.py call sites were migrated off the raw uncapped formula ─────
src = open('main.py', encoding='utf-8').read()
assert 'random.randint(lo + badge_bonus, hi + badge_bonus)' not in src, \
    "FAIL: an uncapped wild-level roll still exists in main.py"
assert src.count('capped_wild_level(lo, hi, badge_bonus)') == 4, \
    f"FAIL: expected 4 call sites using capped_wild_level, found {src.count('capped_wild_level(lo, hi, badge_bonus)')}"
print("PASS 8: all 4 main.py wild-level call sites migrated to capped_wild_level()")

# ── 9: trainer-team level scaling (not a wild range) is untouched ────────────
assert 'enemy = Creature(cname, lv + badge_bonus, is_player=False)' in src, \
    "FAIL: trainer-team badge scaling should remain a flat lv+badge_bonus (out of scope)"
print("PASS 9: trainer-team level scaling correctly left untouched (different mechanic)")

print("\nAll wild encounter level-cap tests passed.")
