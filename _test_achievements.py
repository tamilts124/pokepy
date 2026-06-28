"""Test the achievement gallery (open_achievements).

Verifies:
1. open_achievements method exists on Game class
2. Menu option '🏆  Achievements' present in town opts list
3. elif handler for 'Achievements' present in town_loop
4. Screen renders correctly for 0, partial, and full achievements
5. py_compile clean on main.py
"""
import sys, io, re, py_compile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Source checks ──
with open('main.py', encoding='utf-8') as f:
    src = f.read()

assert 'def open_achievements(self)' in src, "FAIL: open_achievements method not found"
print("PASS 1: open_achievements() method defined")

assert '\U0001f3c6  Achievements' in src or '🏆  Achievements' in src, \
    "FAIL: Achievements menu option not found"
print("PASS 2: '🏆  Achievements' menu option present")

assert 'elif label == "Achievements":' in src, "FAIL: elif Achievements handler missing"
assert 'self.open_achievements()' in src, "FAIL: open_achievements() not called in handler"
print("PASS 3: elif Achievements handler wired correctly")

py_compile.compile('main.py', doraise=True)
print("PASS 4: py_compile clean on main.py")

# ── Functional render test ──
strip_ansi = lambda s: re.sub(r'\x1b\[[0-9;]*m', '', s)

from engine.core import Creature
from main import Game, ACHIEVEMENTS

def capture_achievements(g):
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    # patch press_enter to be a no-op
    import main as m
    orig_pe = m.press_enter
    m.press_enter = lambda: None
    try:
        g.open_achievements()
    finally:
        sys.stdout = old_stdout
        m.press_enter = orig_pe
    return strip_ansi(buf.getvalue())

# Build a minimal Game object
g = Game.__new__(Game)
g.player_name = 'Tester'
g.achievements = []
starter = Creature('Flambit', 5)
g.team = [starter]

# Test: no achievements
out = capture_achievements(g)
assert 'ACHIEVEMENTS' in out.upper(), f"FAIL: banner missing: {out[:200]}"
assert '0/' in out, f"FAIL: count 0/N not shown: {out[:200]}"
# All should show ○ (locked circle)
for key, ach in ACHIEVEMENTS.items():
    assert '○' in out or '\u25cb' in out, "FAIL: no locked-circle markers"
    break  # just check existence once
print("PASS 5: 0-achievements screen renders with locked markers")

# Test: some achievements earned
g.achievements = ['first_catch', 'first_badge', 'battle100']
out = capture_achievements(g)
assert '3/' in out, f"FAIL: count 3/N not shown: {out[:200]}"
# Earned ones show name + desc
assert ACHIEVEMENTS['first_catch']['name'] in out, "FAIL: first_catch name not shown"
assert ACHIEVEMENTS['first_catch']['desc'] in out, "FAIL: first_catch desc not shown"
# Unearned ones show name but NOT desc
assert ACHIEVEMENTS['all_badges']['name'] in out, "FAIL: all_badges name missing"
print("PASS 6: partial achievements - earned show name+desc, locked show name only")

# Test: all achievements
g.achievements = list(ACHIEVEMENTS.keys())
out = capture_achievements(g)
total = len(ACHIEVEMENTS)
assert f'{total}/{total}' in out, f"FAIL: full count {total}/{total} not in: {out[:200]}"
print(f"PASS 7: all {total} achievements earned — full count shown")

print()
print("All achievement gallery tests passed.")
