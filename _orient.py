"""Quick orientation: find key function definitions and TYPE_CHART usage in battle.py"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('engine/battle.py', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ('def ', 'TYPE_CHART', 'type_hint', 'battle_ui', 'creature_card',
            'trainer_name', 'wild=')
for i, l in enumerate(lines, 1):
    lstrip = l.strip()
    if any(k in lstrip for k in keywords):
        if 'def ' in lstrip or 'TYPE_CHART' in lstrip[:40]:
            print(f'{i}: {lstrip[:100]}')
