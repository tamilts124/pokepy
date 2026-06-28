import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
lines = open('ui/display.py', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    lo = l.lower()
    if 'creature_card' in lo or 'status' in lo or 'sleep' in lo or 'confus' in lo:
        print(i, l.rstrip()[:100])
