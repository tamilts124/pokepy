# -*- coding: utf-8 -*-
"""Session 13 — Test: Inn full heal vs cheaper partial heal."""
import sys, py_compile, re
sys.path.insert(0, '.')

# ── 1: compile clean ────────────────────────────────────────────────────────
py_compile.compile('main.py', doraise=True)
print("PASS 1: py_compile clean on main.py")

src = open('main.py', encoding='utf-8').read()

# ── 2: visit_inn computes a partial_cost ────────────────────────────────────
m = re.search(r'def visit_inn\(self, cost\):(.*?)\n    def ', src, re.DOTALL)
assert m, "FAIL: could not isolate visit_inn() body"
body = m.group(1)
assert 'partial_cost = max(1, cost // 2)' in body, \
    "FAIL: partial_cost not computed as half of full cost (min 1)"
print("PASS 2: partial_cost = max(1, cost // 2)")

# ── 3: player is offered a 3-way choice when there's something to heal ─────
assert 'inn_opts = [' in body, "FAIL: inn_opts menu list not built"
assert 'Full Heal' in body and 'Partial Heal' in body and 'Cancel' in body, \
    "FAIL: menu missing one of Full Heal / Partial Heal / Cancel"
assert 'menu("How would you like to rest?", inn_opts)' in body, \
    "FAIL: menu() not called with inn_opts"
print("PASS 3: 3-way Full/Partial/Cancel menu presented")

# ── 4: cancel path returns without charging ─────────────────────────────────
assert 'if ic == 2:\n                return' in body, \
    "FAIL: cancel (index 2) does not return immediately"
print("PASS 4: cancel option exits without paying")

# ── 5: correct price charged per mode ───────────────────────────────────────
assert 'pay = cost if heal_mode == "full" else partial_cost' in body, \
    "FAIL: payment amount not branched on heal_mode"
assert 'self.money -= pay' in body, "FAIL: self.money not deducted by 'pay'"
print("PASS 5: correct price (full or partial) deducted from money")

# ── 6: full heal still does everything it used to ───────────────────────────
assert 'c.hp     = c.max_hp' in body and 'c.status = None' in body, \
    "FAIL: full heal no longer restores HP/cures status"
assert 'c.pp     = {m: MOVE_DATA[m]["pp"] for m in c.moves}' in body, \
    "FAIL: full heal no longer restores PP"
print("PASS 6: full heal still restores HP, cures status, restores PP")

# ── 7: partial heal restores ~50% of missing HP only, no status/PP touch ───
# Isolate ONLY the else (partial-heal) branch, not the preceding full-heal branch.
parts = body.split('        else:\n            for c in self.team:\n                missing')
assert len(parts) == 2, "FAIL: could not isolate the partial-heal else branch"
partial_branch = parts[1]
assert ' = c.max_hp - c.hp' in partial_branch, \
    "FAIL: partial heal does not compute missing HP"
assert '(missing + 1) // 2' in partial_branch, \
    "FAIL: partial heal does not use ceil-50% formula"
assert 'c.status' not in partial_branch, \
    "FAIL: partial heal branch touches c.status (should leave it alone)"
assert 'c.pp' not in partial_branch, \
    "FAIL: partial heal branch touches c.pp (should leave it alone)"
print("PASS 7: partial heal restores ceil(missing/2) HP only, status/PP untouched")

# ── 8: insufficient-money guard uses the right price ────────────────────────
assert 'if self.money < pay:' in body, \
    "FAIL: money check does not use the mode-specific 'pay' amount"
print("PASS 8: insufficient-funds check uses mode-specific price")

# ── 9: numeric spot check of the ceil-50% formula ───────────────────────────
cases = [(10, 0, 5), (10, 7, 9), (1, 0, 1), (9, 0, 5)]
for max_hp, hp, expected in cases:
    missing = max_hp - hp
    gained = min(max_hp, hp + (missing + 1) // 2)
    assert gained == expected, \
        f"FAIL: max_hp={max_hp} hp={hp} -> {gained}, expected {expected}"
print("PASS 9: ceil(missing/2) formula matches hand-computed expected values")

# ── 10: already-fully-healed team keeps the old single-confirm behaviour ───
assert 'heal_mode = "full"' in body.split('if not anything_to_heal:')[1].split('else:')[0], \
    "FAIL: already-full-health path no longer defaults to a full heal_mode"
print("PASS 10: already-full team keeps the simple 'pay anyway' full-heal path")

print("\nAll Inn partial-heal tests passed.")
