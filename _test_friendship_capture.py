"""Verification for friendship-aware capture rate (Session 11 follow-on task)."""
import random
from engine.core import (Creature, try_capture, friendship_capture_bonus,
                          FRIENDSHIP_CAPTURE_THRESHOLD, FRIENDSHIP_CAPTURE_MAX_BONUS,
                          MAX_FRIENDSHIP)

failures = []

def check(cond, msg):
    if not cond:
        failures.append(msg)

# 1. No lead -> no bonus
check(friendship_capture_bonus(None) == 1.0, "no lead should give a 1.0x multiplier")

# 2. Below threshold -> no bonus
low = Creature("Flambit", 10)
low.friendship = FRIENDSHIP_CAPTURE_THRESHOLD - 1
check(friendship_capture_bonus(low) == 1.0, "below-threshold friendship should give 1.0x")

# 3. At threshold -> no bonus (boundary is exclusive of any bonus, starts scaling above it)
at = Creature("Flambit", 10)
at.friendship = FRIENDSHIP_CAPTURE_THRESHOLD
check(friendship_capture_bonus(at) == 1.0, "exactly at threshold should give 1.0x (bonus starts above it)")

# 4. At max friendship -> max bonus, capped
maxed = Creature("Flambit", 10)
maxed.friendship = MAX_FRIENDSHIP
bonus = friendship_capture_bonus(maxed)
check(abs(bonus - (1.0 + FRIENDSHIP_CAPTURE_MAX_BONUS)) < 1e-9,
      f"max friendship should give exactly 1.0+{FRIENDSHIP_CAPTURE_MAX_BONUS}x, got {bonus}")

# 5. Scales monotonically between threshold and max
mid = Creature("Flambit", 10)
mid.friendship = (FRIENDSHIP_CAPTURE_THRESHOLD + MAX_FRIENDSHIP) // 2
mid_bonus = friendship_capture_bonus(mid)
check(1.0 < mid_bonus < (1.0 + FRIENDSHIP_CAPTURE_MAX_BONUS),
      f"mid-range friendship bonus should be strictly between 1.0 and max, got {mid_bonus}")

# 6. try_capture's default (no lead kwarg) behaves exactly as before — no crash, no bonus
wild = Creature("Aquapup", 5, is_player=False)
random.seed(42)
caught_a, shakes_a = try_capture(wild, 1.0)
random.seed(42)
caught_b, shakes_b = try_capture(wild, 1.0, lead=None)
check((caught_a, shakes_a) == (caught_b, shakes_b), "try_capture with no lead arg should match lead=None exactly")

# 7. Deterministic check: with identical RNG streams, a higher effective ball_rate
#    (i.e. with a maxed-bond lead) must never do worse and should do better at least
#    once across many borderline trials, since try_capture's shake rolls are monotonic
#    in the ball rate for a fixed RNG draw.
wild2 = Creature("Aquapup", 30, is_player=False)
wild2.hp = max(1, wild2.max_hp // 10)  # low HP so the 'a' formula has enough magnitude
                                        # for the friendship bonus to survive int() truncation
trials = 2000
caught_no_lead = 0
caught_with_lead = 0
strictly_better_once = False
for i in range(trials):
    random.seed(1000 + i)
    c1, s1 = try_capture(wild2, 1.0)
    random.seed(1000 + i)
    c2, s2 = try_capture(wild2, 1.0, lead=maxed)
    caught_no_lead += c1
    caught_with_lead += c2
    check(s2 >= s1, f"trial {i}: bonded lead (higher rate) produced fewer shakes than no-lead ({s2} < {s1})")
    if s2 > s1:
        strictly_better_once = True
    # With identical RNG draws, the higher effective rate must never catch less often
    check(not (c1 and not c2), f"trial {i}: no-lead caught but bonded-lead (higher rate) did not")
check(strictly_better_once,
      f"bonded lead should raise the shake count in at least one borderline trial across {trials} runs")



if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    raise SystemExit(1)
else:
    print(f"PASS: all friendship-capture checks ok. "
          f"no_lead={caught_no_lead} with_lead={caught_with_lead} (out of {trials})")
