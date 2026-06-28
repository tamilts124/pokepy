"""Patch main.py to add the Achievement Gallery feature.

Changes:
1. Insert open_achievements() method after open_badges() method.
2. Add '🏆  Achievements' option to town menu opts list.
3. Add elif handler for 'Achievements' label.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MAIN = r'D:\ClaudeDir\pokepy\main.py'
with open(MAIN, encoding='utf-8') as f:
    src = f.read()

# ── 1. Insert open_achievements() after open_badges() ──
# Find the end of open_badges: the press_enter() call just before "# ── TRAINER STATS"
OPEN_ACHIEVEMENTS_METHOD = '''
    # ── ACHIEVEMENT GALLERY ─────────────────────────────────
    def open_achievements(self):
        clear()
        section("\\U0001f3c6  ACHIEVEMENTS")
        earned = getattr(self, 'achievements', [])
        total  = len(ACHIEVEMENTS)
        count  = sum(1 for k in ACHIEVEMENTS if k in earned)
        color  = C.YELLOW if count >= total else C.RESET
        print(f"  Unlocked: {color}{count}/{total}{C.RESET}\\n")
        for key, ach in ACHIEVEMENTS.items():
            if key in earned:
                print(f"  {C.YELLOW}\\u2713  {C.BOLD}{ach['name']}{C.RESET}")
                print(f"      {C.GRAY}{ach['desc']}{C.RESET}")
            else:
                print(f"  {C.GRAY}\\u25cb  {ach['name']}{C.RESET}")
        press_enter()

'''

# Locate the insertion point: just before "    # ── TRAINER STATS"
insert_marker = '    # \u2500\u2500 TRAINER STATS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500'
if insert_marker not in src:
    # Try a simpler version
    insert_marker = '    # \u2500\u2500 TRAINER STATS'
    
if insert_marker not in src:
    print(f"ERROR: Could not find TRAINER STATS marker")
    print("Searching for nearby text...")
    idx = src.find('TRAINER STATS')
    if idx >= 0:
        print(f"Found at char {idx}: {repr(src[idx-10:idx+60])}")
    sys.exit(1)

src = src.replace(insert_marker, OPEN_ACHIEVEMENTS_METHOD + insert_marker, 1)
print("STEP 1 OK: open_achievements() inserted")

# ── 2. Add menu option: after "📊  Trainer Card" ──
OLD_MENU = '                "📊  Trainer Card",'
NEW_MENU = '                "📊  Trainer Card",\n                "🏆  Achievements",'
if OLD_MENU not in src:
    print("ERROR: could not find Trainer Card menu entry")
    sys.exit(1)
src = src.replace(OLD_MENU, NEW_MENU, 1)
print("STEP 2 OK: Achievements menu option added after Trainer Card")

# ── 3. Add elif handler: after "elif label == \"Trainer Card\":" ──
OLD_HANDLER = '            elif label == "Trainer Card":\n                self.open_stats()'
NEW_HANDLER = ('            elif label == "Trainer Card":\n'
               '                self.open_stats()\n'
               '            elif label == "Achievements":\n'
               '                self.open_achievements()')
if OLD_HANDLER not in src:
    print("ERROR: could not find Trainer Card elif handler")
    sys.exit(1)
src = src.replace(OLD_HANDLER, NEW_HANDLER, 1)
print("STEP 3 OK: elif Achievements handler wired in")

# ── Write back ──
with open(MAIN, 'w', encoding='utf-8') as f:
    f.write(src)
print("DONE: main.py written")
