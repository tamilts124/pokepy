import os
import time
import sys
from collections import deque

# ─── BATTLE MESSAGE LOG ───
# Rolling buffer of recent slow_print()'d lines, used by the in-battle
# 📜 Log viewer so players can review what just happened.
BATTLE_LOG = deque(maxlen=300)

def reset_battle_log():
    BATTLE_LOG.clear()

def show_battle_log(n=15):
    clear()
    section("📜  BATTLE LOG")
    recent = list(BATTLE_LOG)[-n:]
    if not recent:
        print(f"  {C.GRAY}(nothing has happened yet){C.RESET}")
    else:
        for line in recent:
            print(f"  {line}")
    print()
    press_enter()

# ─── ANSI COLORS ───
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    BG_RED = "\033[41m"
    BG_BLUE= "\033[44m"

TYPE_COLORS = {
    "fire":     C.RED,
    "water":    C.BLUE,
    "grass":    C.GREEN,
    "electric": C.YELLOW,
    "ice":      C.CYAN,
    "rock":     C.GRAY,
    "ground":   C.YELLOW,
    "psychic":  C.MAGENTA,
    "ghost":    C.MAGENTA,
    "poison":   C.MAGENTA,
    "flying":   C.CYAN,
    "dark":     C.GRAY,
    "normal":   C.WHITE,
    "bug":      C.GREEN,
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def slow_print(text, delay=0.025):
    BATTLE_LOG.append(text)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner(text, color=C.CYAN):
    w = 60
    print(color + "═" * w + C.RESET)
    print(color + text.center(w) + C.RESET)
    print(color + "═" * w + C.RESET)

def section(text, color=C.YELLOW):
    print(color + f"\n── {text} " + "─" * (54 - len(text)) + C.RESET)

def hp_bar(hp, max_hp, width=20):
    ratio = hp / max_hp if max_hp else 0
    filled = int(ratio * width)
    bar    = "█" * filled + "░" * (width - filled)
    if ratio > 0.5:
        color = C.GREEN
    elif ratio > 0.25:
        color = C.YELLOW
    else:
        color = C.RED
    return f"{color}[{bar}]{C.RESET} {hp}/{max_hp}"

def creature_card(c, prefix="", show_exp=False):
    types_str = "/".join(
        f"{TYPE_COLORS.get(t, C.WHITE)}{t.upper()}{C.RESET}" for t in c.types
    )
    status_str = ""
    if c.status == "poison":
        status_str = f" {C.MAGENTA}[PSN]{C.RESET}"
    elif c.status == "paralyzed":
        status_str = f" {C.YELLOW}[PAR]{C.RESET}"
    elif c.status == "burn":
        status_str = f" {C.RED}[BRN]{C.RESET}"
    elif c.status == "sleep":
        status_str = f" {C.BLUE}[SLP]{C.RESET}"
    elif c.status == "freeze":
        status_str = f" {C.CYAN}[FRZ]{C.RESET}"
    elif c.status == "confuse":
        status_str = f" {C.MAGENTA}[CNF]{C.RESET}"

    # Held item tag
    held_str = ""
    if getattr(c, 'held_item', None):
        held_str = f"  {C.YELLOW}[{c.held_item}]{C.RESET}"

    print(f"{prefix}{C.BOLD}{c.name}{C.RESET} Lv.{c.level}  {types_str}{status_str}{held_str}")
    # Show ability and nature inline
    ability_str = f"Ability: {c.ability}" if getattr(c, 'ability', None) else ""
    nature_str  = ""
    if getattr(c, 'nature', None):
        from engine.core import NATURES
        boost, lower = NATURES.get(c.nature, (None, None))
        if boost and lower:
            nature_str = (f"Nature: {C.CYAN}{c.nature}{C.RESET}"
                          f"  {C.GREEN}+{boost}{C.RESET}/{C.RED}-{lower}{C.RESET}")
        else:
            nature_str = f"Nature: {C.GRAY}{c.nature}{C.RESET}"
    info_line = "  │  ".join(s for s in [ability_str, nature_str] if s)
    if info_line:
        print(f"{prefix}{C.GRAY}{info_line}{C.RESET}")
    print(f"{prefix}HP  {hp_bar(c.hp, c.max_hp)}")
    # EXP bar (only for player creatures that track exp)
    if show_exp and hasattr(c, 'exp') and hasattr(c, 'exp_to_next') and c.exp_to_next > 0:
        ratio = min(1.0, c.exp / c.exp_to_next)
        width = 20
        filled = int(ratio * width)
        bar = "▪" * filled + "·" * (width - filled)
        pct = int(ratio * 100)
        print(f"{prefix}EXP {C.CYAN}[{bar}]{C.RESET} {c.exp}/{c.exp_to_next} ({pct}%)")

def team_summary(team):
    section("YOUR TEAM")
    for i, c in enumerate(team, 1):
        status = f"{C.RED}[FAINTED]{C.RESET}" if not c.is_alive() else ""
        held   = f"  {C.YELLOW}[{c.held_item}]{C.RESET}" if getattr(c, 'held_item', None) else ""
        print(f"  {i}. {C.BOLD}{c.name}{C.RESET} Lv.{c.level}  "
              f"{hp_bar(c.hp, c.max_hp, 15)} {status}{held}")
        # EXP bar for alive creatures
        if c.is_alive() and hasattr(c, 'exp') and hasattr(c, 'exp_to_next') and c.exp_to_next > 0:
            ratio  = min(1.0, c.exp / c.exp_to_next)
            width  = 15
            filled = int(ratio * width)
            bar    = "\u25aa" * filled + "\u00b7" * (width - filled)
            print(f"     EXP {C.CYAN}[{bar}]{C.RESET} {c.exp}/{c.exp_to_next}")

def menu(title, options, color=C.CYAN):
    """Show a numbered menu and return validated choice (0-indexed)."""
    print(f"\n{color}{title}{C.RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {C.BOLD}{i}{C.RESET}. {opt}")
    while True:
        raw = input(f"{C.GRAY}> {C.RESET}").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print(f"{C.RED}Invalid choice.{C.RESET}")

def confirm(prompt):
    while True:
        ans = input(f"{prompt} {C.GRAY}(y/n){C.RESET} > ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False

def pause(msg="Press ENTER to continue..."):
    input(f"{C.GRAY}{msg}{C.RESET}")

def press_enter():
    input(f"\n{C.GRAY}[ Press ENTER ]{C.RESET}")


# ═══════════════════════════════════════════════════════════
#  WORLD MAP
# ═══════════════════════════════════════════════════════════
# Layout (row, col) in a fixed 19-col × 28-row grid.
# Each town occupies a labelled node; roads are ASCII lines.
#
#   Col:  0         1         2         3         4
#         0123456789012345678901234567890123456789012345
#
_MAP_TOWNS = {
    # name            : (row, col,  short_label,            badge_num)
    "Champion Road"   : ( 1,  28,  "Champion Road",         0),   # no badge num — final
    "Dragonspire"     : ( 5,  20,  "Dragonspire",           7),
    "Shadowmere"      : ( 9,  10,  "Shadowmere",            6),
    "Mistveil"        : ( 9,  26,  "Mistveil",              5),
    "Frostholm"       : (13,  10,  "Frostholm",             4),
    "Ashveil"         : (13,  30,  "Ashveil",               3),
    "Stonepeak"       : (17,  20,  "Stonepeak",             2),
    "Greenpath"       : (21,  20,  "Greenpath",             1),
    "Mudfen"          : (25,  10,  "Mudfen",                0),   # no gym
    "Rootvale"        : (25,  28,  "Rootvale",              0),   # starter town
}

# Connections as (town_a, town_b) — drawn as dotted paths
_MAP_ROADS = [
    ("Rootvale",    "Greenpath"),
    ("Rootvale",    "Mudfen"),
    ("Mudfen",      "Greenpath"),
    ("Greenpath",   "Stonepeak"),
    ("Stonepeak",   "Ashveil"),
    ("Stonepeak",   "Frostholm"),
    ("Ashveil",     "Frostholm"),
    ("Frostholm",   "Mistveil"),
    ("Frostholm",   "Shadowmere"),
    ("Shadowmere",  "Mistveil"),
    ("Shadowmere",  "Dragonspire"),
    ("Dragonspire", "Champion Road"),
]

# Gym leader info per town
_GYM_INFO = {
    "Greenpath"   : ("Fern",    "Grass",   "Leaf Badge"),
    "Stonepeak"   : ("Granite", "Rock",    "Rock Badge"),
    "Ashveil"     : ("Cinder",  "Fire",    "Ember Badge"),
    "Frostholm"   : ("Blizara", "Ice",     "Frost Badge"),
    "Mistveil"    : ("Myra",    "Psychic", "Mystic Badge"),
    "Shadowmere"  : ("Umbra",   "Ghost",   "Shadow Badge"),
    "Dragonspire" : ("Draven",  "Dragon",  "Dragon Badge"),
}

_WILD_AREAS = {
    "Rootvale"      : "Dusty Cave",
    "Mudfen"        : "Bogmarsh",
    "Greenpath"     : "Whisper Forest",
    "Stonepeak"     : "Rocky Tunnel",
    "Ashveil"       : "Lava Fields",
    "Frostholm"     : "Glacial Grotto",
    "Mistveil"      : "Mystic Meadow",
    "Shadowmere"    : "Shadow Ruins",
    "Dragonspire"   : "Dragon Den",
    "Champion Road" : "Champion Road",
}


def _draw_map_grid(current_town, badges):
    """
    Render the world map as a 2-D list of characters.
    Returns a list of strings (rows), already coloured with ANSI.
    """
    ROWS = 28
    COLS = 52
    grid = [[' '] * COLS for _ in range(ROWS)]

    def put(r, c, ch):
        if 0 <= r < ROWS and 0 <= c < COLS:
            grid[r][c] = ch

    # ── Draw roads (simple straight/diagonal segments) ──
    road_coords = set()  # (r,c) occupied by a road char

    def draw_road(r1, c1, r2, c2):
        """Bresenham-like: draw a dotted path between two grid points."""
        steps = max(abs(r2 - r1), abs(c2 - c1))
        if steps == 0:
            return
        for i in range(1, steps):
            r = round(r1 + (r2 - r1) * i / steps)
            c = round(c1 + (c2 - c1) * i / steps)
            # Skip every other step for a dotted look
            dr = abs(r2 - r1)
            dc = abs(c2 - c1)
            if dr == 0:          ch = '─' if i % 2 == 0 else '·'
            elif dc == 0:        ch = '│' if i % 2 == 0 else '·'
            else:                ch = '·'
            put(r, c, ch)
            road_coords.add((r, c))

    town_pos = {name: (info[0], info[1]) for name, info in _MAP_TOWNS.items()}
    for a, b in _MAP_ROADS:
        r1, c1 = town_pos[a]
        r2, c2 = town_pos[b]
        draw_road(r1, c1, r2, c2)

    # ── Draw town nodes (overwrite roads) ──
    # We return coloured strings per town instead of raw chars.
    # Build colour-annotated layers: (row, col_start, coloured_string)
    overlays = []

    for name, (row, col, label, badge_num) in _MAP_TOWNS.items():
        is_here  = (name == current_town)
        has_gym  = name in _GYM_INFO
        is_final = (name == "Champion Road")
        earned   = badge_num > 0 and badges is not None and any(
            b == _GYM_INFO.get(name, (None, None, None))[2] for b in badges
        )

        # Node box: [★ Label] or [ Label]
        if is_here:
            node_color = C.CYAN + C.BOLD
            marker = '►'
        elif is_final:
            node_color = C.YELLOW + C.BOLD
            marker = '★'
        elif has_gym and earned:
            node_color = C.GREEN
            marker = '✓'
        elif has_gym:
            node_color = C.WHITE
            marker = '⚔'
        else:
            node_color = C.GRAY
            marker = '○'

        node_str = f"{marker}{label}"
        overlays.append((row, col, node_color + node_str + C.RESET))

        # Badge pill to the right of label (gym towns only)
        if has_gym:
            badge_col = col + len(node_str) + 1
            if earned:
                pill = f"{C.GREEN}[{badge_num}]{C.RESET}"
            else:
                pill = f"{C.GRAY}[{badge_num}]{C.RESET}"
            overlays.append((row, badge_col, pill))

    # ── Render grid to coloured strings ──
    # First pass: road layer (dim)
    result_rows = []
    for r in range(ROWS):
        row_str = ''
        for c in range(COLS):
            ch = grid[r][c]
            if ch in ('─', '│', '·'):
                row_str += C.GRAY + ch + C.RESET
            else:
                row_str += ch
        result_rows.append(row_str)

    # Second pass: overlay town nodes (split by invisible ANSI)
    # We work with the raw visible-char positions, so we re-build
    # each row that has an overlay using a character-slot approach.
    for (row, col, colored_str) in overlays:
        # Insert colored_str at visual column `col` of result_rows[row].
        # Since result_rows[row] contains ANSI codes we can't simply index,
        # we rebuild the row character by character.
        # Strategy: keep a separate plain array, then re-render.
        pass  # handled in the plain-grid approach below

    return result_rows, overlays


def show_world_map(current_town, badges):
    """Print the ASCII world map with ANSI colour."""
    clear()
    banner("  🗺   WORLD MAP  ", C.CYAN)

    ROWS = 28
    COLS = 52
    # plain grid (no ANSI here — we'll colour on output)
    grid = [[' '] * COLS for _ in range(ROWS)]

    town_pos = {name: (info[0], info[1]) for name, info in _MAP_TOWNS.items()}

    # ── Roads ──
    def draw_road(r1, c1, r2, c2):
        steps = max(abs(r2 - r1), abs(c2 - c1))
        if steps == 0:
            return
        dr = abs(r2 - r1)
        dc = abs(c2 - c1)
        for i in range(1, steps):
            r = round(r1 + (r2 - r1) * i / steps)
            c = round(c1 + (c2 - c1) * i / steps)
            if grid[r][c] == ' ':
                if dr == 0:       ch = '─'
                elif dc == 0:     ch = '│'
                elif i % 2 == 0:  ch = '·'
                else:             ch = '.'
                grid[r][c] = ch

    for a, b in _MAP_ROADS:
        r1, c1 = town_pos[a]
        r2, c2 = town_pos[b]
        draw_road(r1, c1, r2, c2)

    # ── Town labels (plain, length tracked) ──
    # We store (row, col, label_text, color) and overlay after
    town_labels = []
    for name, (row, col, label, badge_num) in _MAP_TOWNS.items():
        is_here  = (name == current_town)
        has_gym  = name in _GYM_INFO
        is_final = (name == "Champion Road")
        earned   = badge_num > 0 and badges is not None and any(
            b == _GYM_INFO.get(name, (None, None, None))[2] for b in badges
        )

        if is_here:
            color  = C.CYAN + C.BOLD
            marker = chr(0x25BA)  # ► (single char)
        elif is_final:
            color  = C.YELLOW + C.BOLD
            marker = '*'
        elif has_gym and earned:
            color  = C.GREEN
            marker = 'v'
        elif has_gym:
            color  = C.WHITE
            marker = '+'
        else:
            color  = C.GRAY
            marker = 'o'

        plain_label = marker + label  # plain for grid blocking
        town_labels.append((row, col, plain_label, color, badge_num, has_gym, earned))

        # Block out road chars behind label in grid
        for i, ch in enumerate(plain_label):
            if 0 <= col + i < COLS:
                grid[row][col + i] = '\x01'  # sentinel → will be skipped

    # ── Render ──
    print()
    for r in range(ROWS):
        # Build the output line piece by piece.
        # For each column: check if a town label starts here, else print grid char.
        line_parts = []
        c = 0
        # Build a map of col → (colored_str, length) for labels in this row
        label_at = {}
        for (lr, lc, plain, color, bnum, has_gym, earned) in town_labels:
            if lr == r:
                badge_pill = ''
                if has_gym:
                    pc = '[v]' if earned else f'[{bnum}]'
                    badge_pill = pc
                display = color + plain + C.RESET
                if has_gym:
                    pill_color = C.GREEN if earned else C.GRAY
                    display += ' ' + pill_color + badge_pill + C.RESET
                label_at[lc] = (display, len(plain) + (1 + len(badge_pill) if has_gym else 0))

        while c < COLS:
            if c in label_at:
                display, length = label_at[c]
                line_parts.append(display)
                c += length
            else:
                ch = grid[r][c]
                if ch == '\x01':
                    line_parts.append(' ')
                elif ch in ('─', '│', '·', '.'):
                    line_parts.append(C.GRAY + ch + C.RESET)
                else:
                    line_parts.append(ch)
                c += 1
        print('  ' + ''.join(line_parts))

    # ── Legend ──
    print()
    print(f"  {C.CYAN + C.BOLD}►Town (you are here){C.RESET}   "
          f"{C.GREEN}vGym (badge earned){C.RESET}   "
          f"{C.WHITE}+Gym (not yet){C.RESET}   "
          f"{C.GRAY}oNo gym{C.RESET}   "
          f"{C.YELLOW + C.BOLD}*Final{C.RESET}")
    print(f"  {C.GRAY}[n] = badge #{C.RESET}   "
          f"{C.GRAY}·  = road{C.RESET}")

    # ── Town detail for current location ──
    print()
    section(f"  You are in: {C.BOLD}{current_town}{C.RESET}")
    wild = _WILD_AREAS.get(current_town, '—')
    gym  = _GYM_INFO.get(current_town)
    if gym:
        leader, gtype, gbadge = gym
        earned = badges and gbadge in badges
        status = f"{C.GREEN}✓ Earned{C.RESET}" if earned else f"{C.RED}Not yet{C.RESET}"
        print(f"  Gym leader : {C.BOLD}{leader}{C.RESET} ({gtype}-type)  Badge: {gbadge}  {status}")
    else:
        print(f"  No gym in {current_town}.")
    print(f"  Wild area  : {C.CYAN}{wild}{C.RESET}")
    print()
    press_enter()
