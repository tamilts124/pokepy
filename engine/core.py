import random
import math
import json
import os

from data.creatures import CREATURES, MOVES, TYPE_CHART, ITEMS, WILD_AREAS

SAVE_FILE = "save.json"

# Shiny encounter probability (1 in 100)
SHINY_CHANCE = 1 / 100

# ─────────────────────────────────────────────
#  FRIENDSHIP / BOND SYSTEM
# ─────────────────────────────────────────────
BASE_FRIENDSHIP = 70    # starting bond value, like a fresh acquaintance
MAX_FRIENDSHIP  = 100   # fully bonded
BOND_THRESHOLD  = 100   # friendship needed to unlock the mechanical payoffs below
BOND_SAVE_CHANCE = 0.10  # 10% chance to survive a lethal hit at 1 HP once per battle


# ─────────────────────────────────────────────
#  NATURE SYSTEM
# ─────────────────────────────────────────────
# Each nature: (boosted_stat, lowered_stat) — None means neutral
# Stats: "atk", "def", "sp_atk", "sp_def", "spd"
NATURES = {
    "Hardy":    (None, None),
    "Lonely":   ("atk",    "def"),
    "Brave":    ("atk",    "spd"),
    "Adamant":  ("atk",    "sp_atk"),
    "Naughty":  ("atk",    "sp_def"),
    "Bold":     ("def",    "atk"),
    "Docile":   (None, None),
    "Relaxed":  ("def",    "spd"),
    "Impish":   ("def",    "sp_atk"),
    "Lax":      ("def",    "sp_def"),
    "Timid":    ("spd",    "atk"),
    "Hasty":    ("spd",    "def"),
    "Serious":  (None, None),
    "Jolly":    ("spd",    "sp_atk"),
    "Naive":    ("spd",    "sp_def"),
    "Modest":   ("sp_atk", "atk"),
    "Mild":     ("sp_atk", "def"),
    "Quiet":    ("sp_atk", "spd"),
    "Bashful":  (None, None),
    "Rash":     ("sp_atk", "sp_def"),
    "Calm":     ("sp_def", "atk"),
    "Gentle":   ("sp_def", "def"),
    "Sassy":    ("sp_def", "spd"),
    "Careful":  ("sp_def", "sp_atk"),
    "Quirky":   (None, None),
}
NATURE_NAMES = list(NATURES.keys())

def nature_mult(nature_name, stat):
    """Return the stat multiplier (1.1, 0.9, or 1.0) for a nature/stat combo."""
    boost, lower = NATURES.get(nature_name, (None, None))
    if boost == stat:
        return 1.1
    if lower == stat:
        return 0.9
    return 1.0

# ─────────────────────────────────────────────
#  CREATURE INSTANCE
# ─────────────────────────────────────────────
class Creature:
    def __init__(self, name, level, moves=None, is_player=True, nature=None):
        self.name      = name
        self.level     = level
        self.is_player = is_player
        data           = CREATURES[name]
        self.types     = data["type"]
        self.ability   = data.get("ability", None)   # passive ability
        self.nature    = nature if nature else random.choice(NATURE_NAMES)
        self.status    = None   # poison / burn / paralyzed / sleep / freeze / confuse / None
        # Sleep counter: how many turns the creature stays asleep (1-3)
        self.sleep_turns = 0
        # Confusion is tracked as a separate volatile flag (not saved like main status)
        # but we store it on status for simplicity; confusion_turns tracks duration
        self.confusion_turns = 0

        bs = data["base_stats"]   # [hp, atk, def, sp_atk, sp_def, spd]
        self.max_hp  = self._calc_hp(bs[0])
        self.hp      = self.max_hp
        self.atk     = self._calc_stat(bs[1], "atk")
        self.defense = self._calc_stat(bs[2], "def")
        self.sp_atk  = self._calc_stat(bs[3], "sp_atk")
        self.sp_def  = self._calc_stat(bs[4], "sp_def")
        self.spd     = self._calc_stat(bs[5], "spd")
        self.exp     = 0
        self.exp_to_next = self._exp_needed()

        # In-battle stat stages (-6 to +6), reset on switch/battle end
        self.stages = {"atk": 0, "def": 0, "spatk": 0, "spdef": 0, "spd": 0, "acc": 0}

        # Held item (None or item name string)
        self.held_item = None
        self._held_item_used = False   # one-use berry flag
        self._sturdy_used    = False   # Sturdy one-per-battle flag
        self.nickname  = None          # optional player-given nickname (≤10 chars)
        self.is_shiny  = False         # cosmetic shiny variant (rolled on wild spawn)
        self.friendship = BASE_FRIENDSHIP   # 0-100 bond stat; rises with care/wins
        self._bond_save_used = False   # one-per-battle flag for the maxed-bond survive proc


        # Moves: use learned set up to current level
        if moves:
            self.moves = moves
        else:
            learned = data["moves_learned"]
            self.moves = []
            for lv, mvs in sorted(learned.items()):
                if lv <= level:

                    for m in mvs:
                        if m not in self.moves:
                            self.moves.append(m)
            self.moves = self.moves[-4:]   # max 4

        # PP tracking
        self.pp = {m: MOVES[m]["pp"] for m in self.moves}

    # ── Stat formulae (simplified Gen-I style) ──
    def _calc_hp(self, base):
        return int((base * 2 * self.level) / 100) + self.level + 10

    def _calc_stat(self, base, stat_key=None):
        raw = int((base * 2 * self.level) / 100) + 5
        if stat_key:
            raw = int(raw * nature_mult(self.nature, stat_key))
        return max(1, raw)

    def _exp_needed(self):
        return int(self.level ** 3 * 0.8)

    # ── Stage multiplier (standard -6..+6 table) ──
    STAGE_MULT = {-6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
                   0: 1.0,
                   1: 3/2,  2: 4/2,  3: 5/2,  4: 6/2,  5: 7/2,  6: 8/2}

    def stage_mult(self, stat):
        return self.STAGE_MULT.get(self.stages.get(stat, 0), 1.0)

    def apply_stage(self, stat, delta):
        """Change a stat stage, clamped to [-6, +6]. Returns actual change."""
        old = self.stages.get(stat, 0)
        new = max(-6, min(6, old + delta))
        self.stages[stat] = new
        return new - old

    def effective_atk(self):
        return max(1, int(self.atk * self.stage_mult("atk")))

    def effective_def(self):
        return max(1, int(self.defense * self.stage_mult("def")))

    def effective_spatk(self):
        return max(1, int(self.sp_atk * self.stage_mult("spatk")))

    def effective_spdef(self):
        return max(1, int(self.sp_def * self.stage_mult("spdef")))

    def effective_spd(self, weather=None):
        spd = max(1, int(self.spd * self.stage_mult("spd")))
        # X Speed item boost (set via battle.py bag handler on use)
        xspd = getattr(self, '_xspd_boost', 1.0)
        if xspd != 1.0:
            spd = max(1, int(spd * xspd))
        if self.status == "paralyzed":
            spd = max(1, spd // 2)
        # Ability speed multiplier (Swift Swim, Speed Boost stages already in stages)
        if self.ability:
            try:
                from engine.battle import ability_speed_mult
                spd = max(1, int(spd * ability_speed_mult(self, weather)))
            except ImportError:
                pass
        return spd

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        # Sturdy: survive a OHKO from full HP
        if (self.ability == "Sturdy"
                and not getattr(self, '_sturdy_used', False)
                and self.hp == self.max_hp
                and dmg >= self.hp):
            self._sturdy_used = True
            self.hp = 1
            # Print Sturdy message — late import to avoid circular dep
            try:
                from ui.display import C, slow_print
                slow_print(f"  {C.YELLOW}{self.name} held on with Sturdy! (1 HP){C.RESET}")
            except Exception:
                pass
            return
        # Maxed bond: a fully-friended creature gets one chance per battle to
        # shrug off what would otherwise be a fatal hit and hang on at 1 HP.
        if (self.friendship >= BOND_THRESHOLD
                and not getattr(self, '_bond_save_used', False)
                and dmg >= self.hp
                and self.hp > 0):
            self._bond_save_used = True
            if random.random() < BOND_SAVE_CHANCE:
                self.hp = 1
                try:
                    from ui.display import C, slow_print
                    slow_print(f"  {C.MAGENTA}{self.name} refused to go down — your bond held strong! (1 HP){C.RESET}")
                except Exception:
                    pass
                return
        self.hp = max(0, self.hp - dmg)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_friendship(self, amount):
        """Raise this creature's bond, clamped to [0, MAX_FRIENDSHIP]. Returns actual delta."""
        old = self.friendship
        self.friendship = max(0, min(MAX_FRIENDSHIP, self.friendship + amount))
        return self.friendship - old

    def reset_stages(self):
        self.stages = {"atk": 0, "def": 0, "spatk": 0, "spdef": 0, "spd": 0, "acc": 0}
        # Confusion clears on switch
        if self.status == "confuse":
            self.status = None
            self.confusion_turns = 0
        self._sturdy_used = False   # Sturdy resets on switch
        self._bond_save_used = False   # bond-save proc resets on switch
    def gain_exp(self, amount):
        """Returns list of events: level-ups, new moves, evolutions."""
        events = []
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = self._exp_needed()
            # Recalc stats
            data = CREATURES[self.name]
            bs   = data["base_stats"]   # [hp, atk, def, sp_atk, sp_def, spd]
            old_hp = self.max_hp
            self.max_hp  = self._calc_hp(bs[0])
            self.hp     += (self.max_hp - old_hp)
            self.atk     = self._calc_stat(bs[1], "atk")
            self.defense = self._calc_stat(bs[2], "def")
            self.sp_atk  = self._calc_stat(bs[3], "sp_atk")
            self.sp_def  = self._calc_stat(bs[4], "sp_def")
            self.spd     = self._calc_stat(bs[5], "spd")
            events.append(("levelup", self.level))
            self.gain_friendship(1)   # leveling up deepens the bond a little
            # New moves?
            for lv, mvs in CREATURES[self.name]["moves_learned"].items():
                if lv == self.level:
                    for m in mvs:
                        if m not in self.moves:
                            if len(self.moves) < 4:
                                self.moves.append(m)
                                self.pp[m] = MOVES[m]["pp"]
                                events.append(("newmove", m))
                            else:
                                events.append(("movefull", m))
            # Evolution?
            evo = CREATURES[self.name]["evolution"]
            if self.level in evo:
                events.append(("evolution", evo[self.level]))
        return events

    def evolve(self, new_name):
        self.name  = new_name
        self.types = CREATURES[new_name]["type"]
        data = CREATURES[new_name]
        bs = data["base_stats"]   # [hp, atk, def, sp_atk, sp_def, spd]
        old_hp = self.max_hp
        self.max_hp  = self._calc_hp(bs[0])
        self.hp     += (self.max_hp - old_hp)
        self.atk     = self._calc_stat(bs[1], "atk")
        self.defense = self._calc_stat(bs[2], "def")
        self.sp_atk  = self._calc_stat(bs[3], "sp_atk")
        self.sp_def  = self._calc_stat(bs[4], "sp_def")
        self.spd     = self._calc_stat(bs[5], "spd")
        for lv, mvs in CREATURES[new_name]["moves_learned"].items():
            if lv <= self.level:
                for m in mvs:
                    if m not in self.moves:
                        self.moves.append(m)
                        self.pp[m] = MOVES[m]["pp"]
        self.moves = self.moves[-4:]

    def to_dict(self):
        return {
            "name":        self.name,
            "level":       self.level,
            "hp":          self.hp,
            "exp":         self.exp,
            "status":      self.status,
            "sleep_turns": self.sleep_turns,
            "moves":       self.moves,
            "pp":          self.pp,
            "held_item":   self.held_item,
            "nature":      self.nature,
            "nickname":    self.nickname,
            "is_shiny":    self.is_shiny,
            "friendship":  self.friendship,

        }


    @classmethod
    def from_dict(cls, d):
        c = cls(d["name"], d["level"], moves=d["moves"],
                nature=d.get("nature"))        # restore saved nature (or pick random if old save)
        c.exp          = d["exp"]
        c.status       = d.get("status")
        c.sleep_turns  = d.get("sleep_turns", 0)
        c.pp           = d.get("pp", {m: MOVES[m]["pp"] for m in c.moves})
        c.held_item    = d.get("held_item")
        # Always recalc stats from level (nature already applied in __init__)
        bs = CREATURES[c.name]["base_stats"]
        c.max_hp  = c._calc_hp(bs[0])
        c.hp      = min(d["hp"], c.max_hp)   # clamp saved HP to valid range
        c.atk     = c._calc_stat(bs[1], "atk")
        c.defense = c._calc_stat(bs[2], "def")
        c.sp_atk  = c._calc_stat(bs[3], "sp_atk")
        c.sp_def  = c._calc_stat(bs[4], "sp_def")
        c.spd     = c._calc_stat(bs[5], "spd")
        c._held_item_used = False   # always reset on load; re-triggers fresh each battle
        c.nickname    = d.get("nickname")       # None if old save (no nickname)
        c.is_shiny    = d.get("is_shiny", False)  # False for old saves
        c.friendship  = d.get("friendship", BASE_FRIENDSHIP)  # default bond for old saves
        return c



# ─────────────────────────────────────────────
#  WEATHER MODIFIER
# ─────────────────────────────────────────────
WEATHER_BOOST = {
    # weather: {type: multiplier}
    "Sunny":     {"fire": 1.5, "water": 0.5},
    "Rainy":     {"water": 1.5, "fire": 0.5},
    "Sandstorm": {},
    "Hail":      {"ice": 1.5},
}

WEATHER_IMMUNE = {
    # weather: types that take no end-of-turn damage
    "Sandstorm": {"rock", "ground", "steel"},
    "Hail":      {"ice"},
}

def weather_move_mult(weather, move_type):
    if not weather:
        return 1.0
    return WEATHER_BOOST.get(weather, {}).get(move_type, 1.0)

def apply_weather_damage(creature, weather):
    """Apply end-of-turn weather damage. Returns dmg dealt (0 if immune)."""
    if not weather:
        return 0
    immune_types = WEATHER_IMMUNE.get(weather, set())
    if any(t in immune_types for t in creature.types):
        return 0
    if weather in ("Sandstorm", "Hail"):
        dmg = max(1, creature.max_hp // 16)
        creature.take_damage(dmg)
        return dmg
    return 0


# ─────────────────────────────────────────────
#  DAMAGE CALCULATOR  (now uses stat stages + weather)
# ─────────────────────────────────────────────
def calc_damage(attacker, defender, move_name, weather=None):
    move = MOVES[move_name]
    if move["power"] == 0:
        return 0, 1.0, False

    # Physical vs Special split
    category = move.get("category", "physical")
    if category == "special":
        eff_atk = attacker.effective_spatk()
        eff_def = defender.effective_spdef()
    else:  # physical
        eff_atk = attacker.effective_atk()
        eff_def = defender.effective_def()

    # Type effectiveness
    effectiveness = 1.0
    for def_type in defender.types:
        chart = TYPE_CHART.get(move["type"], {})
        effectiveness *= chart.get(def_type, 1.0)

    # STAB
    stab = 1.5 if move["type"] in attacker.types else 1.0

    # Weather multiplier
    w_mult = weather_move_mult(weather, move["type"])

    # Ability multipliers + held-item crit bonus (late import to avoid circular dependency)
    try:
        from engine.battle import (ability_damage_dealt_mult, ability_damage_taken_mult,
                                    held_item_crit_bonus)
        dealt_mult = ability_damage_dealt_mult(attacker, move["type"], weather)
        taken_mult = ability_damage_taken_mult(defender, move["type"], move["power"], weather)
        crit_denom = 8 if held_item_crit_bonus(attacker) else 16
        if attacker.friendship >= BOND_THRESHOLD:
            crit_denom = max(4, crit_denom - 4)   # maxed bond shaves the crit roll further
    except ImportError:
        dealt_mult = 1.0
        taken_mult = 1.0
        crit_denom = 16

    # Critical hit (~6.25% chance → 1.5x damage; Scope Lens doubles it to ~12.5%)
    crit = 1.5 if random.randint(1, crit_denom) == 1 else 1.0

    # Random factor
    rand = random.uniform(0.85, 1.0)

    # Burn halves physical damage output only
    if attacker.status == "burn" and category == "physical":
        dealt_mult *= 0.5

    # X Defense / X Sp.Def item boost (passed via defender's _xdef_boost / _xspdef_boost attribute)
    if category == "special":
        xspdef = getattr(defender, '_xspdef_boost', 1.0)
        taken_mult /= xspdef
    else:
        xdef = getattr(defender, '_xdef_boost', 1.0)
        taken_mult /= xdef

    base = ((2 * attacker.level / 5 + 2) * move["power"] * eff_atk / max(1, eff_def)) / 50 + 2
    dmg  = int(base * stab * effectiveness * w_mult * crit * rand * dealt_mult * taken_mult)
    return max(1, dmg), effectiveness, crit > 1.0


# ─────────────────────────────────────────────
#  SAVE / LOAD  (multi-slot)
# ─────────────────────────────────────────────
def save_file_path(slot=1):
    return f"save_slot{slot}.json"

SAVE_VERSION = 2

def save_game(player_name, town, team, inventory, badges, money, steps=0, slot=1, rival=None, achievements=None, season=None, seen=None, caught=None, shiny_caught=None, is_champion=False, avatar="♂", visited_towns=None, play_seconds=0, nuzlocke=False, repel_steps=0, defeated_trainers=None, item_drought=0, last_played_date=None):
    data = {
        "version":     SAVE_VERSION,
        "player_name": player_name,
        "town":        town,

        "team":        [c.to_dict() for c in team],
        "inventory":   inventory,
        "badges":      badges,
        "money":       money,
        "steps":       steps,
        "play_seconds": play_seconds,
        "nuzlocke":    bool(nuzlocke),
        "repel_steps": repel_steps,
        "item_drought": item_drought,
        "defeated_trainers": sorted(defeated_trainers or []),
        "rival":       rival.to_dict() if rival is not None else None,
        "achievements": achievements or [],
        "season":      season or "Spring",
        "seen":        sorted(seen or []),
        "caught":      sorted(caught or []),
        "shiny_caught": sorted(shiny_caught or []),
        "is_champion": bool(is_champion),
        "avatar":      avatar or "♂",
        "visited_towns": sorted(visited_towns or []),
        "last_played_date": last_played_date or "",
    }
    with open(save_file_path(slot), "w") as f:
        json.dump(data, f, indent=2)

def load_game(slot=1):
    path = save_file_path(slot)
    # Legacy fallback for old single save file
    if not os.path.exists(path) and slot == 1 and os.path.exists("save.json"):

        path = "save.json"
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    # Migrate old saves (no version key)
    if "version" not in data:
        data["version"] = 1
        data.setdefault("achievements", [])
        data.setdefault("season", "Spring")
    data.setdefault("seen", [])
    data.setdefault("caught", [])
    data.setdefault("shiny_caught", [])
    data.setdefault("is_champion", False)
    data.setdefault("avatar", "♂")
    data.setdefault("visited_towns", [])
    data.setdefault("play_seconds", 0)
    data.setdefault("nuzlocke", False)
    data.setdefault("repel_steps", 0)
    data.setdefault("item_drought", 0)
    data.setdefault("defeated_trainers", [])
    data.setdefault("last_played_date", "")
    data["team"] = [Creature.from_dict(d) for d in data["team"]]
    return data

def list_save_slots():
    """Return list of (slot, summary_str) for all existing saves."""
    slots = []
    # Also check legacy save.json → treat as slot 1 if slot1 doesn't exist
    for slot in range(1, 4):
        path = save_file_path(slot)
        if not os.path.exists(path) and slot == 1 and os.path.exists("save.json"):
            path = "save.json"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    d = json.load(f)
                summary = (f"{d['player_name']} — {d['town']}  "
                           f"₽{d['money']}  badges:{len(d['badges'])}")
                slots.append((slot, summary))
            except Exception:
                pass
    return slots



# ─────────────────────────────────────────────
#  WILD ENCOUNTER HELPER
# ─────────────────────────────────────────────
PITY_THRESHOLD = 8   # dry encounters before boost kicks in
PITY_MULT_PER_TIER = 0.5  # +50% effective chance per tier beyond threshold

def roll_held_item(name, pity_boost=1.0):
    """Roll a held item for a wild creature of the given species.

    pity_boost > 1.0 increases each item's raw chance multiplicatively — purely
    a luck-smoothing measure after many consecutive item-less encounters.
    The pool is still iterated in order; the first hit wins.
    Returns an item name, or None if nothing hits.
    """
    pool_data = CREATURES[name].get("held_item_pool", [])
    for item_name, chance in pool_data:
        if random.random() < min(1.0, chance * pity_boost):
            return item_name
    return None


def random_wild(area_name, badge_bonus=0):
    pool = WILD_AREAS.get(area_name, [])
    if not pool:
        return None
    name, lo, hi = random.choice(pool)
    level = random.randint(lo + badge_bonus, hi + badge_bonus)
    wild = Creature(name, level, is_player=False)
    # Roll for a held item from this creature's pool
    wild.held_item = roll_held_item(name)
    return wild


# ─────────────────────────────────────────────
#  CAPTURE FORMULA
# ─────────────────────────────────────────────
# A well-bonded lead creature calms wild creatures down a little before a throw —
# small and capped so it nudges odds without replacing the Ultra/Master Ball progression.
FRIENDSHIP_CAPTURE_THRESHOLD = 80    # lead's friendship must be at least this high to matter
FRIENDSHIP_CAPTURE_MAX_BONUS = 0.10  # +10% effective ball rate at friendship 100

def friendship_capture_bonus(lead):
    """Effective ball-rate multiplier from the active lead creature's bond (1.0-1.10)."""
    if lead is None:
        return 1.0
    friendship = getattr(lead, "friendship", 0)
    if friendship < FRIENDSHIP_CAPTURE_THRESHOLD:
        return 1.0
    span = MAX_FRIENDSHIP - FRIENDSHIP_CAPTURE_THRESHOLD
    frac = (friendship - FRIENDSHIP_CAPTURE_THRESHOLD) / span
    return 1.0 + FRIENDSHIP_CAPTURE_MAX_BONUS * frac

def try_capture(wild, ball_rate, lead=None):
    cr   = CREATURES[wild.name]["catch_rate"]
    ball_rate = ball_rate * friendship_capture_bonus(lead)
    a    = ((3 * wild.max_hp - 2 * wild.hp) * cr * ball_rate) / (3 * wild.max_hp)
    a    = max(1, int(a))
    b    = 1048560 / math.sqrt(math.sqrt(16711680 / a))
    shakes = 0
    for _ in range(4):
        if random.randint(0, 65535) < b:
            shakes += 1
        else:
            break
    return shakes == 4, shakes
