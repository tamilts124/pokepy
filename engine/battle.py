import random
import time

from engine.core import (calc_damage, try_capture, Creature, MOVES, ITEMS,
                          apply_weather_damage, weather_move_mult)
from ui.display  import (C, slow_print, banner, hp_bar, creature_card,
                          menu, press_enter, section, clear,
                          show_battle_log, reset_battle_log, TYPE_COLORS)



# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def effectiveness_msg(eff, crit=False):
    parts = []
    if eff >= 2:
        parts.append(f"{C.YELLOW}It's super effective!{C.RESET}")
    elif eff == 0:
        parts.append(f"{C.GRAY}It has no effect...{C.RESET}")
    elif eff < 1:
        parts.append(f"{C.BLUE}It's not very effective...{C.RESET}")
    return "  ".join(parts)


def crit_flash():
    """Print a vivid critical hit banner on its own line."""
    slow_print(f"  {C.BOLD}{C.RED}★  CRITICAL HIT!  ★{C.RESET}", 0)


def type_hint(move_type, defender_types):
    """Return a short effectiveness hint string for the move menu."""
    from data.creatures import TYPE_CHART
    eff = 1.0
    for t in defender_types:
        eff *= TYPE_CHART.get(move_type, {}).get(t, 1.0)
    if eff >= 2:
        return f"{C.YELLOW}▲▲{C.RESET}"
    elif eff == 0:
        return f"{C.GRAY}✗{C.RESET}"
    elif eff < 1:
        return f"{C.BLUE}▼{C.RESET}"
    return f"{C.GRAY}–{C.RESET}"


# ─────────────────────────────────────────────
#  DISPLAY NAME  (resolves same-name ambiguity)
# ─────────────────────────────────────────────

def _dname(c):
    """Return the creature's tagged display name for battle messages.
    If the creature has a nickname, shows 'Nick (Species)'.
    Set c._battle_tag = 'Your' or 'Foe'/'Wild' in run_battle before use."""
    tag      = getattr(c, '_battle_tag', '')
    nickname = getattr(c, 'nickname', None)
    display  = f"{nickname} ({c.name})" if nickname else c.name
    if getattr(c, 'is_shiny', False):
        display = f"✦{display}"
    if tag:
        return f"{tag} {display}"
    return display



_STATUS_IMMUNE = {
    # status: set of types that cannot be inflicted
    "sleep":   set(),
    "freeze":  {"ice"},
    "confuse":  set(),
    "poison":  {"poison", "steel"},
    "burn":    {"fire"},
    "paralyzed": set(),
}

def _can_inflict(status, target):
    """Return True if target can receive this status (not already statused, not immune type)."""
    if target.status is not None:
        return False
    immune = _STATUS_IMMUNE.get(status, set())
    return not any(t in immune for t in target.types)


def inflict_status(status, target, chance=1.0):
    if not _can_inflict(status, target):
        return ''
    if random.random() > chance:
        return ''
    target.status = status
    n = _dname(target)
    if status == "sleep":
        target.sleep_turns = random.randint(1, 3)
        return f"  {C.BLUE}{n} fell asleep!{C.RESET}"
    elif status == "freeze":
        return f"  {C.CYAN}{n} was frozen solid!{C.RESET}"
    elif status == "confuse":
        target.confusion_turns = random.randint(2, 5)
        return f"  {C.MAGENTA}{n} became confused!{C.RESET}"
    elif status == "poison":
        return f"  {C.MAGENTA}{n} was poisoned!{C.RESET}"
    elif status == "burn":
        return f"  {C.RED}{n} was burned!{C.RESET}"
    elif status == "paralyzed":
        return f"  {C.YELLOW}{n} was paralyzed!{C.RESET}"
    return ''


def preturn_status_check(c):
    n = _dname(c)
    if c.status == "sleep":
        if c.sleep_turns <= 0:
            c.status = None
            c.sleep_turns = 0
            return True, f"  {C.GREEN}{n} woke up!{C.RESET}"
        c.sleep_turns -= 1
        return False, f"  {C.BLUE}{n} is fast asleep...{C.RESET}"
    if c.status == "freeze":
        if random.random() < 0.20:
            c.status = None
            return True, f"  {C.CYAN}{n} thawed out!{C.RESET}"
        return False, f"  {C.CYAN}{n} is frozen and can't move!{C.RESET}"
    if c.status == "paralyzed" and random.random() < 0.25:
        return False, f"  {C.YELLOW}{n} is paralyzed and can't move!{C.RESET}"
    if c.status == "confuse":
        c.confusion_turns -= 1
        if c.confusion_turns <= 0:
            c.status = None
            c.confusion_turns = 0
            return True, f"  {C.GREEN}{n} snapped out of confusion!{C.RESET}"
        if random.random() < 0.33:
            dmg = max(1, int(c.max_hp * 0.12))
            c.take_damage(dmg)
            return False, f"  {C.MAGENTA}{n} is confused and hurt itself! ({dmg} dmg){C.RESET}"
        return True, f"  {C.MAGENTA}{n} is confused!{C.RESET}"
    return True, ''
# ─────────────────────────────────────────────
#  ABILITIES
# ─────────────────────────────────────────────
#
# Each ability is a dict of optional hooks:
#   on_entry(c, foe, weather)  → list of message strings (fires when creature enters battle)
#   damage_taken_mult(c, move_type, move_power, weather) → float multiplier on incoming damage
#   damage_dealt_mult(c, move_type, weather) → float multiplier on outgoing damage
#   on_hit_received(c, attacker, move_name, weather) → list of message strings
#   end_of_turn(c, weather)    → list of message strings
#   speed_mult(c, weather)     → float speed multiplier (applied to effective_spd result)
#   blocks_ground              → bool  (creature is immune to ground-type moves)
#

ABILITIES = {
    # ── Starter abilities ──────────────────────────────────
    "Blaze": {
        "desc": "Fire moves power up at low HP.",
        "damage_dealt_mult": lambda c, mtype, weather: (
            1.5 if mtype == "fire" and c.hp <= c.max_hp // 3 else 1.0
        ),
        "end_of_turn": lambda c, weather: _starter_ability_notice(
            c, "Blaze", "fire", "🔥", C.RED
        ),
    },
    "Overgrow": {
        "desc": "Grass moves power up at low HP.",
        "damage_dealt_mult": lambda c, mtype, weather: (
            1.5 if mtype == "grass" and c.hp <= c.max_hp // 3 else 1.0
        ),
        "end_of_turn": lambda c, weather: _starter_ability_notice(
            c, "Overgrow", "grass", "🌿", C.GREEN
        ),
    },
    "Torrent": {
        "desc": "Water moves power up at low HP.",
        "damage_dealt_mult": lambda c, mtype, weather: (
            1.5 if mtype == "water" and c.hp <= c.max_hp // 3 else 1.0
        ),
        "end_of_turn": lambda c, weather: _starter_ability_notice(
            c, "Torrent", "water", "💧", C.CYAN
        ),
    },
    # ── Defensive ─────────────────────────────────────────
    "Thick Fat": {
        "desc": "Halves damage from Fire and Ice moves.",
        "damage_taken_mult": lambda c, mtype, mpwr, weather: (
            0.5 if mtype in ("fire", "ice") else 1.0
        ),
    },
    "Dragon Skin": {
        "desc": "Halves damage from Dragon moves.",
        "damage_taken_mult": lambda c, mtype, mpwr, weather: (
            0.5 if mtype == "dragon" else 1.0
        ),
    },
    "Rock Head": {
        "desc": "Increases Defense by 10%.",
        "damage_taken_mult": lambda c, mtype, mpwr, weather: 0.9,
    },
    "Ice Body": {
        "desc": "Recovers HP in Hail weather.",
        "end_of_turn": lambda c, weather: (
            [(c.heal(max(1, c.max_hp // 16)),
              f"  {C.CYAN}{_dname(c)}'s Ice Body restored some HP!{C.RESET}")[1]]
            if weather == "Hail" else []
        ),
    },
    "Sturdy": {
        "desc": "Survives a one-hit KO with 1 HP (once per switch-in).",
        # Handled specially in take_damage path — see apply_ability_sturdy()
    },
    # ── On-entry ──────────────────────────────────────────
    "Intimidate": {
        "desc": "Lowers foe's Attack by 1 stage on entry.",
        "on_entry": lambda c, foe, weather: (
            [(foe.apply_stage("atk", -1),
              f"  {C.YELLOW}{_dname(c)}'s Intimidate lowered {_dname(foe)}'s Attack!{C.RESET}")[1]]
        ),
    },
    # ── On-hit ────────────────────────────────────────────
    "Static": {
        "desc": "30% chance to paralyze attacker on contact.",
        "on_hit_received": lambda c, attacker, move_name, weather: (
            _static_proc(attacker)
        ),
    },
    "Poison Touch": {
        "desc": "30% chance to poison attacker on contact.",
        "on_hit_received": lambda c, attacker, move_name, weather: (
            _poison_touch_proc(attacker)
        ),
    },
    "Spore Cloud": {
        "desc": "20% chance to put attacker to sleep on contact.",
        "on_hit_received": lambda c, attacker, move_name, weather: (
            _spore_cloud_proc(attacker)
        ),
    },
    # ── Speed ─────────────────────────────────────────────
    "Speed Boost": {
        "desc": "+1 Speed stage at end of each turn.",
        "end_of_turn": lambda c, weather: (
            [(c.apply_stage("spd", 1),
              f"  {C.GREEN}{_dname(c)}'s Speed Boost raised its Speed!{C.RESET}")[1]]
            if c.stages.get("spd", 0) < 6 else []
        ),
    },
    "Swift Swim": {
        "desc": "Speed doubled in Rainy weather.",
        "speed_mult": lambda c, weather: 2.0 if weather == "Rainy" else 1.0,
        "on_entry": lambda c, foe, weather: (
            [f"  {C.CYAN}🌧 {_dname(c)}'s Swift Swim kicked in! Speed doubled in the rain!{C.RESET}"]
            if weather == "Rainy" else []
        ),
    },
    # ── Type immunity ─────────────────────────────────────
    "Levitate": {
        "desc": "Immune to Ground-type moves.",
        "blocks_ground": True,
    },
}

# ── Proc helpers (lambdas can't contain logic, so we use functions) ──

def _static_proc(attacker):
    if attacker.status is None and random.random() < 0.30:
        attacker.status = "paralyzed"
        return [f"  {C.YELLOW}{_dname(attacker)} was paralyzed by Static!{C.RESET}"]
    return []

def _poison_touch_proc(attacker):
    if _can_inflict("poison", attacker) and random.random() < 0.30:
        attacker.status = "poison"
        return [f"  {C.MAGENTA}{_dname(attacker)} was poisoned by Poison Touch!{C.RESET}"]
    return []

def _spore_cloud_proc(attacker):
    if _can_inflict("sleep", attacker) and random.random() < 0.20:
        attacker.status = "sleep"
        attacker.sleep_turns = random.randint(1, 2)
        return [f"  {C.BLUE}{_dname(attacker)} was put to sleep by Spore Cloud!{C.RESET}"]
    return []


def _starter_ability_notice(c, ability_name, move_type, icon, color):
    """One-shot notice when a starter ability (Blaze/Overgrow/Torrent) first activates."""
    flag = f"_{ability_name.lower()}_notified"
    if c.hp <= c.max_hp // 3 and not getattr(c, flag, False):
        setattr(c, flag, True)
        return [f"  {color}{icon} {_dname(c)}'s {ability_name} activated! "
                f"{move_type.title()} moves are now powered up!{C.RESET}"]
    return []


def get_ability(c):
    """Return ability dict for creature, or {}."""
    return ABILITIES.get(c.ability, {})


def ability_damage_taken_mult(c, move_type, move_power, weather):
    """Incoming damage multiplier from abilities (Thick Fat, Dragon Skin, etc)."""
    ab = get_ability(c)
    fn = ab.get("damage_taken_mult")
    if fn:
        return fn(c, move_type, move_power, weather)
    return 1.0


def ability_damage_dealt_mult(c, move_type, weather):
    """Outgoing damage multiplier from abilities (Blaze, Overgrow, Torrent)."""
    ab = get_ability(c)
    fn = ab.get("damage_dealt_mult")
    if fn:
        return fn(c, move_type, weather)
    return 1.0


def ability_speed_mult(c, weather):
    """Speed multiplier from abilities (Swift Swim)."""
    ab = get_ability(c)
    fn = ab.get("speed_mult")
    if fn:
        return fn(c, weather)
    return 1.0


def ability_blocks_ground(c):
    """Returns True if creature is immune to ground moves (Levitate)."""
    return get_ability(c).get("blocks_ground", False)


def fire_on_entry(c, foe, weather):
    """Call on_entry ability when creature enters battle. Returns message list."""
    ab = get_ability(c)
    fn = ab.get("on_entry")
    if fn:
        return fn(c, foe, weather)
    return []


def fire_on_hit_received(c, attacker, move_name, weather):
    """Call on_hit_received ability. Returns message list."""
    ab = get_ability(c)
    fn = ab.get("on_hit_received")
    if fn:
        return fn(c, attacker, move_name, weather)
    return []


def fire_end_of_turn(c, weather):
    """Call end_of_turn ability. Returns message list."""
    ab = get_ability(c)
    fn = ab.get("end_of_turn")
    if fn:
        return fn(c, weather)
    return []


# ─────────────────────────────────────────────
#  STAT-LOWERING MOVE EFFECTS
# ─────────────────────────────────────────────
STAT_EFFECTS = {
    "lower_atk":   ("atk",   -1),
    "lower_def":   ("def",   -1),
    "lower_spd":   ("spd",   -1),
    "lower_acc":   ("acc",   -1),
    "lower_spatk": ("spatk", -1),
    "lower_spdef": ("spdef", -1),
    "raise_atk":   ("atk",   +1),
    "raise_def":   ("def",   +1),
    "raise_spd":   ("spd",   +1),
    "raise_spatk": ("spatk", +1),
    "raise_spdef": ("spdef", +1),
    "raise_atk2":  ("atk",   +2),
    "raise_spd2":  ("spd",   +2),
    "raise_spatk2":("spatk", +2),
    "raise_spdef2":("spdef", +2),
}

STAT_NAMES = {
    "atk":   "Attack",
    "def":   "Defense",
    "spd":   "Speed",
    "acc":   "Accuracy",
    "spatk": "Sp. Atk",
    "spdef": "Sp. Def",
}

STAT_STAGE_DELTA = {
    "raise_atk2":  2,
    "raise_spd2":  2,
    "raise_spatk2":2,
    "raise_spdef2":2,
}

def apply_stat_effect(effect_key, target, attacker_name):
    if effect_key not in STAT_EFFECTS:
        return ""
    stat, delta = STAT_EFFECTS[effect_key]
    delta = STAT_STAGE_DELTA.get(effect_key, delta)
    actual = target.apply_stage(stat, delta)
    n = _dname(target)
    if actual == 0:
        return f"  {C.GRAY}{n}'s {STAT_NAMES[stat]} won't go {'lower' if delta < 0 else 'higher'}!{C.RESET}"
    sharply = " sharply" if abs(actual) >= 2 else ""
    direction = f"fell{sharply}" if actual < 0 else f"rose{sharply}"
    color = C.RED if actual < 0 else C.GREEN
    return f"  {color}{n}'s {STAT_NAMES[stat]} {direction}!{C.RESET}"


# ─────────────────────────────────────────────
#  BATTLE DISPLAY
# ─────────────────────────────────────────────

GYM_LEADER_ART = {
    "Fern": f"""
{C.GREEN}    (^‿^)
   /|   |\\
    |   |
   / \\ / \\{C.RESET}""",
    "Granite": f"""
{C.GRAY}    (ò_ó)
   /|   |\\
   || | ||
   /\\ | /\\{C.RESET}""",
    "Cinder": f"""
{C.RED}    (>_<)
   /|   |\\
  [|   |]
   |\\  /|{C.RESET}""",
    "Blizara": f"""
{C.CYAN}    (❄ ❄)
   /|   |\\
   ||   ||
  _/|   |\\_\\ {C.RESET}""",
    "Myra": f"""
{C.MAGENTA}    (⊙ ω ⊙)
   /|    |\\
   ||    ||
  _\\|    |/_{C.RESET}""",
    "Umbra": f"""
{C.GRAY}    (◕‿◕)
   /|   |\\
  ███████
   |   |{C.RESET}""",
    "Draven": f"""
{C.YELLOW}    (◣_◢)
   /|   |\\
  /|   |\\
 / |   | \\{C.RESET}""",
}


def battle_ui(player_c, enemy_c, wild=True, weather=None, trainer_name=None):
    label = "Wild" if wild else "Foe"
    title = "  ⚔  WILD BATTLE  ⚔  " if wild else f"  ⚔  TRAINER BATTLE  —  {trainer_name}  ⚔  "
    banner(title, C.RED if not wild else C.YELLOW)
    print(f"\n{'─'*60}")
    if weather:
        weather_icons = {"Sunny": "☀", "Rainy": "🌧", "Sandstorm": "🌪", "Hail": "❄"}
        icon = weather_icons.get(weather, "☁")
        print(f"  {C.CYAN}{icon}  Weather: {weather}{C.RESET}")
    creature_card(enemy_c, prefix=f"  {label} ")
    # ── Trainer battle only: show weakness hint under enemy card ──
    if not wild:
        from data.creatures import TYPE_CHART as _TC
        # Collect attacker types that deal ≥ 2× to ALL of the enemy's types combined
        _weaknesses = []
        _all_types = ["fire", "water", "grass", "electric", "ice", "rock",
                      "ground", "psychic", "ghost", "poison", "flying",
                      "dark", "normal", "bug", "dragon", "steel"]
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
    print(f"{'─'*30}")
    creature_card(player_c, prefix="  Your ", show_exp=True)
    print(f"{'─'*60}")


# ─────────────────────────────────────────────
#  ANIMATED CAPTURE
# ─────────────────────────────────────────────

def animated_capture(enemy_c, item_name, ball_rate, lead=None):
    if lead is not None and getattr(lead, "friendship", 0) >= 80:
        slow_print(f"  {C.MAGENTA}{lead.name}'s calm presence settles the wild creature...{C.RESET}")
        time.sleep(0.3)
    slow_print(f"  You threw a {C.BOLD}{item_name}{C.RESET}!", delay=0.03)
    time.sleep(0.4)
    caught, shakes = try_capture(enemy_c, ball_rate, lead=lead)
    print(f"  ", end="", flush=True)
    for i in range(shakes):
        time.sleep(0.6)
        print(f"{C.YELLOW}*shake*{C.RESET}  ", end="", flush=True)
    if shakes < 4:
        time.sleep(0.6)
        print(f"{C.RED}*break!*{C.RESET}")
    else:
        time.sleep(0.6)
        print(f"{C.GREEN}★ Click!{C.RESET}")
    time.sleep(0.5)
    return caught, shakes


# ─────────────────────────────────────────────
#  HELD ITEM TRIGGERS
# ─────────────────────────────────────────────

HELD_ITEMS = {
    # ── Berries (one-use, trigger on condition) ──────────────────
    "Lum Berry":    {"trigger": "status",  "desc": "Auto-cures any status once"},
    "Sitrus Berry": {"trigger": "half_hp", "desc": "Heals 25% HP when below half"},
    "Oran Berry":   {"trigger": "half_hp", "desc": "Heals 10 HP when below half"},
    # ── Combat items (passive, every turn / every hit) ───────────
    "Life Orb":     {"trigger": "passive", "desc": "+30% damage out, costs 10% HP per attack"},
    "Choice Band":  {"trigger": "passive", "desc": "+50% Attack, locks to first move used"},
    "Leftovers":    {"trigger": "eot",     "desc": "Restore 1/16 max HP each turn"},
    "Shell Bell":   {"trigger": "passive", "desc": "Restore 1/8 of damage dealt each hit"},
    "Scope Lens":   {"trigger": "passive", "desc": "Critical hit chance doubled"},
    # Seasonal stat-boosting berries (one-use, trigger when HP < 25%)
    "Salac Berry":  {"trigger": "low_hp_spd", "desc": "+1 Speed when HP below 25%"},
    "Petaya Berry": {"trigger": "low_hp_atk", "desc": "+1 Attack when HP below 25%"},
    "Apicot Berry": {"trigger": "low_hp_def", "desc": "+1 Defense when HP below 25%"},
    "Ganlon Berry": {"trigger": "low_hp_def", "desc": "+1 Defense when HP below 25%"},
}

def check_held_item(c):
    """Trigger held item passively at end of turn. Returns message string or ''."""
    if not c.held_item:
        return ""
    item = c.held_item
    hdata = HELD_ITEMS.get(item)
    if not hdata:
        return ""

    # ── One-use berries ──────────────────────────────────────────
    if not c._held_item_used:
        if hdata["trigger"] == "status" and c.status is not None:
            c.status = None
            c.sleep_turns = 0
            c.confusion_turns = 0
            c._held_item_used = True
            c.gain_friendship(2)
            return f"  {C.GREEN}{_dname(c)}'s {item} cured its status!{C.RESET}"
        if hdata["trigger"] == "half_hp" and c.hp <= c.max_hp // 2:
            heal = c.max_hp // 4 if item == "Sitrus Berry" else 10
            actual = min(heal, c.max_hp - c.hp)
            c.heal(heal)
            c._held_item_used = True
            c.gain_friendship(2)
            return f"  {C.GREEN}{_dname(c)}'s {item} restored {actual} HP!{C.RESET}"

        # Seasonal stat berries: trigger below 25% HP
        if hdata["trigger"] in ("low_hp_spd", "low_hp_atk", "low_hp_def") and c.hp <= c.max_hp // 4:
            stat_map = {"low_hp_spd": "spd", "low_hp_atk": "atk", "low_hp_def": "def"}
            stat = stat_map[hdata["trigger"]]
            c.apply_stage(stat, 1)
            c._held_item_used = True
            c.gain_friendship(2)
            stat_names = {"spd": "Speed", "atk": "Attack", "def": "Defense"}
            return f"  {C.GREEN}{_dname(c)}'s {item} raised its {stat_names[stat]}!{C.RESET}"

    # ── Leftovers: heal 1/16 max HP every turn (never consumed) ──
    if hdata["trigger"] == "eot" and c.is_alive() and c.hp < c.max_hp:
        heal = max(1, c.max_hp // 16)
        actual = min(heal, c.max_hp - c.hp)
        c.heal(heal)
        return f"  {C.GREEN}{_dname(c)}'s Leftovers restored {actual} HP!{C.RESET}"

    return ""


def held_item_damage_mult(attacker):
    """Return outgoing damage multiplier from combat held items (Life Orb, Choice Band)."""
    item = attacker.held_item
    if item == "Life Orb":
        return 1.3
    if item == "Choice Band":
        return 1.5
    return 1.0


def held_item_crit_bonus(attacker):
    """Return extra crit rolls for Scope Lens (doubles crit chance: 1-in-8 instead of 1-in-16)."""
    return attacker.held_item == "Scope Lens"


def apply_life_orb_recoil(attacker):
    """Drain 10% max HP after attacking with Life Orb. Returns message or ''."""
    if attacker.held_item != "Life Orb" or not attacker.is_alive():
        return ""
    dmg = max(1, attacker.max_hp // 10)
    attacker.take_damage(dmg)
    return f"  {C.RED}{_dname(attacker)} is hurt by Life Orb recoil! ({dmg} dmg){C.RESET}"


def apply_shell_bell_heal(attacker, dmg_dealt):
    """Restore 1/8 of damage dealt when holding Shell Bell. Returns message or ''."""
    if attacker.held_item != "Shell Bell" or dmg_dealt <= 0 or not attacker.is_alive():
        return ""
    if attacker.hp >= attacker.max_hp:
        return ""
    heal = max(1, dmg_dealt // 8)
    actual = min(heal, attacker.max_hp - attacker.hp)
    attacker.heal(heal)
    return f"  {C.GREEN}{_dname(attacker)}'s Shell Bell restored {actual} HP!{C.RESET}"


def check_choice_band_lock(attacker, move_name):
    """
    Enforce Choice Band move lock.
    Returns (allowed: bool, message: str).
    Sets attacker._choice_lock to move_name on first use.
    """
    if attacker.held_item != "Choice Band":
        return True, ""
    locked = getattr(attacker, "_choice_lock", None)
    if locked is None:
        # First move this battle — lock to it
        attacker._choice_lock = move_name
        return True, ""
    if move_name != locked:
        return False, (f"  {C.YELLOW}{_dname(attacker)} is locked into {locked} "
                       f"by Choice Band!{C.RESET}")
    return True, ""


# ─────────────────────────────────────────────
#  ENEMY AI
# ─────────────────────────────────────────────

def enemy_move(enemy, player, weather=None):
    # Pre-turn status check
    can_act, pre_msg = preturn_status_check(enemy)
    if pre_msg:
        slow_print(pre_msg)
    if not can_act:
        return

    available = [m for m in enemy.moves if enemy.pp.get(m, 0) > 0]
    if not available:
        slow_print(f"  {_dname(enemy)} has no moves left! It struggles!")
        dmg = max(1, enemy.max_hp // 8)
        player.take_damage(dmg)
        return

    # Smarter AI: score each move by expected damage
    from data.creatures import TYPE_CHART
    best_move = None
    best_score = -1
    for m in available:
        move = MOVES[m]
        effect = move.get("effect", "")
        # Don't try to sleep/freeze/confuse if player already has a status
        if effect in ("sleep", "freeze", "confuse", "poison", "burn", "paralyzed"):
            if player.status is not None:
                score = 5   # low priority
            else:
                score = 35 if effect in ("sleep", "freeze") else 25
        elif effect in ("raise_atk", "raise_def", "raise_spd", "raise_atk2", "raise_spd2",
                         "raise_spatk", "raise_spatk2", "raise_spdef", "raise_spdef2"):
            # Self-buff: more valuable early; deprioritize if already capped
            stat = {"raise_atk": "atk", "raise_def": "def", "raise_spd": "spd",
                    "raise_atk2": "atk", "raise_spd2": "spd",
                    "raise_spatk": "spatk", "raise_spatk2": "spatk",
                    "raise_spdef": "spdef", "raise_spdef2": "spdef"}.get(effect, "atk")
            score = 30 if enemy.stages.get(stat, 0) < 4 else 5
        elif move["power"] == 0:
            score = 20
        else:
            move_type = move["type"]
            eff = 1.0
            for t in player.types:
                eff *= TYPE_CHART.get(move_type, {}).get(t, 1.0)
            w_mult = weather_move_mult(weather, move_type)
            stab = 1.5 if move_type in enemy.types else 1.0
            score = move["power"] * eff * w_mult * stab
        if score > best_score:
            best_score = score
            best_move = m

    move_name = best_move
    enemy.pp[move_name] -= 1
    move = MOVES[move_name]
    slow_print(f"  {C.RED}{_dname(enemy)}{C.RESET} used {C.BOLD}{move_name}{C.RESET}!")

    # Accuracy check for enemy (respects player's evasion/enemy's acc stage)
    if move["power"] != 0:
        acc_mult = enemy.stage_mult("acc")
        adjusted_acc = int(move["accuracy"] * acc_mult)
        if random.randint(1, 100) > adjusted_acc:
            slow_print(f"  {C.YELLOW}{_dname(enemy)}'s attack missed!{C.RESET}")
            return

    effect = move.get("effect", "")
    # Ground-type immunity check (Levitate) — check the DEFENDER
    if move["type"] == "ground" and ability_blocks_ground(player):
        slow_print(f"  {C.GRAY}{player.name} is unaffected! (Levitate){C.RESET}")
        return

    # Two-turn charge moves (Solar Beam, Skull Bash, Sky Attack)
    if effect == "charge":
        if not getattr(enemy, '_charging', None):
            # First turn: announce charging, apply any charge boost
            enemy._charging = move_name
            slow_print(f"  {C.CYAN}{_dname(enemy)} is gathering energy!{C.RESET}")
            charge_boost = move.get("charge_boost")
            if charge_boost:
                msg = apply_stat_effect(f"raise_{charge_boost}", enemy, enemy.name)
                if msg: slow_print(msg)
            return
        elif enemy._charging == move_name:
            # Second turn: fire the move (fall through to damage below)
            enemy._charging = None
            effect = ""  # clear so damage block runs normally
        else:
            # Charging a different move — reset and start fresh
            enemy._charging = move_name
            slow_print(f"  {C.CYAN}{_dname(enemy)} is charging {move_name}!{C.RESET}")
            return

    if move["power"] == 0:
        # Pure status / stat move
        if effect in ("sleep", "freeze", "confuse"):
            msg = inflict_status(effect, player)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect == "poison":
            msg = inflict_status("poison", player, chance=1.0)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect == "burn":
            msg = inflict_status("burn", player, chance=1.0)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect == "paralyzed":
            msg = inflict_status("paralyzed", player, chance=1.0)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect in ("raise_atk", "raise_def", "raise_spd", "raise_atk2", "raise_spd2",
                         "raise_spatk", "raise_spatk2", "raise_spdef", "raise_spdef2"):
            msg = apply_stat_effect(effect, enemy, enemy.name)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        else:
            msg = apply_stat_effect(effect, player, enemy.name)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        return

    # Multi-hit moves (enemy)
    if effect == "multi_hit":
        hits = random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5])[0]
        total_dmg = 0
        for _ in range(hits):
            if not player.is_alive(): break
            dmg, eff_m, crit_m = calc_damage(enemy, player, move_name, weather)
            dmg = int(dmg * held_item_damage_mult(enemy))
            player.take_damage(dmg)
            total_dmg += dmg
        slow_print(f"  {_dname(enemy)} hit {hits} times for {C.RED}{total_dmg}{C.RESET} total damage!")
        msg = apply_life_orb_recoil(enemy)
        if msg: slow_print(msg)
        msg = check_held_item(player)
        if msg: slow_print(msg)
        return

    dmg, eff, crit = calc_damage(enemy, player, move_name, weather)
    dmg = int(dmg * held_item_damage_mult(enemy))
    player.take_damage(dmg)
    if crit: crit_flash()
    slow_print(f"  {_dname(enemy)} dealt {C.RED}{dmg}{C.RESET} damage!  {effectiveness_msg(eff)}")

    # ── Post-hit held item effects (enemy attacker) ──────────────
    msg = apply_life_orb_recoil(enemy)
    if msg: slow_print(msg)
    msg = apply_shell_bell_heal(enemy, dmg)
    if msg: slow_print(msg)

    # Ability: on_hit_received (player's ability fires when player is hit)
    for msg in fire_on_hit_received(player, enemy, move_name, weather):
        slow_print(msg)

    effect = move.get("effect", "")
    if effect == "poison":
        msg = inflict_status("poison", player, chance=0.30)
        if msg: slow_print(msg)
    elif effect == "burn":
        msg = inflict_status("burn", player, chance=0.30)
        if msg: slow_print(msg)
    elif effect == "paralyzed":
        msg = inflict_status("paralyzed", player, chance=0.25)
        if msg: slow_print(msg)
    elif effect == "freeze" and player.status is None:
        msg = inflict_status("freeze", player, chance=0.10)  # secondary freeze from damaging moves
        if msg: slow_print(msg)
    elif effect == "confuse" and player.status is None:
        msg = inflict_status("confuse", player, chance=0.20)
        if msg: slow_print(msg)
    elif effect in STAT_EFFECTS:
        msg = apply_stat_effect(effect, player, enemy.name)
        if msg:
            slow_print(msg)

    # Leech Life: heal enemy attacker for half damage dealt
    if effect == "leech" and dmg > 0:
        heal_amt = max(1, dmg // 2)
        enemy.heal(heal_amt)
        slow_print(f"  {C.RED}{_dname(enemy)} drained {heal_amt} HP!{C.RESET}")

    msg = check_held_item(player)
    if msg:
        slow_print(msg)


# ─────────────────────────────────────────────
#  PLAYER ATTACK
# ─────────────────────────────────────────────

def player_attack(player, enemy, move_name, boosts, weather=None):
    move = MOVES[move_name]

    # ── Choice Band lock check ──────────────────────────────────
    allowed, lock_msg = check_choice_band_lock(player, move_name)
    if not allowed:
        slow_print(lock_msg)
        return

    player.pp[move_name] -= 1
    slow_print(f"\n  {C.GREEN}{_dname(player)}{C.RESET} used {C.BOLD}{move_name}{C.RESET}!")

    # Pre-turn status check (sleep, freeze, paralysis, confusion)
    can_act, pre_msg = preturn_status_check(player)
    if pre_msg:
        slow_print(pre_msg)
    if not can_act:
        return

    # Ground-type immunity check (Levitate) — check the DEFENDER
    if move["type"] == "ground" and ability_blocks_ground(enemy):
        slow_print(f"  {C.GRAY}{enemy.name} is unaffected! (Levitate){C.RESET}")
        return

    if move["power"] == 0:
        effect = move.get("effect", "")
        # Pure status/stat moves
        if effect in ("sleep", "freeze", "confuse"):
            msg = inflict_status(effect, enemy)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect in ("poison", "burn", "paralyzed"):
            msg = inflict_status(effect, enemy, chance=1.0)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        elif effect in ("raise_atk", "raise_def", "raise_spd", "raise_atk2", "raise_spd2",
                         "raise_spatk", "raise_spatk2", "raise_spdef", "raise_spdef2"):
            # Self-buff: target is the attacker
            msg = apply_stat_effect(effect, player, player.name)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        else:
            msg = apply_stat_effect(effect, enemy, player.name)
            slow_print(msg if msg else f"  {C.GRAY}(It had no effect.){C.RESET}")
        return

    # Accuracy check (modified by acc stage)
    acc_mult = player.stage_mult("acc")
    adjusted_acc = int(move["accuracy"] * acc_mult)
    if random.randint(1, 100) > adjusted_acc:
        slow_print(f"  {C.YELLOW}The move missed!{C.RESET}")
        return

    # Multi-hit moves (Fury Swipes: 2-5 hits)
    effect = move.get("effect", "")
    if effect == "multi_hit":
        hits = random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5])[0]
        total_dmg = 0
        for hit_num in range(hits):
            if not enemy.is_alive(): break
            dmg, eff, crit = calc_damage(player, enemy, move_name, weather)
            move_cat = MOVES[move_name].get("category", "physical")
            boost_mult = boosts.get("spatk", 1.0) if move_cat == "special" else boosts.get("atk", 1.0)
            dmg = int(dmg * boost_mult * held_item_damage_mult(player))
            enemy.take_damage(dmg)
            total_dmg += dmg
        slow_print(f"  {_dname(player)} hit {hits} times for {C.GREEN}{total_dmg}{C.RESET} total damage!")
        msg = apply_life_orb_recoil(player)
        if msg: slow_print(msg)
        msg = apply_shell_bell_heal(player, total_dmg)
        if msg: slow_print(msg)
        return

    dmg, eff, crit = calc_damage(player, enemy, move_name, weather)
    # Apply external ATK/SPATK boost (X Attack / X Sp.Atk items) + held item damage mult
    move_category = move.get("category", "physical")
    atk_boost = boosts.get("spatk", 1.0) if move_category == "special" else boosts.get("atk", 1.0)
    dmg = int(dmg * atk_boost * held_item_damage_mult(player))
    enemy.take_damage(dmg)
    if crit: crit_flash()
    slow_print(f"  {_dname(player)} dealt {C.GREEN}{dmg}{C.RESET} damage!  {effectiveness_msg(eff)}")

    # ── Post-hit held item effects ───────────────────────────────
    msg = apply_life_orb_recoil(player)
    if msg: slow_print(msg)
    msg = apply_shell_bell_heal(player, dmg)
    if msg: slow_print(msg)

    # Ability: on_hit_received (Static, Poison Touch, Spore Cloud)
    for msg in fire_on_hit_received(enemy, player, move_name, weather):
        slow_print(msg)

    # Secondary effects
    effect = move.get("effect", "")
    if effect == "poison":
        msg = inflict_status("poison", enemy, chance=0.30)
        if msg: slow_print(msg)
    elif effect == "burn":
        msg = inflict_status("burn", enemy, chance=0.30)
        if msg: slow_print(msg)
    elif effect == "paralyzed":
        msg = inflict_status("paralyzed", enemy, chance=0.25)
        if msg: slow_print(msg)
    elif effect == "freeze":
        msg = inflict_status("freeze", enemy, chance=0.10)
        if msg: slow_print(msg)
    elif effect == "confuse":
        msg = inflict_status("confuse", enemy, chance=0.20)
        if msg: slow_print(msg)
    elif effect in STAT_EFFECTS:
        msg = apply_stat_effect(effect, enemy, player.name)
        if msg:
            slow_print(msg)

    # Leech Life: heal attacker for half damage dealt
    if effect == "leech" and dmg > 0:
        heal_amt = max(1, dmg // 2)
        player.heal(heal_amt)
        slow_print(f"  {C.GREEN}{_dname(player)} drained {heal_amt} HP!{C.RESET}")


# ─────────────────────────────────────────────
#  STATUS END-OF-TURN
# ─────────────────────────────────────────────

def apply_status_damage(c):
    """Apply end-of-turn status damage. Returns True if creature faints."""
    n = _dname(c)
    if c.status == "poison":
        dmg = max(1, c.max_hp // 8)
        c.take_damage(dmg)
        slow_print(f"  {C.MAGENTA}{n} is hurt by poison! ({dmg} dmg){C.RESET}")
        if not c.is_alive():
            return True
    elif c.status == "burn":
        dmg = max(1, c.max_hp // 16)
        c.take_damage(dmg)
        slow_print(f"  {C.RED}{n} is hurt by burn! ({dmg} dmg){C.RESET}")
        if not c.is_alive():
            return True
    # sleep/freeze/confuse/paralyzed have no end-of-turn damage
    return False


# ─────────────────────────────────────────────
#  SWITCH
# ─────────────────────────────────────────────

def switch_creature(team, current, forced=False):
    alive = [c for c in team if c.is_alive() and c is not current]
    if not alive:
        if forced:
            slow_print(f"  {C.RED}No more creatures to send out!{C.RESET}")
        return None
    opts = [f"{c.name} Lv.{c.level}  {hp_bar(c.hp, c.max_hp, 12)}" for c in alive]
    if not forced:
        opts.append("← Cancel")
    idx = menu("Send out which creature?", opts)
    if not forced and idx == len(alive):
        return None
    chosen = alive[idx]
    slow_print(f"  {C.GREEN}Go, {chosen.name}!{C.RESET}")
    chosen.reset_stages()
    chosen._held_item_used = False   # one-use berry resets on switch
    chosen._choice_lock    = None   # Choice Band lock resets on switch
    return chosen


# ─────────────────────────────────────────────
#  RUN CHANCE  (speed-based)
# ─────────────────────────────────────────────

def run_chance(player_c, enemy_c):
    """Probability of successfully fleeing, based on speed."""
    ps = player_c.effective_spd()
    es = enemy_c.effective_spd()
    if ps >= es:
        return 0.9
    ratio = ps / max(1, es)
    return max(0.25, ratio * 0.9)


# ─────────────────────────────────────────────
#  BATTLE SUMMARY
# ─────────────────────────────────────────────

class BattleSummary:
    def __init__(self):
        self.player_dmg_dealt  = 0
        self.player_dmg_taken  = 0
        self.turns             = 0
        self.items_used        = 0
        self.switches          = 0
        self.moves_used        = 0   # total damaging moves fired
        self.moves_super       = 0   # super-effective hits
        self.moves_resisted    = 0   # not-very-effective or immune hits
        self.enemy_types       = []  # foe's types (set once, used for tip generation)
        self.player_start_hp   = 0   # lead's HP at battle start (for grade calc)

    def _grade(self):
        """Return (letter, color) performance grade based on battle stats."""
        # Points start at 100; deduct for each inefficiency
        pts = 100
        # Turns: free up to 3, then -6 per extra turn
        if self.turns > 3:
            pts -= (self.turns - 3) * 6
        # Items: -15 each
        pts -= self.items_used * 15
        # Switches: -10 each
        pts -= self.switches * 10
        # Damage taken as % of start HP: -0.3 per percent
        if self.player_start_hp > 0:
            pct_taken = (self.player_dmg_taken / self.player_start_hp) * 100
            pts -= int(pct_taken * 0.3)
        pts = max(0, pts)
        if pts >= 90:
            return "S", C.YELLOW + C.BOLD
        elif pts >= 70:
            return "A", C.GREEN + C.BOLD
        elif pts >= 45:
            return "B", C.CYAN
        else:
            return "C", C.GRAY

    def show(self, force=False):
        """Only display summary if the battle lasted more than 1 turn (or forced for trainer/gym battles)."""
        if self.turns <= 1 and not force:
            return
        section("📊  BATTLE SUMMARY")
        # Performance grade
        grade, grade_color = self._grade()
        print(f"  Performance  : {grade_color}{grade}{C.RESET}")
        print(f"  Turns fought : {C.BOLD}{self.turns}{C.RESET}")
        print(f"  Damage dealt : {C.GREEN}{self.player_dmg_dealt}{C.RESET}")
        print(f"  Damage taken : {C.RED}{self.player_dmg_taken}{C.RESET}")
        if self.items_used:
            print(f"  Items used   : {C.YELLOW}{self.items_used}{C.RESET}")
        if self.switches:
            print(f"  Switches     : {C.CYAN}{self.switches}{C.RESET}")
        # Move-efficiency tip
        if self.moves_used > 0:
            if self.moves_super > 0 and self.moves_resisted == 0:
                print(f"  {C.GREEN}💡 Tip: Great type coverage — your moves were super effective!{C.RESET}")
            elif self.moves_resisted > 0 and self.moves_super == 0:
                _type_str = "/".join(self.enemy_types) if self.enemy_types else "the foe"
                print(f"  {C.YELLOW}💡 Tip: Your moves were often resisted by {_type_str}-types. "
                      f"Try a creature with better type coverage.{C.RESET}")
            elif self.moves_super > 0 and self.moves_resisted > 0:
                print(f"  {C.CYAN}💡 Tip: Mixed effectiveness — some moves hit hard, others were resisted.{C.RESET}")


# ─────────────────────────────────────────────
#  MAIN BATTLE FUNCTION
#  Returns: ("win"|"lose"|"ran"|"caught", obj)
# ─────────────────────────────────────────────

def run_battle(player_c, enemy_c, inventory, team,
               wild=True, trainer_name=None, weather=None):

    label = "Wild" if wild else f"Trainer {trainer_name}'s"
    banner(f"  {'Wild Battle' if wild else 'Trainer Battle'}  ", C.RED)

    # Show gym leader art if applicable
    if not wild and trainer_name in GYM_LEADER_ART:
        print(GYM_LEADER_ART[trainer_name])

    slow_print(f"  A {C.BOLD}{label} {enemy_c.name}{C.RESET} appeared!", 0.03)
    if weather:
        weather_icons = {"Sunny": "☀", "Rainy": "🌧", "Sandstorm": "🌪", "Hail": "❄"}
        icon = weather_icons.get(weather, "☁")
        slow_print(f"  {C.CYAN}{icon}  The weather is {weather}!{C.RESET}")
    press_enter()

    boosts  = {"atk": 1.0, "def": 1.0, "spatk": 1.0, "spdef": 1.0}
    reset_battle_log()

    summary = BattleSummary()
    summary.enemy_types = list(enemy_c.types)   # capture foe type(s) for tip generation
    summary.player_start_hp = player_c.hp       # record lead's HP for grade calc

    # Assign display tags so messages say "Your Flambit" vs "Wild Flambit" (or "Foe Flambit")

    player_c._battle_tag = "Your"
    enemy_c._battle_tag  = "Wild" if wild else "Foe"

    player_c.reset_stages()
    player_c._held_item_used = False
    player_c._choice_lock    = None
    player_c._xdef_boost     = 1.0
    player_c._xspdef_boost   = 1.0
    player_c._xspd_boost     = 1.0
    enemy_c.reset_stages()
    enemy_c._held_item_used  = False
    enemy_c._choice_lock     = None
    enemy_c._xdef_boost      = 1.0
    enemy_c._xspdef_boost    = 1.0
    enemy_c._xspd_boost      = 1.0

    # Fire on_entry abilities for both sides at battle start
    for msg in fire_on_entry(player_c, enemy_c, weather):
        slow_print(msg)
    for msg in fire_on_entry(enemy_c, player_c, weather):
        slow_print(msg)

    first_turn = True
    # Turn recap: tracks last exchange for display at top of next turn
    _recap = {"player_move": None, "player_dmg": 0, "enemy_move": None, "enemy_dmg": 0}
    while True:
        if not first_turn:
            press_enter()
        first_turn = False
        clear()
        battle_ui(player_c, enemy_c, wild, weather, trainer_name=trainer_name)

        # Show last-turn recap (after first turn, if something happened)
        if summary.turns > 0 and (_recap["player_move"] or _recap["enemy_move"] or
                                   _recap["player_dmg"] or _recap["enemy_dmg"]):
            p_line = (f"{C.GREEN}↑ {_dname(player_c)}: {_recap['player_move']} "
                      f"→ {_recap['player_dmg']} dmg dealt{C.RESET}"
                      if _recap["player_move"] else
                      f"{C.GRAY}↑ {_dname(player_c)}: no move{C.RESET}")
            e_line = (f"{C.RED}↓ {_dname(enemy_c)}: {_recap['enemy_move']} "
                      f"→ {_recap['enemy_dmg']} dmg taken{C.RESET}"
                      if _recap["enemy_move"] else
                      f"{C.GRAY}↓ {_dname(enemy_c)}: no move{C.RESET}")
            print(f"  {C.GRAY}─── Last turn ───{C.RESET}  {p_line}   {e_line}")
        # Reset recap for this turn
        _recap = {"player_move": None, "player_dmg": 0, "enemy_move": None, "enemy_dmg": 0}

        # Brief weather reminder at the start of each turn
        if weather:
            _wx_icon  = {"Sunny": "☀", "Rainy": "🌧", "Sandstorm": "🌪", "Hail": "❄"}.get(weather, "☁")
            _wx_hints = {
                "Sunny":     "Fire moves boosted, Water moves weakened.",
                "Rainy":     "Water moves boosted, Fire moves weakened.",
                "Sandstorm": "Rock/Steel/Ground take no chip; others lose 1/16 HP each turn.",
                "Hail":      "Ice-types take no chip; others lose 1/16 HP each turn.",
            }
            slow_print(f"  {C.CYAN}{_wx_icon}  {weather}: {_wx_hints.get(weather, '')}{C.RESET}", 0.01)

        options = ["⚔  Fight", "🎒  Bag", "🔄  Switch Creature", "📊  Stats", "📜  Log"]
        if wild:
            options.append("🏃  Run")

        choice = menu("What will you do?", options)

        took_turn  = False
        fought     = False
        move_name  = None


        # ══ FIGHT ══
        if choice == 0:
            available_moves = [m for m in player_c.moves if player_c.pp.get(m, 0) > 0]
            if not available_moves:
                slow_print(f"{C.RED}No moves left! {_dname(player_c)} struggles!{C.RESET}")
                dmg = max(1, player_c.max_hp // 8)
                player_c.take_damage(dmg)
                summary.player_dmg_taken += dmg
                took_turn = True
            else:
                def _pwr_tier(pwr):
                    if pwr == 0:
                        return f"{C.GRAY}—   {C.RESET}"
                    elif pwr <= 40:
                        return f"{C.YELLOW}★   {C.RESET}"
                    elif pwr <= 80:
                        return f"{C.YELLOW}★★  {C.RESET}"
                    else:
                        return f"{C.RED}★★★ {C.RESET}"
                def _acc_tag(acc):
                    if acc >= 100:
                        return f"{C.GRAY}—  {C.RESET}"
                    elif acc >= 90:
                        return f"{C.WHITE}{acc}%{C.RESET}"
                    elif acc >= 75:
                        return f"{C.YELLOW}{acc}%{C.RESET}"
                    else:
                        return f"{C.RED}{acc}%{C.RESET}"
                def _cat_tag(cat):
                    if cat == "physical":
                        return f"{C.RED}Phys{C.RESET}"
                    elif cat == "special":
                        return f"{C.CYAN}Spec{C.RESET}"
                    else:
                        return f"{C.GRAY}Stat{C.RESET}"
                move_opts = [
                    (f"{m:<16}  {C.GRAY}PP {player_c.pp[m]}/{MOVES[m]['pp']}"
                     f"  Pwr:{MOVES[m]['power']:<4}{_pwr_tier(MOVES[m]['power'])}"
                     f"Acc:{_acc_tag(MOVES[m]['accuracy'])}  "
                     f"{_cat_tag(MOVES[m].get('category','status'))}  "
                     f"{TYPE_COLORS.get(MOVES[m]['type'], C.WHITE)}[{MOVES[m]['type'].upper():<8}]{C.RESET}"
                     f"  {type_hint(MOVES[m]['type'], enemy_c.types)}"
                     f"{(' ' + C.CYAN + '[FAST]' + C.RESET) if MOVES[m].get('priority',0) > 0 else ''}"
                     f"\n     {C.GRAY}{MOVES[m].get('desc', '')}{C.RESET}")
                    for m in player_c.moves
                ]


                if mc == len(player_c.moves):
                    continue
                move_name = player_c.moves[mc]
                if player_c.pp.get(move_name, 0) == 0:
                    slow_print(f"{C.RED}No PP left for that move!{C.RESET}")
                    continue

                hp_before = enemy_c.hp
                player_attack(player_c, enemy_c, move_name, boosts, weather)
                _dmg_dealt = max(0, hp_before - enemy_c.hp)
                summary.player_dmg_dealt += _dmg_dealt
                _recap["player_move"] = move_name
                _recap["player_dmg"]  = _dmg_dealt
                # Track move type-effectiveness for post-battle tip
                _move_type = MOVES.get(move_name, {}).get("type", "")
                if _move_type:
                    from data.creatures import TYPE_CHART as _TC
                    _eff = 1.0
                    for _t in enemy_c.types:
                        _eff *= _TC.get(_move_type, {}).get(_t, 1.0)
                    if MOVES.get(move_name, {}).get("power", 0) > 0:
                        summary.moves_used += 1
                        if _eff >= 2.0:
                            summary.moves_super += 1
                        elif _eff < 1.0:
                            summary.moves_resisted += 1
                took_turn = True
                fought    = True

        # ══ BAG ══
        elif choice == 1:
            usable = {k: v for k, v in inventory.items()
                      if v > 0 and ITEMS.get(k, {}).get("type") in
                      ("heal", "cure", "revive", "capture", "pp", "boost")}

            if not usable:
                slow_print(f"{C.YELLOW}No usable items!{C.RESET}")
                continue

            # Group into categories when there are enough usable items that a flat
            # list gets hard to scan -- mirrors the overworld Bag's grouping (main.py).
            _battle_bag_cats = [
                ("🎯  Capture",      {"capture"}),
                ("💊  Healing",      {"heal", "revive"}),
                ("✨  Status Cures",     {"cure"}),
                ("🔋  PP Restore",   {"pp"}),
                ("📈  Battle Boosts", {"boost"}),
            ]
            _grouped = {}
            for _k in usable:
                _itype = ITEMS.get(_k, {}).get("type", "")
                _label = next((lbl for lbl, types in _battle_bag_cats if _itype in types), "🍬  Other")
                _grouped.setdefault(_label, []).append(_k)
            _cat_labels = [lbl for lbl, _ in _battle_bag_cats if lbl in _grouped]
            if "🍬  Other" in _grouped:
                _cat_labels.append("🍬  Other")

            if len(_cat_labels) <= 1:
                active_keys = list(usable.keys())
            else:
                _cat_opts = [f"{lbl}  {C.GRAY}({len(_grouped[lbl])} item{'s' if len(_grouped[lbl]) != 1 else ''}){C.RESET}"
                             for lbl in _cat_labels]
                _cat_opts.append("← Back")
                _cc = menu("Use item:", _cat_opts)
                if _cc == len(_cat_labels):
                    continue
                active_keys = _grouped[_cat_labels[_cc]]

            bag_opts = [f"{item} x{usable[item]}  {C.GRAY}({ITEMS[item]['desc']}){C.RESET}"
                        for item in active_keys]
            bag_opts.append("← Back")
            bc = menu("Use item:", bag_opts)
            if bc == len(active_keys):
                continue

            item_name = active_keys[bc]
            idata = ITEMS[item_name]
            inventory[item_name] -= 1
            took_turn = True
            summary.items_used += 1

            if idata["type"] == "heal":
                healed = min(idata["amount"], player_c.max_hp - player_c.hp)
                player_c.heal(idata["amount"])
                cured_status = False
                if idata.get("amount", 0) >= 9999:
                    if player_c.status:
                        cured_status = True
                    player_c.status = None
                if healed > 0:
                    slow_print(f"  {C.GREEN}{player_c.name} recovered {healed} HP!{C.RESET}")
                    if cured_status:
                        slow_print(f"  {C.GREEN}Status condition cleared!{C.RESET}")
                elif cured_status:
                    slow_print(f"  {C.GREEN}{player_c.name}'s status condition was cleared!{C.RESET}")
                else:
                    slow_print(f"  {C.YELLOW}{player_c.name} is already at full HP!{C.RESET}")

            elif idata["type"] == "cure":
                target_status = idata["status"]
                if target_status == "all":
                    player_c.status = None
                    player_c.sleep_turns = 0
                    player_c.confusion_turns = 0
                    slow_print(f"  {C.GREEN}All status effects cleared!{C.RESET}")
                elif player_c.status == target_status:
                    player_c.status = None
                    player_c.sleep_turns = 0
                    player_c.confusion_turns = 0
                    slow_print(f"  {C.GREEN}{player_c.name} was cured!{C.RESET}")
                else:
                    if player_c.status is None:
                        slow_print(f"  {C.YELLOW}{player_c.name} has no status condition.{C.RESET}")
                    else:
                        slow_print(f"  {C.YELLOW}That item doesn't cure {player_c.status.title()}.{C.RESET}")
                    inventory[item_name] += 1
                    took_turn = False

            elif idata["type"] == "capture":
                if not wild:
                    slow_print(f"  {C.RED}You can't capture trainer's creatures!{C.RESET}")
                    inventory[item_name] += 1
                    took_turn = False
                    continue
                caught, shakes = animated_capture(enemy_c, item_name, idata["rate"], lead=player_c)
                if caught:
                    slow_print(f"  {C.GREEN}★  Gotcha! {enemy_c.name} was caught!{C.RESET}")
                    print('\a', end='', flush=True)
                    press_enter()
                    return "caught", enemy_c
                else:
                    slow_print(f"  {C.RED}Oh no! {enemy_c.name} broke free!{C.RESET}")
                    # Shake-count feedback: tells the player how close they were
                    _shake_hints = {
                        0: f"  {C.GRAY}It didn't even twitch. Weaken it more or try a better ball.{C.RESET}",
                        1: f"  {C.YELLOW}One shake — try weakening it further or upgrading your ball.{C.RESET}",
                        2: f"  {C.YELLOW}Two shakes! Very close — try a Great Ball or weaken it more.{C.RESET}",
                        3: f"  {C.GREEN}Three shakes — tantalizingly close! An Ultra or Master Ball should do it.{C.RESET}",
                    }
                    slow_print(_shake_hints.get(shakes, ""))


            elif idata["type"] == "revive":
                fainted = [c for c in team if not c.is_alive()]
                if not fainted:
                    slow_print(f"  {C.YELLOW}No fainted creatures!{C.RESET}")
                    inventory[item_name] += 1
                    took_turn = False
                else:
                    r_opts = [f"{c.name} Lv.{c.level}" for c in fainted] + ["← Back"]
                    rc = menu("Revive which?", r_opts)
                    if rc == len(fainted):
                        inventory[item_name] += 1
                        took_turn = False
                    else:
                        target = fainted[rc]
                        target.hp = int(target.max_hp * idata["amount"])
                        slow_print(f"  {C.GREEN}{target.name} was revived!{C.RESET}")

            elif idata["type"] == "pp":
                for m in player_c.moves:
                    max_pp = MOVES[m]["pp"]
                    player_c.pp[m] = min(max_pp, player_c.pp.get(m, 0) + idata["amount"])
                slow_print(f"  {C.GREEN}Move PP restored!{C.RESET}")

            elif idata["type"] == "boost":
                stat = idata["stat"]
                boosts[stat] = round(boosts.get(stat, 1.0) * idata["amount"], 2)
                if stat == "def":
                    # Store on the creature so calc_damage can see it
                    player_c._xdef_boost = boosts["def"]
                elif stat == "spdef":
                    player_c._xspdef_boost = boosts["spdef"]
                elif stat == "spd":
                    player_c._xspd_boost = boosts["spd"]
                slow_print(f"  {C.GREEN}{player_c.name}'s {STAT_NAMES.get(stat, stat.upper())} rose!{C.RESET}")

        # ══ SWITCH ══
        elif choice == 2:
            new_c = switch_creature(team, player_c, forced=False)
            if new_c:
                player_c = new_c
                boosts = {"atk": 1.0, "def": 1.0, "spatk": 1.0, "spdef": 1.0}
                player_c._xdef_boost   = 1.0
                player_c._xspdef_boost = 1.0
                player_c._xspd_boost   = 1.0
                for msg in fire_on_entry(player_c, enemy_c, weather):
                    slow_print(msg)
                took_turn = True
                summary.switches += 1
            else:
                continue

        # ══ STATS ══
        elif choice == 3:
            def _stage_bar(val):
                if val > 0: return f"{C.GREEN}+{val}{C.RESET}"
                if val < 0: return f"{C.RED}{val}{C.RESET}"
                return f"{C.GRAY} 0{C.RESET}"
            section("📊  STAT STAGES")
            print(f"  {'':18} {'ATK':>5} {'DEF':>5} {'SPATK':>6} {'SPDEF':>6} {'SPD':>5} {'ACC':>5}")
            for label, c in [(f"Your {player_c.name}", player_c), (f"Foe  {enemy_c.name}", enemy_c)]:
                atk   = _stage_bar(c.stages.get('atk',   0))
                df    = _stage_bar(c.stages.get('def',   0))
                spatk = _stage_bar(c.stages.get('spatk', 0))
                spdef = _stage_bar(c.stages.get('spdef', 0))
                spd   = _stage_bar(c.stages.get('spd',   0))
                acc   = _stage_bar(c.stages.get('acc',   0))
                print(f"  {label:<18} {atk:>5} {df:>5} {spatk:>6} {spdef:>6} {spd:>5} {acc:>5}")
            # Show nature for player creature
            if getattr(player_c, 'nature', None):
                from engine.core import NATURES
                boost, lower = NATURES.get(player_c.nature, (None, None))
                if boost and lower:
                    nature_tag = (f"{C.CYAN}{player_c.nature}{C.RESET}"
                                  f"  ({C.GREEN}+{boost}{C.RESET} / {C.RED}-{lower}{C.RESET})")
                else:
                    nature_tag = f"{C.GRAY}{player_c.nature} (neutral){C.RESET}"
                print(f"\n  {player_c.name}'s nature: {nature_tag}")
            press_enter()
            continue

        # ══ LOG ══
        elif choice == 4:
            show_battle_log()
            continue

        # ══ RUN ══
        elif choice == 5 and wild:

            chance = run_chance(player_c, enemy_c)
            if random.random() < chance:
                slow_print(f"  {C.CYAN}Got away safely!{C.RESET}")
                press_enter()
                return "ran", None
            else:
                slow_print(f"  {C.RED}Can't escape!{C.RESET}")
                took_turn = True

        # ── Check enemy fainted (after player action) ──
        if not enemy_c.is_alive():
            slow_print(f"\n  {C.YELLOW}{_dname(enemy_c)} fainted!{C.RESET}")
            summary.show(force=not wild)
            press_enter()
            return "win", enemy_c

        if not took_turn:
            continue

        summary.turns += 1

        # ══ SPEED-BASED TURN ORDER (with priority moves) ══
        # Priority moves always go first regardless of speed.
        p_spd = player_c.effective_spd(weather)
        e_spd = enemy_c.effective_spd(weather)
        # Check player's move priority
        player_priority = 0
        if fought and move_name is not None:
            player_priority = MOVES.get(move_name, {}).get("priority", 0)
        enemy_goes_first = (e_spd > p_spd) and (player_priority == 0)

        if enemy_goes_first:
            if fought:
                slow_print(f"  {C.YELLOW}» {_dname(enemy_c)} is faster! (Spd {e_spd} vs {p_spd}){C.RESET}")
            # Enemy attacks BEFORE player's move resolves
            hp_before = player_c.hp
            enemy_move(enemy_c, player_c, weather)
            _e_dmg = max(0, hp_before - player_c.hp)
            summary.player_dmg_taken += _e_dmg
            _recap["enemy_move"] = f"{_dname(enemy_c)} attacked"
            _recap["enemy_dmg"]  = _e_dmg

            # Check player fainted before their move
            if not player_c.is_alive():
                slow_print(f"  {C.RED}{_dname(player_c)} fainted before it could move!{C.RESET}")
                new_c = switch_creature(team, player_c, forced=True)
                if new_c:
                    player_c = new_c
                    boosts = {"atk": 1.0, "def": 1.0, "spatk": 1.0, "spdef": 1.0}
                    player_c._xdef_boost   = 1.0
                    player_c._xspdef_boost = 1.0
                    player_c._xspd_boost   = 1.0
                    for msg in fire_on_entry(player_c, enemy_c, weather):
                        slow_print(msg)
                    slow_print(f"  {C.GREEN}{player_c.name} is sent out!{C.RESET}")
                    press_enter()
                else:
                    slow_print(f"  {C.RED}All your creatures fainted! You lose!{C.RESET}")
                    summary.show(force=not wild)
                    press_enter()
                    return "lose", None
                # Skip the player's queued move since creature switched
                continue

            # Now the player's already-selected move resolves (was taken above)
            # Check enemy faint after player's move (already recorded in summary)
            if not enemy_c.is_alive():
                slow_print(f"\n  {C.YELLOW}{_dname(enemy_c)} fainted!{C.RESET}")
                summary.show(force=not wild)
                press_enter()
                return "win", enemy_c
        else:
            if p_spd > e_spd and fought:
                slow_print(f"  {C.GREEN}» {_dname(player_c)} is faster! (Spd {p_spd} vs {e_spd}){C.RESET}")
            # Check enemy faint after player's move (already recorded in summary)
            if not enemy_c.is_alive():
                slow_print(f"\n  {C.YELLOW}{_dname(enemy_c)} fainted!{C.RESET}")
                summary.show(force=not wild)
                press_enter()
                return "win", enemy_c

            # ── Enemy turn (player was faster or tied) ──
            hp_before = player_c.hp
            enemy_move(enemy_c, player_c, weather)
            _e_dmg = max(0, hp_before - player_c.hp)
            summary.player_dmg_taken += _e_dmg
            _recap["enemy_move"] = f"{_dname(enemy_c)} attacked"
            _recap["enemy_dmg"]  = _e_dmg


        # ── End-of-turn: status damage ──
        apply_status_damage(player_c)
        apply_status_damage(enemy_c)

        # ── End-of-turn: passive abilities (Speed Boost, Ice Body, etc.) ──
        for msg in fire_end_of_turn(player_c, weather):
            slow_print(msg)
        for msg in fire_end_of_turn(enemy_c, weather):
            slow_print(msg)

        # ── End-of-turn: held items ──
        msg = check_held_item(player_c)
        if msg: slow_print(msg)
        msg = check_held_item(enemy_c)
        if msg: slow_print(msg)

        # ── End-of-turn: weather damage ──
        from engine.core import apply_weather_damage as _awd
        w_dmg_p = _awd(player_c, weather)
        if w_dmg_p:
            weather_icons = {"Sunny": "☀", "Rainy": "🌧", "Sandstorm": "🌪", "Hail": "❄"}
            icon = weather_icons.get(weather, "")
            slow_print(f"  {C.CYAN}{icon} {_dname(player_c)} is buffeted by {weather}! ({w_dmg_p} dmg){C.RESET}")
            summary.player_dmg_taken += w_dmg_p
        w_dmg_e = _awd(enemy_c, weather)
        if w_dmg_e:
            weather_icons = {"Sunny": "☀", "Rainy": "🌧", "Sandstorm": "🌪", "Hail": "❄"}
            icon = weather_icons.get(weather, "")
            slow_print(f"  {C.CYAN}{icon} {_dname(enemy_c)} is buffeted by {weather}! ({w_dmg_e} dmg){C.RESET}")

        # ── Check enemy faint (after end-of-turn) ──
        if not enemy_c.is_alive():
            slow_print(f"\n  {C.YELLOW}{_dname(enemy_c)} fainted!{C.RESET}")
            summary.show(force=not wild)
            press_enter()
            return "win", enemy_c

        # ── Check player faint ──
        if not player_c.is_alive():
            slow_print(f"\n  {C.RED}{_dname(player_c)} fainted!{C.RESET}")
            new_c = switch_creature(team, player_c, forced=True)
            if new_c:
                player_c = new_c
                boosts = {"atk": 1.0, "def": 1.0, "spatk": 1.0, "spdef": 1.0}
                player_c._xdef_boost   = 1.0
                player_c._xspdef_boost = 1.0
                player_c._xspd_boost   = 1.0
                for msg in fire_on_entry(player_c, enemy_c, weather):
                    slow_print(msg)
                slow_print(f"  {C.GREEN}{player_c.name} is sent out!{C.RESET}")
                press_enter()
                continue
            else:
                slow_print(f"  {C.RED}All your creatures fainted! You lose!{C.RESET}")
                summary.show(force=not wild)
                press_enter()
                return "lose", None
