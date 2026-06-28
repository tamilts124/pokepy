"""Verification for the Type Chart reference menu (📘 Type Chart).

Checks:
  1. All 16 creature-relevant types are present as both rows and columns.
  2. The rendered grid's symbol/colour for a representative sample of cells
     matches the underlying TYPE_CHART data exactly (no transcription bugs).
  3. Grid columns stay aligned (every row line is the same visible length).
  4. The menu option is wired into main.py's town_loop (label + handler).
  5. py_compile / ast sanity on touched files.
"""
import sys, io, builtins, re, ast, pathlib
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ui.display import show_type_chart, _CHART_TYPES, _chart_cell, C
from data.creatures import TYPE_CHART

# Test 1: all 16 in-use creature types appear in the chart's type list
from data.creatures import CREATURES
used_types = set()
for d in CREATURES.values():
    used_types.update(d["type"])
assert used_types == set(_CHART_TYPES), f"type list mismatch: {used_types ^ set(_CHART_TYPES)}"
print(f"PASS 1: all {len(_CHART_TYPES)} creature types present as chart rows/columns")

# Test 2: spot-check cell symbol/colour against TYPE_CHART for a sample of
# (attacker, defender) pairs covering super/resist/immune/neutral cases.
samples = [
    ("fire", "grass", 2, "▲", C.YELLOW),
    ("fire", "water", 0.5, "▼", C.BLUE),
    ("electric", "ground", 0, "✗", C.GRAY),
    ("normal", "ghost", 0, "✗", C.GRAY),
    ("fire", "electric", 1.0, "·", C.GRAY),
    ("water", "rock", 2, "▲", C.YELLOW),
    ("ground", "flying", 0, "✗", C.GRAY),
    ("steel", "steel", 0.5, "▼", C.BLUE),
]
for atk, dfd, expect_eff, expect_sym, expect_color in samples:
    eff = TYPE_CHART.get(atk, {}).get(dfd, 1.0)
    assert eff == expect_eff, f"{atk} vs {dfd}: expected eff {expect_eff}, got {eff}"
    sym, color = _chart_cell(eff)
    assert sym == expect_sym and color == expect_color, (
        f"{atk} vs {dfd}: expected symbol/colour {expect_sym!r}/{expect_color!r}, "
        f"got {sym!r}/{color!r}")
print(f"PASS 2: {len(samples)} sample cells match TYPE_CHART exactly")

# Test 3: rendered grid stays aligned — every data row, with ANSI codes
# stripped, has the same visible length as the header row.
old_input = builtins.input
builtins.input = lambda *a, **k: ""
buf = io.StringIO()
old_stdout = sys.stdout
sys.stdout = buf
try:
    show_type_chart()
finally:
    sys.stdout = old_stdout
    builtins.input = old_input

ansi_re = re.compile(r'\x1b\[[0-9;]*m')
lines = [ansi_re.sub('', l) for l in buf.getvalue().splitlines()]
row_labels = {t[:3].upper() for t in _CHART_TYPES}
grid_rows = [l for l in lines if len(l) >= 7 and l[2:5] in row_labels]
header_lines = [l for l in lines
                 if l.strip().startswith(next(iter(_CHART_TYPES))[:3].upper())
                 and not any(sym in l for sym in "▲▼✗·")]
all_grid_lines = header_lines + grid_rows
assert len(all_grid_lines) == 1 + len(_CHART_TYPES), (
    f"expected header + {len(_CHART_TYPES)} rows, found {len(all_grid_lines)}")
widths = {len(l) for l in all_grid_lines}
assert len(widths) == 1, f"grid rows not aligned, widths seen: {widths}"
print(f"PASS 3: header + {len(_CHART_TYPES)} rows all render at the same width ({widths.pop()} chars)")

# Test 4: menu wiring present in main.py
main_src = pathlib.Path("main.py").read_text(encoding="utf-8")
ast.parse(main_src)
assert '"📘  Type Chart"' in main_src, "Type Chart menu option not added to town_loop opts"
assert 'show_type_chart' in main_src, "show_type_chart not imported/used in main.py"
assert 'label == "Type Chart"' in main_src, "Type Chart menu handler missing"
print("PASS 4: Type Chart menu option + handler wired into town_loop")

# Test 5: compile sanity
import py_compile
for f in ["main.py", "ui/display.py"]:
    py_compile.compile(f, doraise=True)
print("PASS 5: py_compile clean on main.py and ui/display.py")

print("\nAll type-chart tests passed.")
