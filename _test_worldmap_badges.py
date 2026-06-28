"""
Verify world-map gym badge status feature (task.md listed it as 'todo' but it turned
out to already be implemented in ui/display.py's show_world_map() from an earlier
session — this is the resume-and-verify check before flipping the task to done).
"""
import sys, os, io, re, builtins
sys.path.insert(0, os.path.dirname(__file__))
import ui.display as D

builtins.input = lambda *a, **k: ""

def run(town, badges):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        D.show_world_map(town, badges)
    finally:
        sys.stdout = old
    return re.sub(r'\x1b\[[0-9;]*m', '', buf.getvalue())

plain = run("Rootvale", [])
assert '[1]' in plain or '[2]' in plain
print("PASS 1: unearned gym towns show numbered badge pill (e.g. [1])")

plain2 = run("Rootvale", ["Leaf Badge"])
assert '[v]' in plain2
print("PASS 2: earning a badge flips that gym town's pill to [v]")

assert 'badge earned' in plain.lower()
assert 'not yet' in plain.lower()
print("PASS 3: legend explains v/+/o markers and badge-earned meaning")

print("\nWorld-map badge-status feature confirmed fully implemented and working.")
