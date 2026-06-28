"""Test status condition duration display in creature_card."""
import sys, io, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from engine.core import Creature
from ui.display import creature_card

strip = lambda s: re.sub(r'\x1b\[[0-9;]*m', '', s)

def capture_card(c):
    """Capture creature_card output as a plain string."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    creature_card(c, prefix="  ")
    sys.stdout = old
    return strip(buf.getvalue())

# ── Build a test creature ──
c = Creature("Flambit", 10)
c._battle_tag = "Your"

# ── Test 1: no status → no badge ──
c.status = None
out = capture_card(c)
assert "[SLP" not in out and "[CNF" not in out, f"FAIL: unexpected badge with no status:\n{out}"
print("PASS 1: no status — no badge shown")

# ── Test 2: sleep with 2 turns remaining ──
c.status = "sleep"
c.sleep_turns = 2
out = capture_card(c)
assert "[SLP-2]" in out, f"FAIL: expected [SLP-2] in card, got:\n{out}"
print(f"PASS 2: sleep 2 turns → [SLP-2] shown")

# ── Test 3: sleep with 1 turn remaining ──
c.sleep_turns = 1
out = capture_card(c)
assert "[SLP-1]" in out, f"FAIL: expected [SLP-1] in card, got:\n{out}"
print("PASS 3: sleep 1 turn  → [SLP-1] shown")

# ── Test 4: sleep_turns=0 (wake-up edge) → shows plain [SLP] ──
c.sleep_turns = 0
out = capture_card(c)
assert "[SLP]" in out, f"FAIL: expected [SLP] when turns=0, got:\n{out}"
assert "[SLP-0]" not in out, f"FAIL: should not show -0, got:\n{out}"
print("PASS 4: sleep_turns=0 → [SLP] (no counter), not [SLP-0]")

# ── Test 5: confusion with 4 turns remaining ──
c.status = "confuse"
c.confusion_turns = 4
out = capture_card(c)
assert "[CNF-4]" in out, f"FAIL: expected [CNF-4], got:\n{out}"
print("PASS 5: confuse 4 turns → [CNF-4] shown")

# ── Test 6: confusion winding down ──
c.confusion_turns = 1
out = capture_card(c)
assert "[CNF-1]" in out, f"FAIL: expected [CNF-1], got:\n{out}"
print("PASS 6: confuse 1 turn  → [CNF-1] shown")

# ── Test 7: unaffected statuses (poison/burn/par/freeze) still show without turn count ──
for status, tag in [("poison", "[PSN]"), ("burn", "[BRN]"), ("paralyzed", "[PAR]"), ("freeze", "[FRZ]")]:
    c.status = status
    out = capture_card(c)
    assert tag in out, f"FAIL: {status} → expected {tag} in:\n{out}"
    # Confirm no spurious dash-number
    for bad in [f"{tag[:-1]}-"]:
        assert bad not in out, f"FAIL: {status} has unexpected counter: {out}"
print("PASS 7: poison/burn/paralyzed/freeze show clean badges without turn counter")

print()
print("All status duration UI tests passed.")
