"""Patch battle.py: add weakness hint to battle_ui for trainer battles."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BATTLE = r'D:\ClaudeDir\pokepy\engine\battle.py'
with open(BATTLE, encoding='utf-8') as f:
    src = f.read()

# The original creature_card line for enemy:
OLD = '    creature_card(enemy_c, prefix=f"  {label} ")\n    print(f"{\'─\'*30}")'

NEW = '''\
    creature_card(enemy_c, prefix=f"  {label} ")
    # ── Trainer battle only: show weakness hint under enemy card ──
    if not wild:
        from data.creatures import TYPE_CHART as _TC
        # Collect attacker types that deal ≥ 2× to ALL of the enemy's types combined
        _weaknesses = []
        _all_types = [\"fire\", \"water\", \"grass\", \"electric\", \"ice\", \"rock\",
                      \"ground\", \"psychic\", \"ghost\", \"poison\", \"flying\",
                      \"dark\", \"normal\", \"bug\", \"dragon\", \"steel\"]
        for _atk in _all_types:
            _eff = 1.0
            for _def in enemy_c.types:
                _eff *= _TC.get(_atk, {}).get(_def, 1.0)
            if _eff >= 2.0:
                _weaknesses.append(_atk)
        if _weaknesses:
            _tags = "  ".join(
                f"{TYPE_COLORS.get(t, C.WHITE)}[{t.upper()}]{C.RESET}"
                for t in _weaknesses[:4]
            )
            print(f"  {C.GRAY}Weak to: {C.RESET}{_tags}")
    print(f"{'─'*30}")'''

if OLD not in src:
    print("ERROR: target block not found - checking manually...")
    idx = src.find('creature_card(enemy_c, prefix=f"  {label}')
    print(f"  enemy card call at char {idx}: {repr(src[idx:idx+80])}")
    sys.exit(1)

src = src.replace(OLD, NEW, 1)
with open(BATTLE, 'w', encoding='utf-8') as f:
    f.write(src)
print("DONE: weakness hint inserted into battle_ui()")
