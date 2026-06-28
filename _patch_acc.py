"""Patch battle.py: add accuracy display to fight menu."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = r'D:\ClaudeDir\pokepy\engine\battle.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replacement block (0-indexed lines 1125-1142)
new_block = [
    '                def _pwr_tier(pwr):\n',
    '                    if pwr == 0:\n',
    '                        return f"{C.GRAY}\u2014   {C.RESET}"\n',
    '                    elif pwr <= 40:\n',
    '                        return f"{C.YELLOW}\u2605   {C.RESET}"\n',
    '                    elif pwr <= 80:\n',
    '                        return f"{C.YELLOW}\u2605\u2605  {C.RESET}"\n',
    '                    else:\n',
    '                        return f"{C.RED}\u2605\u2605\u2605 {C.RESET}"\n',
    '                def _acc_tag(acc):\n',
    '                    if acc >= 100:\n',
    '                        return f"{C.GRAY}\u2014  {C.RESET}"\n',
    '                    elif acc >= 90:\n',
    '                        return f"{C.WHITE}{acc}%{C.RESET}"\n',
    '                    elif acc >= 75:\n',
    '                        return f"{C.YELLOW}{acc}%{C.RESET}"\n',
    '                    else:\n',
    '                        return f"{C.RED}{acc}%{C.RESET}"\n',
    '                move_opts = [\n',
    '                    (f"{m:<16}  {C.GRAY}PP {player_c.pp[m]}/{MOVES[m][\'pp\']}"\n',
    '                     f"  Pwr:{MOVES[m][\'power\']:<4}{_pwr_tier(MOVES[m][\'power\'])}"\n',
    '                     f"Acc:{_acc_tag(MOVES[m][\'accuracy\'])}  "\n',
    '                     f"{TYPE_COLORS.get(MOVES[m][\'type\'], C.WHITE)}[{MOVES[m][\'type\'].upper():<8}]{C.RESET}"\n',
    '                     f"  {type_hint(MOVES[m][\'type\'], enemy_c.types)}"\n',
    '                     f"{(\' \' + C.CYAN + \'[FAST]\' + C.RESET) if MOVES[m].get(\'priority\',0) > 0 else \'\'}"\n',
    '                     f"\\n     {C.GRAY}{MOVES[m].get(\'desc\', \'\')}{C.RESET}")\n',
    '                    for m in player_c.moves\n',
    '                ]\n',
]

# Replace lines 1125-1142 (0-indexed)
out = lines[:1125] + new_block + lines[1143:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)

print(f"Patched: replaced lines 1126-1143 with {len(new_block)} new lines")
print(f"File now has {len(out)} lines (was {len(lines)})")
