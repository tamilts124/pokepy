"""Show patched battle_ui"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open('engine/battle.py', encoding='utf-8') as f:
    lines = f.readlines()
for i in range(449, 490):
    sys.stdout.write(f'{i+1}: {lines[i].rstrip()}\n')
