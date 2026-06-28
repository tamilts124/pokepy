import sys, textwrap
sys.path.insert(0, '.')
from data.creatures import CREATURES

short = [(n, len(d['desc'])) for n, d in CREATURES.items() if len(d.get('desc', '')) < 80]
if short:
    print('FAIL: short lore entries:', short)
    sys.exit(1)
else:
    print(f'PASS: all {len(CREATURES)} creatures have desc >= 80 chars')

avg = sum(len(d['desc']) for d in CREATURES.values()) // len(CREATURES)
print(f'Avg lore length: {avg} chars')

# Spot check: wrap works cleanly
sample = CREATURES['Ghostlet']['desc']
wrapped = textwrap.wrap(sample, 70)
assert len(wrapped) >= 2, f"Expected multi-line wrap, got {wrapped}"
print(f'PASS: Ghostlet wraps into {len(wrapped)} lines')
for line in wrapped:
    print(f'  {line}')

# Check all creatures loadable
for name, data in CREATURES.items():
    assert 'desc' in data, f"Missing desc for {name}"
    assert len(data['desc']) > 50, f"Still too short for {name}: {data['desc']!r}"
print(f'\nPASS: all {len(CREATURES)} creatures have desc > 50 chars')

# Verify main.py has textwrap call
import pathlib
main_src = pathlib.Path('main.py').read_text(encoding='utf-8')
assert 'textwrap' in main_src, 'textwrap not in main.py'
assert '_tw.wrap' in main_src, '_tw.wrap not in main.py'
print('PASS: textwrap display code present in main.py')
