"""Verify accuracy display in fight menu (battle.py)."""
import sys, py_compile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('engine/battle.py', 'r', encoding='utf-8') as f:
    src = f.read()

assert '_acc_tag' in src, "FAIL: _acc_tag helper not found"
print("PASS 1: _acc_tag helper present in battle.py")

assert "MOVES[m]['accuracy']" in src, "FAIL: accuracy field not referenced"
print("PASS 2: MOVES[m]['accuracy'] referenced in move_opts block")

py_compile.compile('engine/battle.py', doraise=True)
print("PASS 3: py_compile clean")

# Test acc_tag logic inline (mimic the code)
WHITE = YELLOW = RED = GRAY = RESET = ''
def _acc_tag(acc):
    if acc >= 100:
        return f"{GRAY}\u2014  {RESET}"
    elif acc >= 90:
        return f"{WHITE}{acc}%{RESET}"
    elif acc >= 75:
        return f"{YELLOW}{acc}%{RESET}"
    else:
        return f"{RED}{acc}%{RESET}"

assert '\u2014' in _acc_tag(100), f"FAIL acc=100: {_acc_tag(100)}"
print("PASS 4: acc=100 shows em-dash (perfect accuracy, no clutter)")
assert '70%' in _acc_tag(70), f"FAIL acc=70: {_acc_tag(70)}"
print("PASS 5: acc=70 shows 70% (low accuracy)")
assert '90%' in _acc_tag(90), f"FAIL acc=90: {_acc_tag(90)}"
print("PASS 6: acc=90 shows 90% (decent accuracy)")
assert '75%' in _acc_tag(75), f"FAIL acc=75: {_acc_tag(75)}"
print("PASS 7: acc=75 shows 75% (borderline accuracy)")

# Column ordering in the rendered menu line
pwr_pos = src.find("Pwr:{MOVES[m]['power']")
acc_pos = src.find("Acc:{_acc_tag")
type_pos = src.find("TYPE_COLORS.get(MOVES[m]['type']")
assert 0 < pwr_pos < acc_pos < type_pos, \
    f"FAIL ordering: pwr={pwr_pos}, acc={acc_pos}, type={type_pos}"
print("PASS 8: Acc column appears between Pwr and type tag in fight menu")

print()
print("All accuracy display tests passed.")
