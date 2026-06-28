import random
import sys
import os
import time

# ── Force UTF-8 stdout/stderr ──────────────────────────────
# Windows consoles often default to a legacy codepage (cp1252) that can't
# encode the box-drawing characters / emoji used throughout the UI, which
# crashes the game on the very first print before the player sees a menu.
# Reconfigure to UTF-8 with a safe fallback so the game never crashes on
# encoding alone, even on an un-configured cmd.exe.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from engine.core    import (Creature, save_game, load_game, list_save_slots, random_wild)
from data.creatures import (CREATURES, ITEMS, TOWNS, WILD_AREAS,
                             ELITE_FOUR, REQUIRED_BADGES, RANDOM_TRAINERS,
                             FISH_OLD_ROD, FISH_GOOD_ROD, GROTTOS,
                             SEASONAL_WILDS, SEASONAL_BERRY)
from engine.battle  import run_battle, HELD_ITEMS
from engine.rival   import (RivalState, trigger_rival_if_due,
                             trigger_post_elite_rival, COUNTER_STARTER)
from ui.display     import (C, clear, slow_print, banner, section,
                             hp_bar, creature_card, team_summary,
                             menu, confirm, pause, press_enter,
                             show_world_map)

SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
SEASON_COLORS = {"Spring": C.GREEN, "Summer": C.YELLOW, "Autumn": C.RED, "Winter": C.CYAN}
SEASON_ICONS  = {"Spring": "🌸", "Summer": "☀", "Autumn": "🍂", "Winter": "❄"}

def current_season():
    """Season cycles every 7 days, based on week number."""
    week = time.localtime().tm_yday // 7
    return SEASONS[week % 4]


# ── Achievement definitions ────────────────────────────────
ACHIEVEMENTS = {
    "first_catch":     {"name": "First Catch!",        "desc": "Catch your first wild creature."},
    "first_badge":     {"name": "Badge Earned",         "desc": "Win your first gym badge."},
    "all_badges":      {"name": "Badge Master",         "desc": "Collect all 7 badges."},
    "champion":        {"name": "Champion!",            "desc": "Defeat the Elite Four."},
    "first_evolution": {"name": "Evolution!",           "desc": "Evolve a creature for the first time."},
    "team_full":       {"name": "Full House",           "desc": "Fill your team with 6 creatures."},
    "rich":            {"name": "Money Bags",           "desc": "Accumulate ₽10,000 at once."},
    "first_fish":      {"name": "Gone Fishin'",         "desc": "Catch your first fishing encounter."},
    "grotto_found":    {"name": "Grotto Explorer",      "desc": "Discover a hidden grotto."},
    "rival_winner":    {"name": "Rival Rivalry",        "desc": "Defeat your rival 3 times."},
    "battle100":       {"name": "Veteran Trainer",      "desc": "Fight 100 battles."},
    "pokedex_complete": {"name": "Dex Master",           "desc": "Catch every creature in the Pokédex."},
}

# ── Move Tutor data ──────────────────────────────────────
WEATHER_POOL = [None, None, None, "Sunny", "Rainy", "Sandstorm", "Hail"]
SEASON_WEATHER = {
    "Spring": [None, None, "Rainy", "Rainy", "Sunny"],
    "Summer": [None, "Sunny", "Sunny", "Sunny", "Sandstorm"],
    "Autumn": [None, None, "Sandstorm", "Rainy", "Sunny"],
    "Winter": [None, "Hail", "Hail", "Rainy", None],
}

MOVE_TUTORS = {
    "Stonepeak":   [("Headbutt", 500),  ("Rock Throw", 400), ("Howl", 300)],
    "Ashveil":     [("Fire Blast", 1500), ("Lava Plume", 1200), ("Swords Dance", 1000)],
    "Frostholm":   [("Blizzard", 1500),  ("Ice Beam", 1200), ("Agility", 1000)],
    "Mistveil":    [("Psychic", 1200),   ("Shadow Ball", 1000), ("Agility", 1000)],
    "Shadowmere":  [("Night Slash", 800), ("Crunch", 900), ("Swords Dance", 1000)],
    "Dragonspire": [("Dragon Rage", 2000), ("Earthquake", 2500), ("Swords Dance", 1500)],
}

# ── Random trainer identities ────────────────────────────
# Each title pairs with a small fixed pool of first names, so a random encounter
# resolves to a stable identity (e.g. "Hiker Earl") instead of an anonymous title.
# Combined with Game._defeated_trainers, this lets repeat encounters with the same
# named trainer in the same area read as a rematch rather than a fresh reskin.
RANDOM_TRAINER_NAMES = {
    "Youngster":   ["Joey", "Timmy"],
    "Lass":        ["Mia", "Nora"],
    "Hiker":       ["Earl", "Rocco"],
    "Sailor":      ["Skip", "Mango"],
    "Ranger":      ["Forrest", "Wren"],
    "Ace Trainer": ["Vance", "Sable"],
}

# ── Town revisit flavor lines ────────────────────────────
# Each town has two lines: one shown after beating its gym, one for non-gym revisits.
# Format: (gym_beaten_quote, general_revisit_quote)
TOWN_REVISIT_QUOTES = {
    "Rootvale":     (None,
                     "The tall grass sways like it's waving you home."),
    "Mudfen":       (None,
                     "The swamp smells just as bad as you remember."),
    "Greenpath":    ("Fern's gym is quieter now. The leaves remember your victory.",
                     "The forest air feels cleaner every time you visit."),
    "Stonepeak":    ("Granite's badge glints in your pocket like a trophy.",
                     "The mountain wind is as sharp and cold as ever."),
    "Ashveil":      ("The ash still falls, but Cinder's fire has cooled for you.",
                     "Warm cinders drift lazily through the volcanic air."),
    "Frostholm":    ("Blizara's gym stands silent. You broke her cold streak.",
                     "Your breath fogs in the air. Nothing thaws here."),
    "Mistveil":     ("Myra said the mist foresees your future. It looks bright.",
                     "The purple mist curls around you like it knows your name."),
    "Shadowmere":   ("Umbra's Shadow Badge — proof the darkness couldn't hold you.",
                     "Shadows shift at the corner of your eye. Old habits."),
    "Dragonspire":  ("Draven nods at you now. One dragon to another.",
                     "The great skeleton looms overhead, ancient and silent."),
    "Champion Road": ("You've walked this road before and come out on top.",
                      "The air here hums with history. Yours included."),
}

# ── Day/Night cycle ──────────────────────────────────────
def time_of_day():
    h = time.localtime().tm_hour
    if 6 <= h < 12:
        return "Morning", C.YELLOW, "🌅"
    elif 12 <= h < 18:
        return "Afternoon", C.CYAN, "☀"
    elif 18 <= h < 21:
        return "Evening", C.MAGENTA, "🌆"
    else:
        return "Night", C.BLUE, "🌙"

def night_bonus_areas():
    """At night, ghost-types appear more and certain areas get bonus creatures."""
    h = time.localtime().tm_hour
    return h >= 21 or h < 6


# ═══════════════════════════════════════════════
#  GAME STATE
# ═══════════════════════════════════════════════
class Game:
    def __init__(self):
        self.player_name = ""
        self.town        = "Rootvale"
        self.team        = []
        self.inventory   = {k: 0 for k in ITEMS}
        self.inventory["Potion"]       = 3
        self.inventory["Capture Ball"] = 5
        self.inventory["Old Rod"]      = 1   # Start with fishing rod
        self.inventory["Rare Candy"]   = 0
        self.badges      = []
        self.money       = 3000
        self.steps       = 0
        self.play_seconds = 0            # accumulated playtime in seconds
        self._session_start = time.time() # start of current session
        self.save_slot   = 1
        self.rival       = RivalState()
        self.achievements = []           # list of earned achievement keys
        self.season      = current_season()
        self.repel_steps = 0             # remaining wild-encounter charges from a Repel item
        self._defeated_trainers = set()  # track rematched trainers by (area, name_hash)
        self.seen        = set()         # creature names encountered in the wild
        self.caught      = set()         # creature names successfully captured
        self.is_champion = False         # True once the Elite Four has been beaten at least once
        self.avatar      = "♂"          # trainer avatar symbol chosen at character creation
        self.visited_towns = set()       # towns the player has entered at least once
        self.nuzlocke    = False         # if True, fainted creatures are permanently deleted

    # ── Achievement checker ────────────────────────────
    def _check_achievement(self, key):
        if key not in self.achievements and key in ACHIEVEMENTS:
            self.achievements.append(key)
            ach = ACHIEVEMENTS[key]
            slow_print(f"  {C.YELLOW}🏆  Achievement unlocked: {C.BOLD}{ach['name']}{C.RESET}")
            slow_print(f"     {C.GRAY}{ach['desc']}{C.RESET}")

    def _check_pokedex_completion(self):
        """Fire the pokedex_complete achievement + reward when all creatures caught."""
        total = len(CREATURES)
        if len(self.caught) >= total and "pokedex_complete" not in self.achievements:
            self._check_achievement("pokedex_complete")
            # Reward: a free Master Ball
            self.inventory["Master Ball"] = self.inventory.get("Master Ball", 0) + 1
            slow_print(f"  {C.MAGENTA}★★  You've caught all {total} creatures!  ★★{C.RESET}")
            slow_print(f"  {C.YELLOW}As a reward, you receive a {C.BOLD}Master Ball{C.RESET}{C.YELLOW}!{C.RESET}")

    # ── Pokédex ────────────────────────────────────────
    def open_pokedex(self):
        from data.creatures import CREATURES as CDEX
        all_names = sorted(CDEX.keys())
        total     = len(all_names)

        # Paged listing (20 per page)
        PAGE = 20
        page = 0
        max_page = (total - 1) // PAGE

        while True:
            seen_cnt   = len(self.seen)
            caught_cnt = len(self.caught)
            clear()
            section("📖  POKÉDEX")
            print(f"  Seen {C.CYAN}{seen_cnt}/{total}{C.RESET}  │  "
                  f"Caught {C.GREEN}{caught_cnt}/{total}{C.RESET}  │  "
                  f"Page {page+1}/{max_page+1}\n")

            pct = int((caught_cnt / total) * 20) if total else 0
            bar = "█" * pct + "░" * (20 - pct)
            print(f"  Progress  {C.GREEN}[{bar}]{C.RESET} {int(caught_cnt/total*100) if total else 0}%\n")

            start = page * PAGE
            chunk = all_names[start:start + PAGE]

            entry_opts = []
            for name in chunk:
                if name in self.caught:
                    data = CDEX[name]
                    types_str = "/".join(t.upper() for t in data["type"])
                    entry_opts.append(f"{C.GREEN}●{C.RESET} {C.BOLD}{name:<14}{C.RESET}  "
                                       f"{C.GRAY}[{types_str}]{C.RESET}")
                elif name in self.seen:
                    entry_opts.append(f"{C.YELLOW}◐{C.RESET} {name:<14}  {C.GRAY}(seen){C.RESET}")
                else:
                    entry_opts.append(f"{C.GRAY}○ {'???':<14}  ???{C.RESET}")

            nav = []
            if page > 0:         nav.append("◀  Prev page")
            if page < max_page:  nav.append("▶  Next page")
            nav.append("← Back")

            choice = menu("", entry_opts + nav)
            if choice < len(entry_opts):
                selected = chunk[choice]
                if selected in self.seen or selected in self.caught:
                    self._show_pokedex_entry(selected)
                # Unseen entries (???) just do nothing — nothing to show yet.
                continue
            label = nav[choice - len(entry_opts)]
            if label == "◀  Prev page":
                page -= 1
            elif label == "▶  Next page":
                page += 1
            else:
                return

    def _show_pokedex_entry(self, name):
        """Detail view for a single Pokédex entry — types, base stats, ability, evolution line."""
        from data.creatures import CREATURES as CDEX
        data = CDEX[name]
        caught = name in self.caught

        clear()
        section(f"📖  #{name}")
        types_str = "/".join(t.upper() for t in data["type"])
        slow_print(f"  {C.BOLD}{name}{C.RESET}  {C.GRAY}[{types_str}]{C.RESET}")
        if caught:
            slow_print(f"  {C.GREEN}● Caught{C.RESET}")
        else:
            slow_print(f"  {C.YELLOW}◐ Seen, not yet caught{C.RESET}")
        slow_print(f"  {C.GRAY}{data.get('desc', '')}{C.RESET}\n")

        if caught:
            # Full info once the player actually owns one.
            bs = data["base_stats"]
            stat_names = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
            print(f"  {C.CYAN}Base Stats{C.RESET}")
            for sname, val in zip(stat_names, bs):
                filled = int((val / 150) * 20)
                bar = "▪" * max(0, min(20, filled)) + "·" * (20 - max(0, min(20, filled)))
                print(f"  {sname:<8} {val:>4}  {C.GREEN}{bar}{C.RESET}")
            print()
            slow_print(f"  {C.CYAN}Ability:{C.RESET} {data.get('ability', 'None')}")

            evo = data.get("evolution")
            if evo:
                evo_lv, evo_name = next(iter(evo.items()))
                slow_print(f"  {C.CYAN}Evolves:{C.RESET} → {evo_name} at Lv.{evo_lv}")
            else:
                slow_print(f"  {C.CYAN}Evolves:{C.RESET} (final form)")
            stone_evo = data.get("stone_evolution")
            if stone_evo:
                for stone, evo_name in stone_evo.items():
                    slow_print(f"  {C.CYAN}Or:{C.RESET} use a {stone} → {evo_name}")
        else:
            slow_print(f"  {C.GRAY}Catch one to reveal base stats, ability, and evolution data.{C.RESET}")

        print()
        press_enter()

    # ── EXP & level-up handler (shared helper) ──────────
    def _handle_exp_events(self, creature, events):
        """Process levelup/newmove/movefull/evolution events. Returns True if evolved."""
        from data.creatures import MOVES as MOVE_DATA
        evolved = False
        for etype, val in events:
            if etype == "levelup":
                slow_print(f"  {C.GREEN}★  {creature.name} grew to Lv.{val}!{C.RESET}")
                print('\a', end='', flush=True)
            elif etype == "newmove":
                slow_print(f"  {C.CYAN}❆  {creature.name} learned {val}!{C.RESET}")
            elif etype == "movefull":

                new_move = val
                mv = MOVE_DATA[new_move]
                slow_print(f"\n  {C.YELLOW}★  {creature.name} wants to learn "
                           f"{C.BOLD}{new_move}{C.RESET}"
                           f"{C.YELLOW}!{C.RESET}")
                slow_print(f"     {C.GRAY}[{mv['type']}]  Pwr:{mv['power']}  "
                           f"PP:{mv['pp']}  {mv.get('desc','')}{C.RESET}")
                slow_print(f"  {C.RED}But {creature.name} already knows 4 moves!{C.RESET}")
                print()
                r_opts = []
                for m in creature.moves:
                    mm = MOVE_DATA[m]
                    r_opts.append(f"Replace {C.BOLD}{m}{C.RESET}  "
                                  f"{C.GRAY}[{mm['type']}] Pwr:{mm['power']} "
                                  f"PP:{creature.pp.get(m,0)}/{mm['pp']}  {mm.get('desc','')}{C.RESET}")
                r_opts.append(f"Don't learn {new_move}")
                rc = menu(f"Which move to replace with {new_move}?", r_opts)
                if rc < len(creature.moves):
                    old_move = creature.moves[rc]
                    creature.moves[rc] = new_move
                    del creature.pp[old_move]
                    creature.pp[new_move] = mv["pp"]
                    slow_print(f"  {C.GREEN}{creature.name} forgot {old_move} "
                               f"and learned {new_move}!{C.RESET}")
                else:
                    slow_print(f"  {C.GRAY}{creature.name} did not learn {new_move}.{C.RESET}")
            elif etype == "evolution":
                slow_print(f"\n  {C.MAGENTA}❆❆  {creature.name} is evolving…  ❆❆{C.RESET}")
                time.sleep(0.8)
                if confirm(f"  Evolve {creature.name} into {val}?"):
                    old = creature.name
                    creature.evolve(val)
                    slow_print(f"  {C.MAGENTA}❆  {old} evolved into "
                               f"{C.BOLD}{val}{C.RESET}{C.MAGENTA}!  ❆{C.RESET}")
                    print('\a', end='', flush=True)
                    self._check_achievement("first_evolution")
                    evolved = True
        return evolved

    # ── EXP & level-up handler ──────────────────
    def _nuzlocke_purge(self):
        """In Nuzlocke mode: permanently remove all fainted creatures from the team."""
        if not getattr(self, 'nuzlocke', False):
            return
        dead = [c for c in self.team if not c.is_alive()]
        if not dead:
            return
        for c in dead:
            nick = getattr(c, 'nickname', None)
            dname = f"{nick} ({c.name})" if nick else c.name
            print()
            slow_print(f"  {C.RED}{'━'*44}{C.RESET}")
            slow_print(f"  {C.RED}  ✝  {C.BOLD}{dname}{C.RESET}{C.RED} has fallen.{C.RESET}")
            slow_print(f"  {C.RED}     This is Nuzlocke. There is no coming back.{C.RESET}")
            slow_print(f"  {C.RED}{'━'*44}{C.RESET}")
            self.team.remove(c)
        if not self.team:
            print()
            slow_print(f"  {C.RED}{C.BOLD}Your last creature has fallen.{C.RESET}")
            slow_print(f"  {C.RED}Your adventure ends here.{C.RESET}")
            press_enter()
            sys.exit(0)

    def award_exp(self, winner, loser):
        from data.creatures import MOVES as MOVE_DATA
        base = loser.level * 5
        exp  = int(base * (1 + random.uniform(-0.1, 0.1)))

        # Shared EXP: all alive bench creatures get a reduced split
        bench = [c for c in self.team if c.is_alive() and c is not winner]
        if bench:
            bench_exp = max(1, exp // 2)
            for bc in bench:
                slow_print(f"  {bc.name} gained {C.GRAY}{bench_exp} EXP (shared){C.RESET}!")
                b_events = bc.gain_exp(bench_exp)
                for etype, val in b_events:
                    if etype == "levelup":
                        slow_print(f"  {C.GREEN}★  {bc.name} grew to Lv.{val}!{C.RESET}")
                    elif etype == "newmove":
                        slow_print(f"  {C.CYAN}✦  {bc.name} learned {val}!{C.RESET}")
                    elif etype == "movefull":
                        new_move = val
                        mv = MOVE_DATA[new_move]
                        slow_print(f"\n  {C.YELLOW}★  {bc.name} wants to learn "
                                   f"{C.BOLD}{new_move}{C.RESET}"
                                   f"{C.YELLOW}!{C.RESET}")
                        slow_print(f"     {C.GRAY}[{mv['type']}]  Pwr:{mv['power']}  "
                                   f"PP:{mv['pp']}{C.RESET}")
                        slow_print(f"  {C.RED}But {bc.name} already knows 4 moves!{C.RESET}")
                        print()
                        r_opts = []
                        for m in bc.moves:
                            mm = MOVE_DATA[m]
                            r_opts.append(f"Replace {C.BOLD}{m}{C.RESET}  "
                                          f"{C.GRAY}[{mm['type']}] Pwr:{mm['power']} "
                                          f"PP:{bc.pp.get(m,0)}/{mm['pp']}{C.RESET}")
                        r_opts.append(f"Don't learn {new_move}")
                        rc = menu(f"Which move to replace with {new_move}?", r_opts)
                        if rc < len(bc.moves):
                            old_move = bc.moves[rc]
                            bc.moves[rc] = new_move
                            del bc.pp[old_move]
                            bc.pp[new_move] = mv["pp"]
                            slow_print(f"  {C.GREEN}{bc.name} forgot {old_move} "
                                       f"and learned {new_move}!{C.RESET}")
                        else:
                            slow_print(f"  {C.GRAY}{bc.name} did not learn {new_move}.{C.RESET}")
                    elif etype == "evolution":
                        slow_print(f"  {C.MAGENTA}✦✦  {bc.name} is evolving...{C.RESET}")
                        import time as _time; _time.sleep(0.5)
                        if confirm(f"  Evolve {bc.name} into {val}?"):
                            old = bc.name
                            bc.evolve(val)
                            slow_print(f"  {C.MAGENTA}✦  {old} evolved into {C.BOLD}{val}{C.RESET}{C.MAGENTA}!{C.RESET}")
                            print('\a', end='', flush=True)

        slow_print(f"\n  {winner.name} gained {C.YELLOW}{exp} EXP{C.RESET}!")
        events = winner.gain_exp(exp)
        for etype, val in events:
            if etype == "levelup":
                slow_print(f"  {C.GREEN}★  {winner.name} grew to Lv.{val}!{C.RESET}")
                print('\a', end='', flush=True)
            elif etype == "newmove":
                slow_print(f"  {C.CYAN}✦  {winner.name} learned {val}!{C.RESET}")
            elif etype == "movefull":
                new_move = val
                mv = MOVE_DATA[new_move]
                slow_print(f"\n  {C.YELLOW}★  {winner.name} wants to learn "
                           f"{C.BOLD}{new_move}{C.RESET}"
                           f"{C.YELLOW}!{C.RESET}")
                slow_print(f"     {C.GRAY}[{mv['type']}]  Pwr:{mv['power']}  "
                           f"PP:{mv['pp']}  {mv.get('desc','')}{C.RESET}")
                slow_print(f"  {C.RED}But {winner.name} already knows 4 moves!{C.RESET}")
                print()
                opts = []
                for m in winner.moves:
                    mm = MOVE_DATA[m]
                    opts.append(f"Replace {C.BOLD}{m}{C.RESET}  "
                                f"{C.GRAY}[{mm['type']}] Pwr:{mm['power']} "
                                f"PP:{winner.pp.get(m,0)}/{mm['pp']}  {mm.get('desc','')}{C.RESET}")
                opts.append(f"Don't learn {new_move}")
                choice = menu(f"Which move to replace with {new_move}?", opts)
                if choice < len(winner.moves):
                    old_move = winner.moves[choice]
                    winner.moves[choice] = new_move
                    del winner.pp[old_move]
                    winner.pp[new_move] = mv["pp"]
                    slow_print(f"  {C.GREEN}{winner.name} forgot {old_move} "
                               f"and learned {new_move}!{C.RESET}")
                else:
                    slow_print(f"  {C.GRAY}{winner.name} did not learn {new_move}.{C.RESET}")
            elif etype == "evolution":
                slow_print(f"\n  {C.MAGENTA}✦✦  {winner.name} is evolving...  ✦✦{C.RESET}")
                time.sleep(0.8)
                if confirm(f"  Evolve {winner.name} into {val}?"):
                    old = winner.name
                    winner.evolve(val)
                    slow_print(f"  {C.MAGENTA}✦  {old} evolved into "
                               f"{C.BOLD}{val}{C.RESET}{C.MAGENTA}!  ✦{C.RESET}")
                    print('\a', end='', flush=True)
        press_enter()
        self._nuzlocke_purge()

    def earn_money(self, amount):
        self.money += amount
        slow_print(f"  {C.YELLOW}You earned ₽{amount}!{C.RESET}")
        if self.money >= 10000:
            self._check_achievement("rich")

    def _count_battle(self):
        """Increment battle counter and fire battle100 achievement if threshold hit."""
        self.steps += 1
        if self.steps == 100:
            self._check_achievement("battle100")


    def save(self):
        # Accumulate current session time, then reset session start
        self.play_seconds += int(time.time() - self._session_start)
        self._session_start = time.time()
        save_game(self.player_name, self.town, self.team,
                  self.inventory, self.badges, self.money,
                  self.steps, slot=self.save_slot,
                  rival=getattr(self, 'rival', None),
                  achievements=getattr(self, 'achievements', []),
                  season=getattr(self, 'season', 'Spring'),
                  seen=getattr(self, 'seen', set()),
                  caught=getattr(self, 'caught', set()),
                  is_champion=getattr(self, 'is_champion', False),
                  avatar=getattr(self, 'avatar', '♂'),
                  visited_towns=getattr(self, 'visited_towns', set()),
                  play_seconds=self.play_seconds,
                  nuzlocke=getattr(self, 'nuzlocke', False),
                  repel_steps=getattr(self, 'repel_steps', 0),
                  defeated_trainers=getattr(self, '_defeated_trainers', set()))
        slow_print(f"  {C.GREEN}Game saved to slot {self.save_slot}!{C.RESET}")


    # ── INN ────────────────────────────────────
    def visit_inn(self, cost):
        from data.creatures import MOVES as MOVE_DATA
        clear()
        section(f"🏨  INN  —  {C.YELLOW}₽{cost}{C.RESET} to heal all creatures")

        # ── Heal-preview table ─────────────────────────────────────────────
        print(f"  {'Creature':<16} {'HP':>12}   {'PP':>8}  {'Status'}")
        print(f"  {'─'*16} {'─'*12}   {'─'*8}  {'─'*8}")
        anything_to_heal = False
        for c in self.team:
            hp_gain  = c.max_hp - c.hp
            pp_short = any(c.pp.get(m, 0) < MOVE_DATA[m]["pp"] for m in c.moves)
            has_status = bool(c.status)
            if hp_gain > 0 or pp_short or has_status:
                anything_to_heal = True

            hp_str = f"{c.hp}/{c.max_hp}"
            if hp_gain > 0:
                hp_str += f"  {C.GREEN}+{hp_gain}{C.RESET}"
            else:
                hp_str = f"{C.GRAY}{hp_str} (full){C.RESET}"

            pp_str = f"{C.GREEN}restore{C.RESET}" if pp_short else f"{C.GRAY}full{C.RESET}"
            st_str = f"{C.RED}{c.status}{C.RESET}" if c.status else f"{C.GRAY}—{C.RESET}"

            nick = getattr(c, 'nickname', None)
            dname = f"{nick} ({c.name})" if nick else c.name
            print(f"  {dname:<16} {hp_str:>12}   {pp_str:>8}  {st_str}")

        print()
        if not anything_to_heal:
            slow_print(f"  {C.GRAY}Your team is already at full health and PP!{C.RESET}")
            if not confirm(f"\n  Pay ₽{cost} anyway?"):
                return
        else:
            if not confirm(f"\n  Pay ₽{cost} to fully heal your team?"):
                return

        if self.money < cost:
            slow_print(f"  {C.RED}Not enough money! Need ₽{cost}.{C.RESET}")
            press_enter(); return
        self.money -= cost
        for c in self.team:
            c.hp     = c.max_hp
            c.status = None
            c.pp     = {m: MOVE_DATA[m]["pp"] for m in c.moves}
        slow_print(f"  {C.GREEN}Your team is fully healed! Rest well, trainer.{C.RESET}")
        press_enter()

    # ── BAG ────────────────────────────────────
    def open_bag(self):
        from data.creatures import MOVES as MOVE_DATA
        while True:
            clear()
            section("🎒  BAG")
            have = {k: v for k, v in self.inventory.items() if v > 0}
            if not have:
                slow_print("  Your bag is empty.")
                press_enter(); return

            opts = [f"{k} x{v}  {C.GRAY}({ITEMS[k]['desc']}){C.RESET}"
                    for k, v in have.items()]
            opts.append("← Close Bag")
            choice = menu("Items:", opts)
            if choice == len(have):
                return

            item_name = list(have.keys())[choice]
            idata     = ITEMS[item_name]

            if idata["type"] == "heal":
                need_heal = [c for c in self.team if c.is_alive() and c.hp < c.max_hp]
                if not need_heal:
                    slow_print("  No creature needs healing.")
                    press_enter(); continue
                t_opts = [f"{c.name} Lv.{c.level} {hp_bar(c.hp, c.max_hp, 12)}"
                          for c in need_heal] + ["← Back"]
                tc = menu("Heal which?", t_opts)
                if tc == len(need_heal): continue
                target = need_heal[tc]
                healed = min(idata["amount"], target.max_hp - target.hp)
                target.heal(idata["amount"])
                if idata.get("amount", 0) >= 9999:
                    target.status = None
                self.inventory[item_name] -= 1
                slow_print(f"  {C.GREEN}{target.name} recovered {healed} HP!{C.RESET}")
                press_enter()

            elif idata["type"] == "revive":
                fainted = [c for c in self.team if not c.is_alive()]
                if not fainted:
                    slow_print("  No fainted creatures."); press_enter(); continue
                t_opts = [f"{c.name} Lv.{c.level}" for c in fainted] + ["← Back"]
                tc = menu("Revive which?", t_opts)
                if tc == len(fainted): continue
                target = fainted[tc]
                target.hp = int(target.max_hp * idata["amount"])
                self.inventory[item_name] -= 1
                slow_print(f"  {C.GREEN}{target.name} was revived with "
                           f"{target.hp} HP!{C.RESET}")
                press_enter()

            elif idata["type"] == "cure":
                status_filter = idata["status"]
                if status_filter == "all":
                    sick = [c for c in self.team if c.status]
                else:
                    sick = [c for c in self.team if c.status == status_filter]
                if not sick:
                    slow_print("  No creature has that status."); press_enter(); continue
                t_opts = [f"{c.name} [{c.status}]" for c in sick] + ["← Back"]
                tc = menu("Cure which?", t_opts)
                if tc == len(sick): continue
                sick[tc].status = None
                self.inventory[item_name] -= 1
                slow_print(f"  {C.GREEN}Cured!{C.RESET}")
                press_enter()

            elif idata["type"] == "pp":
                alive = [c for c in self.team if c.is_alive()]
                if not alive:
                    slow_print("  No alive creatures."); press_enter(); continue
                t_opts = [f"{c.name} Lv.{c.level}" for c in alive] + ["← Back"]
                tc = menu("Restore PP for which?", t_opts)
                if tc == len(alive): continue
                target = alive[tc]
                for m in target.moves:
                    max_pp = MOVE_DATA[m]["pp"]
                    target.pp[m] = min(max_pp, target.pp.get(m, 0) + idata["amount"])
                self.inventory[item_name] -= 1
                slow_print(f"  {C.GREEN}{target.name}'s PP restored!{C.RESET}")
                press_enter()

            elif idata["type"] == "repel":
                already_active = self.repel_steps > 0
                self.repel_steps += idata["charges"]
                self.inventory[item_name] -= 1
                if already_active:
                    slow_print(f"  {C.CYAN}🛡  You used another {item_name}! Effect extended — "
                               f"now wards off wild creatures for {self.repel_steps} more "
                               f"encounters.{C.RESET}")
                else:
                    slow_print(f"  {C.CYAN}🛡  You used a {item_name}! Wild creatures will avoid "
                               f"you for the next {self.repel_steps} encounters while exploring.{C.RESET}")
                press_enter()

            elif idata["type"] in ("capture", "escape", "boost"):
                slow_print("  Use this during a battle or exploration.")
                press_enter()

    # ── HELD ITEM ASSIGNMENT ────────────────────
    def manage_held_items(self):
        """Let player give/take held items from team members."""
        # Items that cannot be held (consumables used from bag only)
        NON_HOLDABLE = {"Escape Rope", "Old Rod", "Good Rod",
                        "Capture Ball", "Great Ball", "Ultra Ball", "Master Ball",
                        "Revive", "Max Revive",
                        "Potion", "Super Potion", "Hyper Potion", "Full Restore",
                        "Antidote", "Burn Heal", "Awakening", "Ice Heal",
                        "Cheer Up", "Full Heal",
                        "Elixir", "Max Elixir",
                        "X Attack", "X Defense",
                        "Fire Stone", "Water Stone", "Leaf Stone", "Thunder Stone",
                        "Repel", "Super Repel", "Max Repel"}
        clear()
        section("📦  HELD ITEMS")
        slow_print(f"  {C.GRAY}Give any compatible item to a creature to hold in battle.{C.RESET}\n")

        have_holdable = [k for k, v in self.inventory.items()
                         if v > 0 and k not in NON_HOLDABLE]
        if not have_holdable and not any(c.held_item for c in self.team):
            slow_print("  No holdable items in bag and no held items on team.")
            press_enter(); return

        opts = [f"{c.name} Lv.{c.level}  Holding: {C.YELLOW}{c.held_item or 'nothing'}{C.RESET}"
                for c in self.team if c.is_alive()]
        opts.append("← Back")
        idx = menu("Which creature?", opts)
        alive = [c for c in self.team if c.is_alive()]
        if idx == len(alive): return
        target = alive[idx]

        sub_opts = []
        for item_name in have_holdable:
            desc = ITEMS.get(item_name, {}).get("desc", "")
            sub_opts.append(f"Give {item_name}  {C.GRAY}({desc}){C.RESET}")
        if target.held_item:
            sub_opts.append(f"Take back {target.held_item}")
        sub_opts.append("← Cancel")
        sc = menu(f"Held item for {target.name}:", sub_opts)

        if sc < len(have_holdable):
            chosen_item = have_holdable[sc]
            if target.held_item:
                # Return old item to bag
                self.inventory[target.held_item] = self.inventory.get(target.held_item, 0) + 1
            target.held_item = chosen_item
            target._held_item_used = False
            self.inventory[chosen_item] -= 1
            slow_print(f"  {C.GREEN}{target.name} is now holding {chosen_item}!{C.RESET}")
        elif target.held_item and sc == len(have_holdable):
            self.inventory[target.held_item] = self.inventory.get(target.held_item, 0) + 1
            target.held_item = None
            slow_print(f"  {C.GREEN}Item taken back.{C.RESET}")
        press_enter()

    # ── CREATURE MANAGEMENT HUB ──────────────────────
    def open_creatures(self):
        """Central hub: pick a creature, then manage it fully."""
        from data.creatures import MOVES as MD
        from engine.battle  import ABILITIES

        USABLE_ON_CREATURE = {
            "heal", "cure", "revive", "pp",
        }
        # Items that can be applied directly to a creature outside battle
        FIELD_ITEMS = {
            "Rare Candy": "rare_candy",
        }
        # Non-holdable item types (can't be assigned as held)
        NON_HOLDABLE = {
            "Escape Rope", "Old Rod", "Good Rod",
            "Capture Ball", "Great Ball", "Ultra Ball", "Master Ball",
            "Revive", "Max Revive",
            "Potion", "Super Potion", "Hyper Potion", "Full Restore",
            "Antidote", "Burn Heal", "Awakening", "Ice Heal",
            "Cheer Up", "Full Heal",
            "Elixir", "Max Elixir",
            "X Attack", "X Defense", "X Sp.Atk", "X Sp.Def", "X Speed",
            "Fire Stone", "Water Stone", "Leaf Stone", "Thunder Stone",
            "Repel", "Super Repel", "Max Repel",
        }

        while True:
            clear()
            section("👥  CREATURES")
            if not self.team:
                slow_print("  No creatures yet!"); press_enter(); return

            # Team list with HP bars
            opts = []
            for c in self.team:
                faint_tag = f" {C.RED}[FAINTED]{C.RESET}" if not c.is_alive() else ""
                held_tag  = f"  {C.YELLOW}[{c.held_item}]{C.RESET}" if c.held_item else ""
                nick = getattr(c, 'nickname', None)
                if nick:
                    cname_str = f"{C.BOLD}{nick}{C.RESET} {C.GRAY}({c.name}){C.RESET}"
                else:
                    cname_str = f"{C.BOLD}{c.name}{C.RESET}"
                opts.append(
                    f"{cname_str} Lv.{c.level}  "
                    f"{hp_bar(c.hp, c.max_hp, 12)}{faint_tag}{held_tag}"
                )

            opts.append("🔀  Reorder team")
            opts.append("🔃  Sort team")
            opts.append("← Back")
            idx = menu("Which creature?", opts)

            if idx == len(self.team) + 2:   # ← Back
                return
            if idx == len(self.team) + 1:   # Sort team
                self._sort_team_menu()
                continue
            if idx == len(self.team):        # Reorder team
                self._reorder_team_inline()
                continue

            c = self.team[idx]

            # ── Per-creature action loop ──────────────────────
            while True:
                clear()
                # ── Full stat card ──
                _nick = getattr(c, 'nickname', None)
                _banner_name = f"{_nick} ({c.name})" if _nick else c.name
                banner(f"  {_banner_name}  Lv.{c.level}  ", C.CYAN)

                from ui.display import TYPE_COLORS
                types_str = "/".join(
                    f"{TYPE_COLORS.get(t, C.WHITE)}{t.upper()}{C.RESET}"
                    for t in c.types
                )
                print(f"  Type    : {types_str}")
                ab_name = c.ability or "None"
                ab_desc = ABILITIES.get(ab_name, {}).get("desc", "")
                print(f"  Ability : {C.BOLD}{ab_name}{C.RESET}  {C.GRAY}{ab_desc}{C.RESET}")
                # Nature
                if getattr(c, 'nature', None):
                    from engine.core import NATURES
                    boost, lower = NATURES.get(c.nature, (None, None))
                    if boost and lower:
                        nat_str = (f"{C.CYAN}{c.nature}{C.RESET}"
                                   f"  {C.GRAY}({C.GREEN}+{boost}{C.GRAY} / {C.RED}-{lower}{C.GRAY}){C.RESET}")
                    else:
                        nat_str = f"{C.GRAY}{c.nature} (neutral){C.RESET}"
                    print(f"  Nature  : {nat_str}")
                if c.held_item:
                    print(f"  Held    : {C.YELLOW}{c.held_item}{C.RESET}")
                print(f"  {C.GRAY}{CREATURES[c.name]['desc']}{C.RESET}")
                print()

                # HP + EXP
                print(f"  HP   {hp_bar(c.hp, c.max_hp)}")
                if hasattr(c, 'exp') and c.exp_to_next > 0:
                    ratio  = min(1.0, c.exp / c.exp_to_next)
                    filled = int(ratio * 20)
                    bar    = "▪" * filled + "·" * (20 - filled)
                    print(f"  EXP  {C.CYAN}[{bar}]{C.RESET} {c.exp}/{c.exp_to_next}")
                print()

                # Core stats — mark nature-boosted (+) and nature-lowered (-) stats
                from engine.core import NATURES as _NAT
                _boost, _lower = _NAT.get(getattr(c, 'nature', None) or '', (None, None))
                def _nat_tag(sk):
                    if sk == _boost: return f" {C.GREEN}▲{C.RESET}"
                    if sk == _lower: return f" {C.RED}▼{C.RESET}"
                    return ""
                print(f"  {C.BOLD}{'STAT':<10} {'VAL':>6}{C.RESET}")
                print(f"  {'─'*18}")
                print(f"  {'HP':<10} {c.max_hp:>6}")
                print(f"  {'Attack':<10} {c.atk:>6}{_nat_tag('atk')}")
                print(f"  {'Defense':<10} {c.defense:>6}{_nat_tag('def')}")
                print(f"  {'Sp. Atk':<10} {c.sp_atk:>6}{_nat_tag('sp_atk')}")
                print(f"  {'Sp. Def':<10} {c.sp_def:>6}{_nat_tag('sp_def')}")
                print(f"  {'Speed':<10} {c.spd:>6}{_nat_tag('spd')}")
                print()

                # Moves
                print(f"  {C.BOLD}MOVES:{C.RESET}")
                for i, m in enumerate(c.moves, 1):
                    mv     = MD[m]
                    pp_now = c.pp.get(m, 0)
                    color  = C.GREEN if pp_now > mv["pp"] // 3 else C.RED
                    print(f"  {i}. {C.BOLD}{m:<16}{C.RESET} "
                          f"[{mv['type']:<8}] "
                          f"{'Phys' if mv['category']=='physical' else 'Spec' if mv['category']=='special' else 'Stat':<4}  "
                          f"Pwr:{mv['power']:<4} "
                          f"PP:{color}{pp_now}{C.RESET}/{mv['pp']}")

                # Evolution info
                evo = CREATURES[c.name]["evolution"]
                if evo:
                    for lv, nxt in evo.items():
                        print(f"\n  {C.CYAN}→ Evolves into {nxt} at Lv.{lv}{C.RESET}")
                else:
                    print(f"\n  {C.MAGENTA}✦ Final form{C.RESET}")
                stone_evo = CREATURES[c.name].get("stone_evolution", {})
                for stone, nxt in stone_evo.items():
                    print(f"  {C.CYAN}→ Or use a {stone} to evolve into {nxt} now{C.RESET}")

                # Status
                if c.status:
                    print(f"  Status  : {C.RED}{c.status.upper()}{C.RESET}")

                print()

                # Action menu
                actions = [
                    "⚔  Reorder moves",
                    "📦  Change held item",
                    "🎒  Use item",
                    "✏  Rename",
                    "← Back to team",
                ]
                ac = menu("Action:", actions)

                # ── Rename ──
                if ac == 3:
                    cur_nick = getattr(c, 'nickname', None) or ""
                    slow_print(f"  Current name: {C.BOLD}{cur_nick or c.name}{C.RESET}"
                               f"{'  ' + C.GRAY + '(' + c.name + ')' + C.RESET if cur_nick else ''}")
                    slow_print(f"  {C.GRAY}Enter a nickname (max 10 chars, blank to clear):{C.RESET}")
                    raw = input("  > ").strip()[:10]
                    c.nickname = raw if raw else None
                    if c.nickname:
                        slow_print(f"  {C.GREEN}{c.name} will now be called {C.BOLD}{c.nickname}{C.RESET}{C.GREEN}!{C.RESET}")
                    else:
                        slow_print(f"  {C.GRAY}Nickname cleared — back to {c.name}.{C.RESET}")
                    press_enter()
                    continue

                # ── Reorder moves ──
                elif ac == 0:

                    if len(c.moves) < 2:
                        slow_print(f"  {C.YELLOW}Only one move — nothing to reorder.{C.RESET}")
                        press_enter(); continue
                    while True:
                        clear()
                        section(f"⚔  REORDER MOVES  —  {c.name}")
                        for i, m in enumerate(c.moves, 1):
                            mv = MD[m]
                            print(f"  {i}. {C.BOLD}{m:<16}{C.RESET} [{mv['type']}] Pwr:{mv['power']}")
                        move_opts = [f"{m}" for m in c.moves] + ["← Done"]
                        src = menu("Move which slot?", move_opts)
                        if src == len(c.moves): break
                        dst_opts = [f"{m}" for i, m in enumerate(c.moves) if i - 1 != src] + ["← Cancel"]
                        dst_raw  = menu(f"Swap '{c.moves[src]}' with?", dst_opts)
                        if dst_raw == len(c.moves) - 1: continue
                        actual = [i for i in range(len(c.moves)) if i != src]
                        dst    = actual[dst_raw]
                        c.moves[src], c.moves[dst] = c.moves[dst], c.moves[src]
                        c.pp[c.moves[src]], c.pp[c.moves[dst]] = c.pp[c.moves[dst]], c.pp[c.moves[src]]
                        slow_print(f"  {C.GREEN}Moves swapped!{C.RESET}")

                # ── Change held item ──
                elif ac == 1:
                    have_holdable = [k for k, v in self.inventory.items()
                                     if v > 0 and k not in NON_HOLDABLE]
                    sub_opts = []
                    for item_name in have_holdable:
                        desc = ITEMS.get(item_name, {}).get("desc", "")
                        sub_opts.append(f"Give {item_name}  {C.GRAY}({desc}){C.RESET}")
                    if c.held_item:
                        sub_opts.append(f"Take back {c.held_item}")
                    sub_opts.append("← Cancel")
                    sc = menu(f"Held item for {c.name}:", sub_opts)
                    cancel_idx = len(sub_opts) - 1
                    take_idx   = len(have_holdable) if c.held_item else None
                    if sc == cancel_idx:
                        pass
                    elif take_idx is not None and sc == take_idx:
                        self.inventory[c.held_item] = self.inventory.get(c.held_item, 0) + 1
                        slow_print(f"  {C.GREEN}Took back {c.held_item}.{C.RESET}")
                        c.held_item = None
                        c._held_item_used = False
                    elif sc < len(have_holdable):
                        chosen = have_holdable[sc]
                        if c.held_item:
                            self.inventory[c.held_item] = self.inventory.get(c.held_item, 0) + 1
                        c.held_item = chosen
                        c._held_item_used = False
                        self.inventory[chosen] -= 1
                        slow_print(f"  {C.GREEN}{c.name} is now holding {chosen}!{C.RESET}")
                    press_enter()

                # ── Use item ──
                elif ac == 2:
                    # Build usable list: heal/cure/revive/pp + Rare Candy + Evolution Stones
                    usable = {}
                    stone_evo = CREATURES[c.name].get("stone_evolution", {})
                    for k, v in self.inventory.items():
                        if v <= 0: continue
                        itype = ITEMS.get(k, {}).get("type", "")
                        if itype in ("heal", "cure", "revive", "pp"):
                            usable[k] = v
                        if k == "Rare Candy":
                            usable[k] = v
                        if itype == "stone" and k in stone_evo:
                            usable[k] = v
                    if not usable:
                        slow_print(f"  {C.YELLOW}No usable items in bag.{C.RESET}")
                        press_enter(); continue
                    item_opts = [
                        f"{k} x{v}  {C.GRAY}({ITEMS[k]['desc']}){C.RESET}"
                        for k, v in usable.items()
                    ] + ["← Cancel"]
                    ic = menu(f"Use on {c.name}:", item_opts)
                    if ic == len(usable):
                        continue
                    item_name = list(usable.keys())[ic]
                    idata     = ITEMS[item_name]
                    itype     = idata.get("type", "")

                    if item_name == "Rare Candy":
                        if c.level >= 100:
                            slow_print(f"  {C.YELLOW}{c.name} is already at max level!{C.RESET}")
                        else:
                            self.inventory[item_name] -= 1
                            events = c.gain_exp(c.exp_to_next - c.exp)  # force level-up
                            self._handle_exp_events(c, events)
                            slow_print(f"  {C.GREEN}{c.name} grew to Lv.{c.level}!{C.RESET}")
                        press_enter()

                    elif itype == "stone":
                        target = stone_evo.get(item_name)
                        slow_print(f"\n  {C.MAGENTA}❆❆  {c.name} is bathed in the {item_name}'s power…  ❆❆{C.RESET}")
                        time.sleep(0.8)
                        if confirm(f"  Evolve {c.name} into {target}?"):
                            old = c.name
                            self.inventory[item_name] -= 1
                            c.evolve(target)
                            slow_print(f"  {C.MAGENTA}❆  {old} evolved into "
                                       f"{C.BOLD}{target}{C.RESET}{C.MAGENTA}!  ❆{C.RESET}")
                            print('\a', end='', flush=True)
                            self._check_achievement("first_evolution")
                        else:
                            slow_print(f"  {C.GRAY}{c.name} did not evolve. The {item_name} was not used.{C.RESET}")
                        press_enter()

                    elif itype == "heal":
                        if not c.is_alive():
                            slow_print(f"  {C.RED}{c.name} is fainted — revive it first.{C.RESET}")
                        elif c.hp >= c.max_hp:
                            slow_print(f"  {C.YELLOW}{c.name} is already at full HP.{C.RESET}")
                        else:
                            healed = min(idata["amount"], c.max_hp - c.hp)
                            c.heal(idata["amount"])
                            if idata.get("amount", 0) >= 9999:
                                c.status = None
                            self.inventory[item_name] -= 1
                            slow_print(f"  {C.GREEN}{c.name} recovered {healed} HP!{C.RESET}")
                        press_enter()

                    elif itype == "cure":
                        target_status = idata["status"]
                        if target_status == "all":
                            if not c.status:
                                slow_print(f"  {C.YELLOW}{c.name} has no status to cure.{C.RESET}")
                            else:
                                c.status = None; c.sleep_turns = 0; c.confusion_turns = 0
                                self.inventory[item_name] -= 1
                                slow_print(f"  {C.GREEN}{c.name} was fully cured!{C.RESET}")
                        elif c.status == target_status:
                            c.status = None; c.sleep_turns = 0; c.confusion_turns = 0
                            self.inventory[item_name] -= 1
                            slow_print(f"  {C.GREEN}{c.name} was cured!{C.RESET}")
                        else:
                            slow_print(f"  {C.YELLOW}No effect — {c.name} doesn't have that status.{C.RESET}")
                        press_enter()

                    elif itype == "revive":
                        if c.is_alive():
                            slow_print(f"  {C.YELLOW}{c.name} hasn't fainted.{C.RESET}")
                        else:
                            c.hp = int(c.max_hp * idata["amount"])
                            self.inventory[item_name] -= 1
                            slow_print(f"  {C.GREEN}{c.name} was revived with {c.hp} HP!{C.RESET}")
                        press_enter()

                    elif itype == "pp":
                        if not c.moves:
                            slow_print(f"  {C.YELLOW}{c.name} has no moves.{C.RESET}")
                        else:
                            from data.creatures import MOVES as MOVE_DATA
                            for m in c.moves:
                                max_pp = MOVE_DATA[m]["pp"]
                                c.pp[m] = min(max_pp, c.pp.get(m, 0) + idata["amount"])
                            self.inventory[item_name] -= 1
                            slow_print(f"  {C.GREEN}{c.name}'s move PP restored!{C.RESET}")
                        press_enter()

                # ── Back ──
                elif ac == 4:
                    break


    def _sort_team_menu(self):
        """Sort the team in-place by the player's chosen criterion."""
        clear()
        section("🔃  SORT TEAM")
        sort_opts = [
            "By Level  (highest first)",
            "By HP %   (lowest first — lead with injured)",
            "By Name   (A → Z)",
            "← Cancel",
        ]
        choice = menu("Sort by:", sort_opts)
        if choice == 0:   # Level desc
            self.team.sort(key=lambda c: c.level, reverse=True)
            slow_print(f"  {C.GREEN}Team sorted by Level (highest first).{C.RESET}")
        elif choice == 1: # HP % asc (most injured first — useful for triage)
            self.team.sort(key=lambda c: c.hp / c.max_hp if c.max_hp else 0)
            slow_print(f"  {C.GREEN}Team sorted by HP% (most injured first).{C.RESET}")
        elif choice == 2: # Name asc
            nick_or_name = lambda c: getattr(c, 'nickname', None) or c.name
            self.team.sort(key=nick_or_name)
            slow_print(f"  {C.GREEN}Team sorted alphabetically.{C.RESET}")
        else:
            return
        press_enter()

    def _reorder_team_inline(self):
        """Reorder team by picking a creature and a destination slot."""
        clear()
        section("🔀  REORDER TEAM")
        while True:
            opts = [
                f"{i+1}. {c.name} Lv.{c.level}  {hp_bar(c.hp, c.max_hp, 12)}"
                for i, c in enumerate(self.team)
            ] + ["← Done"]
            src = menu("Move which creature?", opts)
            if src == len(self.team): break
            dst_opts = [
                f"{i+1}. {c.name}" for i, c in enumerate(self.team) if i != src
            ] + ["← Cancel"]
            dst_raw = menu(f"Move {self.team[src].name} to which slot?", dst_opts)
            if dst_raw == len(dst_opts) - 1: continue
            actual = [i for i in range(len(self.team)) if i != src]
            dst    = actual[dst_raw]
            self.team.insert(dst, self.team.pop(src))
            slow_print(f"  {C.GREEN}Team reordered!{C.RESET}")
        press_enter()



    # ── BADGES ─────────────────────────────────
    def open_badges(self):
        clear()
        section("🏅  BADGES")
        total = len(REQUIRED_BADGES)
        print(f"  Collected: {C.YELLOW}{len(self.badges)}/{total}{C.RESET}\n")
        for b in REQUIRED_BADGES:
            if b in self.badges:
                print(f"  {C.YELLOW}★  {b}{C.RESET}")
            else:
                print(f"  {C.GRAY}○  {b}{C.RESET}")
        press_enter()

    # ── TRAINER STATS ───────────────────────────
    def open_stats(self):
        clear()
        section("📊  TRAINER CARD")
        tod, tod_color, tod_icon = time_of_day()
        slow_print(f"  Name    : {C.BOLD}{self.player_name}{C.RESET}  {C.CYAN}{getattr(self,'avatar','♂')}{C.RESET}")
        if getattr(self, 'is_champion', False):
            slow_print(f"  Title   : {C.YELLOW}★  Champion  ★{C.RESET}")
        if getattr(self, 'nuzlocke', False):
            slow_print(f"  Mode    : {C.RED}⚠  NUZLOCKE — creatures die forever{C.RESET}")
        slow_print(f"  Money   : {C.YELLOW}₽{self.money}{C.RESET}")
        slow_print(f"  Badges  : {len(self.badges)}/{len(REQUIRED_BADGES)}")
        slow_print(f"  Battles : {self.steps}")
        _ps = getattr(self, 'play_seconds', 0)
        _ph, _pm = _ps // 3600, (_ps % 3600) // 60
        slow_print(f"  Playtime: {_ph}h {_pm:02d}m")
        slow_print(f"  Town    : {self.town}")
        slow_print(f"  Time    : {tod_color}{tod_icon} {tod}{C.RESET}")
        # Rival score
        r = getattr(self, 'rival', None)
        if r and r.starter:
            score_color = C.GREEN if r.player_wins >= r.rival_wins else C.RED
            slow_print(f"  Rival   : {C.BOLD}{r.name}{C.RESET}  "
                       f"({score_color}You {r.player_wins}\u2013{r.rival_wins} {r.name}{C.RESET})")
        print()
        team_summary(self.team)
        press_enter()

    # ── SHOP (buy + sell combined) ──────────────────────────
    def visit_shop(self, stock, badge_count=0):
        # Items that unlock globally in ALL shops as badge count increases.
        # This ensures early-town shops progressively stock better goods on revisit.
        BADGE_BONUS_STOCK = [
            (1, "Super Potion"),
            (2, "Great Ball"),
            (2, "Antidote"),
            (2, "Awakening"),
            (2, "Fire Stone"),
            (2, "Water Stone"),
            (2, "Leaf Stone"),
            (2, "Thunder Stone"),
            (1, "Repel"),
            (3, "Super Repel"),
            (5, "Max Repel"),
            (3, "Hyper Potion"),
            (3, "Revive"),
            (3, "Elixir"),
            (4, "Ultra Ball"),
            (4, "Full Heal"),
            (5, "Full Restore"),
            (5, "Max Revive"),
            (6, "Max Elixir"),
            (7, "Master Ball"),
        ]
        # Merge bonus stock into base stock without duplicates, preserving order
        merged_stock = list(stock)
        for req_badges, item in BADGE_BONUS_STOCK:
            if badge_count >= req_badges and item not in merged_stock:
                merged_stock.append(item)
        stock = merged_stock

        BADGE_LOCKED = {
            "Hyper Potion": 3, "Full Restore": 5, "Ultra Ball": 3,
            "Master Ball": 7, "Max Revive": 5, "Max Elixir": 6,
            "X Attack": 2, "X Defense": 2,
        }
        NON_SELLABLE = {"escape", "fish"}

        while True:
            clear()
            section(f"🛒  SHOP  {C.YELLOW}₽{self.money}{C.RESET}")
            top = menu("What would you like to do?",
                       ["🛠  Buy", "💰  Sell", "← Leave"])

            # ── BUY ──────────────────────────────────────────────────
            if top == 0:
                available = [item for item in stock
                             if badge_count >= BADGE_LOCKED.get(item, 0)]
                locked    = [item for item in stock if item not in available]
                while True:
                    clear()
                    section(f"🛠  BUY  {C.YELLOW}₽{self.money}{C.RESET}")
                    if locked:
                        slow_print(f"  {C.GRAY}Locked (need more badges): {', '.join(locked)}{C.RESET}")
                    opts = [
                        f"{item:<20} {C.YELLOW}₽{ITEMS[item]['price']}{C.RESET}  "
                        f"{C.GRAY}({ITEMS[item]['desc']}){C.RESET}"
                        for item in available
                    ] + ["← Back"]
                    choice = menu("Buy which item?", opts)
                    if choice == len(available):
                        break
                    item  = available[choice]
                    price = ITEMS[item]["price"]
                    max_can = self.money // price if price > 0 else 99
                    if max_can == 0:
                        slow_print(f"  {C.RED}Not enough money!{C.RESET}")
                        press_enter(); continue
                    qty = self._ask_qty(1, max_can, f"Buy how many {item}? (max {max_can})")
                    if qty == 0:
                        continue
                    total = price * qty
                    self.money -= total
                    self.inventory[item] = self.inventory.get(item, 0) + qty
                    slow_print(f"  {C.GREEN}Bought {qty}x {item} for {C.YELLOW}₽{total}{C.RESET}  "
                               f"| Remaining: {C.YELLOW}₽{self.money}{C.RESET}")
                    press_enter()

            # ── SELL ─────────────────────────────────────────────────
            elif top == 1:
                while True:
                    clear()
                    section(f"💰  SELL  {C.YELLOW}₽{self.money}{C.RESET}")
                    sellable = {
                        k: v for k, v in self.inventory.items()
                        if v > 0
                        and ITEMS.get(k, {}).get("price", 0) > 0
                        and ITEMS.get(k, {}).get("type") not in NON_SELLABLE
                    }
                    if not sellable:
                        slow_print("  Nothing to sell.")
                        press_enter(); break
                    opts = [
                        f"{k:<20} x{v:<4} {C.GRAY}sell @ {C.YELLOW}₽{ITEMS[k]['price']//2}{C.RESET}{C.GRAY} each{C.RESET}"
                        for k, v in sellable.items()
                    ] + ["← Back"]
                    choice = menu("Sell which item?", opts)
                    if choice == len(sellable):
                        break
                    item    = list(sellable.keys())[choice]
                    max_qty = sellable[item]
                    qty = self._ask_qty(1, max_qty, f"Sell how many {item}? (max {max_qty})")
                    if qty == 0:
                        continue
                    sell_price = (ITEMS[item]["price"] // 2) * qty
                    self.inventory[item] -= qty
                    self.money += sell_price
                    slow_print(f"  {C.GREEN}Sold {qty}x {item} for {C.YELLOW}₽{sell_price}{C.RESET}  "
                               f"| Balance: {C.YELLOW}₽{self.money}{C.RESET}")
                    press_enter()

            # ── Leave ──
            else:
                return

    def _ask_qty(self, lo, hi, prompt):
        """Prompt for an integer quantity between lo and hi. Returns 0 to cancel."""
        if lo == hi:
            return lo
        slow_print(f"  {C.CYAN}{prompt}{C.RESET}")
        while True:
            raw = input(f"  {C.GRAY}(enter number, or 0 to cancel) > {C.RESET}").strip()
            if raw == "0":
                return 0
            if raw.isdigit():
                n = int(raw)
                if lo <= n <= hi:
                    return n
            slow_print(f"  {C.RED}Enter a number between {lo} and {hi}, or 0 to cancel.{C.RESET}")

    # ── MOVE TUTOR ──────────────────────────────
    def visit_move_tutor(self, town_name):
        from data.creatures import MOVES as MOVE_DATA
        tutors = MOVE_TUTORS.get(town_name, [])
        if not tutors:
            slow_print("  No move tutor here."); press_enter(); return
        clear()
        section(f"🎓  MOVE TUTOR  —  {town_name}")
        slow_print(f"  {C.GRAY}\"I can teach your creatures powerful techniques!\"{C.RESET}\n")
        alive = [c for c in self.team if c.is_alive()]
        if not alive:
            slow_print("  No alive creatures."); press_enter(); return

        tutor_opts = [f"{m}  {C.YELLOW}₽{cost}{C.RESET}  "
                      f"{C.GRAY}[{MOVE_DATA[m]['type']}] Pwr:{MOVE_DATA[m]['power']}{C.RESET}"
                      for m, cost in tutors]
        tutor_opts.append("Leave")
        tc = menu("Which move to learn?", tutor_opts)
        if tc == len(tutors): return

        move_name, cost = tutors[tc]
        mv = MOVE_DATA[move_name]
        if self.money < cost:
            slow_print(f"  {C.RED}Not enough money! Need ₽{cost}.{C.RESET}")
            press_enter(); return

        c_opts = [f"{c.name} Lv.{c.level}" for c in alive] + ["Cancel"]
        cc = menu(f"Teach {move_name} to which creature?", c_opts)
        if cc == len(alive): return
        target = alive[cc]

        if move_name in target.moves:
            slow_print(f"  {C.YELLOW}{target.name} already knows {move_name}!{C.RESET}")
            press_enter(); return

        self.money -= cost
        if len(target.moves) < 4:
            target.moves.append(move_name)
            target.pp[move_name] = mv["pp"]
            slow_print(f"  {C.GREEN}{target.name} learned {move_name}!{C.RESET}")
        else:
            # Must replace
            slow_print(f"  {target.name} already knows 4 moves. Choose one to replace:")
            r_opts = [f"Replace {m}  {C.GRAY}[{MOVE_DATA[m]['type']}] Pwr:{MOVE_DATA[m]['power']}{C.RESET}"
                      for m in target.moves] + ["Cancel (don't learn)"]
            rc = menu("Replace which?", r_opts)
            if rc == len(target.moves):
                self.money += cost  # refund
            else:
                old = target.moves[rc]
                target.moves[rc] = move_name
                del target.pp[old]
                target.pp[move_name] = mv["pp"]
                slow_print(f"  {C.GREEN}{target.name} forgot {old} and learned {move_name}!{C.RESET}")
        press_enter()

    # ── REORDER TEAM (legacy, kept for internal use) ──────────
    def reorder_team(self):
        """Let player drag-reorder their team."""
        clear()
        section("🔀  REORDER TEAM")
        slow_print(f"  {C.GRAY}Pick a creature to move, then pick its new position.{C.RESET}\n")
        while True:
            opts = [f"{i+1}. {c.name} Lv.{c.level}  {hp_bar(c.hp, c.max_hp, 12)}"
                    for i, c in enumerate(self.team)]
            opts.append("← Done")
            src = menu("Move which creature?", opts)
            if src == len(self.team): break
            dst_opts = [f"{i+1}. {c.name}" for i, c in enumerate(self.team)
                        if i != src]
            dst_opts.append("← Cancel")
            dst_raw = menu(f"Move {self.team[src].name} to which slot?", dst_opts)
            if dst_raw == len(dst_opts) - 1: continue
            # Map dst_raw back to actual index (skipping src)
            actual_indices = [i for i in range(len(self.team)) if i != src]
            dst = actual_indices[dst_raw]
            self.team.insert(dst, self.team.pop(src))
            slow_print(f"  {C.GREEN}Team reordered!{C.RESET}")
        press_enter()

    # ── PICK LEAD ──────────────────────────────
    def _pick_lead(self, current=None):
        alive = [c for c in self.team if c.is_alive()]
        if not alive:
            slow_print(f"  {C.RED}All your creatures fainted! Visit an Inn to heal.{C.RESET}")
            press_enter(); return None
        # If current lead is still alive, reuse it (no prompt needed)
        if current is not None and current.is_alive():
            return current
        if len(alive) == 1:
            return alive[0]
        opts = [f"{c.name} Lv.{c.level}  {hp_bar(c.hp, c.max_hp, 12)}"
                for c in alive]
        idx = menu("Lead with which creature?", opts)
        return alive[idx]

    # ── GYM ────────────────────────────────────
    def challenge_gym(self, gym_data):
        badge  = gym_data["badge"]
        leader = gym_data["leader"]
        quote  = gym_data.get("quote", "Prepare yourself!")

        if badge in self.badges:
            slow_print(f"  {C.YELLOW}You already have the {badge}.{C.RESET}")
            press_enter(); return

        banner(f"  GYM LEADER  {leader.upper()}  ", C.RED)
        slow_print(f"  {C.BOLD}{leader}{C.RESET}: «{quote}»")
        press_enter()

        player_c = self._pick_lead()
        if player_c is None: return

        prize_money = 0
        for cname, lv in gym_data["team"]:
            enemy  = Creature(cname, lv, is_player=False)
            result, obj = run_battle(player_c, enemy, self.inventory,
                                     self.team, wild=False, trainer_name=leader)
            if result == "win":
                self._count_battle()
                self.award_exp(player_c, enemy)
                prize_money += lv * 60
                alive = [c for c in self.team if c.is_alive()]
                if alive and not player_c.is_alive():
                    player_c = alive[0]
            elif result == "lose":
                slow_print(f"\n  {C.RED}You were defeated! Visit an Inn to recover.{C.RESET}")
                press_enter(); return

        banner(f"  YOU DEFEATED {leader.upper()}!  ", C.GREEN)
        slow_print(f"  {C.BOLD}{leader}{C.RESET}: «You've earned the "
                   f"{C.YELLOW}{badge}{C.RESET}!»")
        self.badges.append(badge)
        print('\a', end='', flush=True)
        self._check_achievement("first_badge")
        if len(self.badges) == len(REQUIRED_BADGES):
            self._check_achievement("all_badges")
        self.earn_money(prize_money)

        # Auto-save after each badge
        self.save()
        press_enter()
        # Rival encounter check — some encounters trigger right after a gym win
        trigger_rival_if_due(self)

    # ── EXPLORE ────────────────────────────────
    def explore(self, area_name):
        clear()
        section(f"🌿  EXPLORING  {area_name}")
        weather = random.choice(WEATHER_POOL)
        if weather:
            slow_print(f"  {C.CYAN}☁  Weather today: {weather}{C.RESET}")

        # Day/Night flavour
        tod, tod_color, tod_icon = time_of_day()
        slow_print(f"  {tod_color}{tod_icon}  It is {tod}.{C.RESET}")
        if night_bonus_areas():
            slow_print(f"  {C.BLUE}👻  Ghost-type creatures are more active at night!{C.RESET}")
        slow_print(f"  You venture into {area_name}...", 0.02)

        trainer_pool = RANDOM_TRAINERS.get(area_name, [])
        steps_in_area = 0
        player_c = self._pick_lead()  # establish lead once at area entry
        if player_c is None: return

        while True:
            clear()
            section(f"🌿  EXPLORING  {area_name}")
            alive_hp = "  ".join(
                f"{C.BOLD}{c.name}{C.RESET} {hp_bar(c.hp, c.max_hp, 10)}"
                for c in self.team if c.is_alive()
            )
            if alive_hp:
                print(f"  {alive_hp}")
            if self.repel_steps > 0:
                print(f"  {C.CYAN}🛡  Repel active: {self.repel_steps} "
                      f"encounter{'s' if self.repel_steps != 1 else ''} left{C.RESET}")
            opts = ["Walk further", "🏕  Rest (heal 20% HP)", "← Return to town"]
            if self.inventory.get("Escape Rope", 0) > 0:
                opts.insert(2, "🪢  Use Escape Rope (leave instantly)")
            choice = menu("", opts)
            label  = opts[choice]

            if "Return" in label:
                slow_print("  You leave the area safely."); break

            if "Escape Rope" in label:
                self.inventory["Escape Rope"] -= 1
                slow_print(f"  {C.CYAN}You escape using the rope!{C.RESET}")
                press_enter(); break

            if "Rest" in label:
                clear()
                section(f"🏕  REST  —  {area_name}")
                healed_any = False
                for c in self.team:
                    if c.is_alive() and c.hp < c.max_hp:
                        old_hp = c.hp
                        c.heal(int(c.max_hp * 0.2))
                        slow_print(f"  {C.GREEN}{c.name} restored {c.hp - old_hp} HP "
                                   f"({c.hp}/{c.max_hp}){C.RESET}")
                        healed_any = True
                if not healed_any:
                    slow_print(f"  {C.GRAY}Your team is already healthy.{C.RESET}")
                press_enter(); continue

            # Walk
            steps_in_area += 1
            roll = random.random()

            # ── Hidden item (8% chance) ──
            if roll < 0.08:
                treasure_pool = ["Potion", "Super Potion", "Capture Ball",
                                 "Antidote", "Elixir"]
                found = random.choice(treasure_pool)
                self.inventory[found] = self.inventory.get(found, 0) + 1
                slow_print(f"\n  {C.YELLOW}✦  You found a hidden {found}!{C.RESET}")
                # Berry chance — seasonal berry has boosted odds
                season_berry = SEASONAL_BERRY.get(self.season)
                if random.random() < 0.3:
                    berry_pool = ["Lum Berry", "Sitrus Berry", "Oran Berry"]
                    # Seasonal berry appears in the pool with double weight
                    if season_berry:
                        berry_pool.append(season_berry)
                    berry = random.choice(berry_pool)
                    self.inventory[berry] = self.inventory.get(berry, 0) + 1
                    slow_print(f"  {C.GREEN}...and a {berry}!{C.RESET}")
                    if season_berry and berry == season_berry:
                        slow_print(f"  {C.CYAN}(A seasonal {season_berry} — rare this {self.season}!){C.RESET}")
                press_enter(); continue

            # ── Trainer (18%) ──
            elif roll < 0.26 and trainer_pool:
                # Badge-scaled levels: +5 per 2 badges earned
                badge_bonus = (len(self.badges) // 2) * 5
                # Build a trainer team of 1-3 creatures
                team_size = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                trainer_team = [random.choice(trainer_pool) for _ in range(team_size)]
                cname, lv = trainer_team[0]
                t_title = random.choice(list(RANDOM_TRAINER_NAMES))
                t_first = random.choice(RANDOM_TRAINER_NAMES[t_title])
                t_name  = f"{t_title} {t_first}"
                trainer_key = f"{area_name}::{t_name}"
                rematch = trainer_key in self._defeated_trainers
                clear()
                banner(f"  TRAINER BATTLE  ", C.YELLOW)
                if rematch:
                    slow_print(f"\n  {C.BOLD}{t_name}{C.RESET} spots you again!")
                    slow_print(f"  {C.YELLOW}{t_name}{C.RESET}: \"You beat me before, "
                               f"but I've been training! Let's go again!\"")
                else:
                    slow_print(f"\n  {C.BOLD}{t_name}{C.RESET} steps out from the tall grass!")
                    slow_print(f"  {C.YELLOW}{t_name}{C.RESET}: \"Hey! You there! Let's battle!\"")
                team_preview = ", ".join(f"{n} Lv.{l + badge_bonus}" for n, l in trainer_team)
                slow_print(f"  {C.GRAY}{t_name} has: {team_preview}{C.RESET}")
                press_enter()
                player_c = self._pick_lead(player_c)
                if player_c is None: break
                prize_money = 0
                lost = False
                for cname, lv in trainer_team:
                    enemy = Creature(cname, lv + badge_bonus, is_player=False)
                    result, obj = run_battle(player_c, enemy, self.inventory,
                                             self.team, wild=False,
                                             trainer_name=t_name, weather=weather)
                    if result == "win":
                        self._count_battle()
                        self.award_exp(player_c, enemy)

                        prize_money += (lv + badge_bonus) * 40
                        alive_after = [c for c in self.team if c.is_alive()]
                        if alive_after and not player_c.is_alive():
                            player_c = alive_after[0]
                        clear()
                    elif result == "lose":
                        lost = True
                        break
                if lost:
                    slow_print(f"  {C.RED}You lost! Retreating...{C.RESET}")
                    press_enter()
                    clear()
                    break
                else:
                    self.earn_money(prize_money)
                    slow_print(f"  {C.YELLOW}{t_name}: \"Good battle!\"  {C.RESET}")
                    self._defeated_trainers.add(trainer_key)
                    press_enter()
                    clear()

            # ── Wild (50%) ──
            elif roll < 0.76:
                # ── Repel: cancels this wild encounter and burns one charge ──
                if self.repel_steps > 0:
                    self.repel_steps -= 1
                    remaining = self.repel_steps
                    slow_print(f"  {C.CYAN}🛡  Your Repel kept the wild creatures away. "
                               f"({remaining} encounter{'s' if remaining != 1 else ''} left){C.RESET}")
                    if remaining == 0:
                        slow_print(f"  {C.YELLOW}Your Repel wore off!{C.RESET}")
                    press_enter()
                else:
                    # Badge-scaled levels: +5 per 2 badges earned
                    badge_bonus = (len(self.badges) // 2) * 5
                    # Build pool: base wild pool + any seasonal additions
                    seasonal_extras = SEASONAL_WILDS.get(self.season, {}).get(area_name, [])

                    # At night, ghost-types have higher weight
                    if night_bonus_areas() and random.random() < 0.35:
                        ghost_pool = [("Ghostlet", 5, 30), ("Spectrex", 20, 45)]
                        night_pool = [p for p in ghost_pool
                                      if p[0] in [w[0] for w in WILD_AREAS.get(area_name, [])]]
                        wild_pool_override = night_pool if night_pool else None
                    else:
                        wild_pool_override = None

                    if wild_pool_override:
                        name, lo, hi = random.choice(wild_pool_override)
                        lv = random.randint(lo + badge_bonus, hi + badge_bonus)
                        wild = Creature(name, lv, is_player=False)
                    elif seasonal_extras and random.random() < 0.30:
                        # 30% chance to pull from the seasonal bonus pool
                        name, lo, hi = random.choice(seasonal_extras)
                        lv = random.randint(lo + badge_bonus, hi + badge_bonus)
                        wild = Creature(name, lv, is_player=False)
                        slow_print(f"  {SEASON_COLORS.get(self.season, C.GREEN)}"
                                   f"✦ A {self.season} visitor!{C.RESET}")
                    else:
                        wild = random_wild(area_name, badge_bonus=badge_bonus)


                    if wild:
                        slow_print(f"\n  {C.YELLOW}A wild {C.BOLD}{wild.name}{C.RESET}"
                                   f"{C.YELLOW} appeared! (Lv.{wild.level}){C.RESET}")
                        press_enter()
                        player_c = self._pick_lead(player_c)
                        if player_c is None: break

                        result, obj = run_battle(player_c, wild, self.inventory,
                                                 self.team, wild=True, weather=weather)
                        if result == "win":
                            self.seen.add(wild.name)
                            self._count_battle()
                            self.award_exp(player_c, wild)
                            self.earn_money(max(wild.level * 15, 100))
                            alive_after = [c for c in self.team if c.is_alive()]
                            if alive_after and not player_c.is_alive():
                                player_c = alive_after[0]
                            clear()
                        elif result == "caught":
                            self._count_battle()
                            captured = obj
                            self.seen.add(captured.name)
                            self.caught.add(captured.name)
                            # If the captured wild was holding an item, give it to the player
                            if captured.held_item:
                                stolen = captured.held_item
                                self.inventory[stolen] = self.inventory.get(stolen, 0) + 1
                                captured.held_item = None
                                slow_print(f"  {C.YELLOW}★  {captured.name} was holding {stolen}! You got it!{C.RESET}")
                            if len(self.team) < 6:
                                self.team.append(captured)
                                slow_print(f"  {C.GREEN}★  {captured.name} joined your team!{C.RESET}")
                                self._check_achievement("first_catch")
                                self._check_pokedex_completion()
                                if len(self.team) == 6:
                                    self._check_achievement("team_full")
                                # Offer nickname
                                slow_print(f"  {C.GRAY}Give {captured.name} a nickname? (blank to skip):{C.RESET}")
                                _nick = input("  > ").strip()[:10]
                                if _nick:
                                    captured.nickname = _nick
                                    slow_print(f"  {C.GREEN}Nicknamed {C.BOLD}{_nick}{C.RESET}{C.GREEN}!{C.RESET}")
                            else:
                                slow_print(f"  {C.YELLOW}Team full (max 6)! "
                                           f"{captured.name} was released.{C.RESET}")
                            press_enter()
                        elif result == "lose":
                            slow_print(f"  {C.RED}Your creatures fainted! Retreating...{C.RESET}")
                            press_enter(); break


            else:
                msgs = [
                    "Nothing but rustling leaves...",
                    "The wind howls through the area.",
                    "Footprints in the dirt — but nothing nearby.",
                    "A cool breeze passes by.",
                    "You find a berry bush but nothing useful.",
                    "Strange sounds echo in the distance...",
                ]
                slow_print(f"  {C.GRAY}{random.choice(msgs)}{C.RESET}")
                press_enter()

    # ── ELITE FOUR ─────────────────────────────
    def challenge_elite_four(self):
        missing = [b for b in REQUIRED_BADGES if b not in self.badges]
        if missing:
            slow_print(f"  {C.RED}You need ALL {len(REQUIRED_BADGES)} badges!{C.RESET}")
            slow_print(f"  {C.YELLOW}Missing: {', '.join(missing)}{C.RESET}")
            press_enter(); return

        rematch = getattr(self, 'is_champion', False)

        if rematch:
            banner("  ★  ELITE FOUR REMATCH  ★  ", C.MAGENTA)
            slow_print("""
  The Elite Four await a rematch — stronger than ever.
  No Inn between rounds. Only your team will carry you through.
""", 0.02)
        else:
            banner("  ★  THE ELITE FOUR  ★  ", C.MAGENTA)
            slow_print("""
  Four masters stand between you and the championship.
  No Inn between rounds. Only your team will carry you through.
""", 0.02)
        if not confirm("  Are you ready?"):
            return

        player_c = self._pick_lead()
        if player_c is None: return

        for i, challenger in enumerate(ELITE_FOUR):
            clear()
            is_champ = (i == len(ELITE_FOUR) - 1)
            color    = C.YELLOW if is_champ else C.RED
            title    = "★  CHAMPION  ★" if is_champ else challenger["name"].upper()
            banner(f"  {title}  ", color)
            slow_print(f"  {C.BOLD}{challenger['name']}{C.RESET} — {challenger['title']}")
            slow_print(f"  «Your journey ends here, {self.player_name}!»")
            press_enter()

            # Rematch: scale every Elite Four member up to at least level 70
            # (relative boost preserved so the Champion still hits hardest).
            team_list = challenger["team"]
            if rematch:
                team_list = [(cname, max(70, lv + 20)) for cname, lv in team_list]

            for cname, lv in team_list:
                enemy  = Creature(cname, lv, is_player=False)
                result, obj = run_battle(player_c, enemy, self.inventory,
                                         self.team, wild=False,
                                         trainer_name=challenger["name"])
                if result == "win":
                    self._count_battle()
                    self.award_exp(player_c, enemy)
                    alive = [c for c in self.team if c.is_alive()]
                    if alive and not player_c.is_alive():
                        player_c = alive[0]
                elif result == "lose":
                    slow_print(f"\n  {C.RED}Defeated by {challenger['name']}...{C.RESET}")

                    slow_print("  Heal up and try again!")
                    press_enter(); return

            slow_print(f"\n  {C.GREEN}★  {challenger['name']} defeated!{C.RESET}")
            press_enter()

        # CHAMPION!
        clear()
        banner("  ★ ★ ★  CHAMPION!  ★ ★ ★", C.YELLOW)
        name_centered = self.player_name.upper().center(44)
        slow_print(f"""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║   {name_centered} ║
  ║         IS THE NEW CREATURE CHAMPION!        ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝
""", 0.015)
        slow_print(f"  Battles fought: {C.YELLOW}{self.steps}{C.RESET}")
        slow_print(f"  Final team:")
        team_summary(self.team)
        if not rematch:
            self._check_achievement("champion")
            self.is_champion = True
        self.save()
        press_enter()
        # Final rival battle fires here
        if not rematch:
            trigger_post_elite_rival(self)

    # ── GO FISHING ─────────────────────────────
    def go_fishing(self):
        """Fish for water creatures in the current town using Old Rod or Good Rod."""
        has_old = self.inventory.get("Old Rod", 0) > 0
        has_good = self.inventory.get("Good Rod", 0) > 0
        if not has_old and not has_good:
            slow_print(f"  {C.YELLOW}You don't have a fishing rod! Buy one at a shop.{C.RESET}")
            press_enter(); return

        # Check if there are fish in this town
        old_pool  = FISH_OLD_ROD.get(self.town, [])
        good_pool = FISH_GOOD_ROD.get(self.town, [])
        if not old_pool and not good_pool:
            slow_print(f"  {C.GRAY}No good fishing spots in {self.town}.{C.RESET}")
            press_enter(); return

        # Choose rod
        if has_old and has_good:
            rod_choice = menu("Which rod?", ["🎣  Old Rod (common water creatures)",
                                              "🎣  Good Rod (rarer & higher level)",
                                              "← Cancel"])
            if rod_choice == 2:
                return
            rod_name = "Good Rod" if rod_choice == 1 else "Old Rod"
        elif has_good:
            rod_name = "Good Rod"
        else:
            rod_name = "Old Rod"

        fish_pool = FISH_GOOD_ROD.get(self.town, []) if rod_name == "Good Rod" \
                    else FISH_OLD_ROD.get(self.town, [])
        if not fish_pool:
            slow_print(f"  {C.GRAY}No fish for {rod_name} here.{C.RESET}")
            press_enter(); return

        clear()
        section(f"🎣  FISHING  —  {self.town}")
        slow_print(f"  You cast your {C.BOLD}{rod_name}{C.RESET} into the water...", 0.03)
        import time as _t; _t.sleep(0.6)

        player_c = self._pick_lead()
        if player_c is None: return

        badge_bonus = (len(self.badges) // 2) * 5
        fish_count = 0
        while True:
            # Bobber animation
            slow_print(f"\n  {C.CYAN}~ ~ ~ waiting for a bite... ~ ~ ~{C.RESET}", 0)
            _t.sleep(random.uniform(0.5, 1.2))

            roll = random.random()
            if roll < 0.15:
                slow_print(f"  {C.GRAY}Nothing biting... the water is calm.{C.RESET}")
                press_enter()
            else:
                # A bite!
                name, lo, hi = random.choice(fish_pool)
                lv = random.randint(lo + badge_bonus, hi + badge_bonus)
                wild = Creature(name, lv, is_player=False)
                slow_print(f"  {C.YELLOW}A wild {C.BOLD}{wild.name}{C.RESET}"
                           f"{C.YELLOW} took the hook! (Lv.{wild.level}){C.RESET}")
                press_enter()
                player_c = self._pick_lead(player_c)
                if player_c is None: break

                result, obj = run_battle(player_c, wild, self.inventory,
                                         self.team, wild=True, weather=None)
                if result == "win":
                    self.seen.add(wild.name)
                    self._count_battle()
                    self.award_exp(player_c, wild)
                    self.earn_money(max(wild.level * 15, 100))
                    alive_after = [c for c in self.team if c.is_alive()]
                    if alive_after and not player_c.is_alive():
                        player_c = alive_after[0]
                    fish_count += 1
                elif result == "caught":
                    self._count_battle()
                    captured = obj
                    self.seen.add(captured.name)
                    self.caught.add(captured.name)
                    if captured.held_item:
                        stolen = captured.held_item
                        self.inventory[stolen] = self.inventory.get(stolen, 0) + 1
                        captured.held_item = None
                        slow_print(f"  {C.YELLOW}★  {captured.name} was holding {stolen}!{C.RESET}")
                    if len(self.team) < 6:
                        self.team.append(captured)
                        slow_print(f"  {C.GREEN}★  {captured.name} joined your team!{C.RESET}")
                        self._check_achievement("first_catch")
                        self._check_achievement("first_fish")
                        self._check_pokedex_completion()
                        if len(self.team) == 6:
                            self._check_achievement("team_full")
                        # Offer nickname
                        slow_print(f"  {C.GRAY}Give {captured.name} a nickname? (blank to skip):{C.RESET}")
                        _nick = input("  > ").strip()[:10]
                        if _nick:
                            captured.nickname = _nick
                            slow_print(f"  {C.GREEN}Nicknamed {C.BOLD}{_nick}{C.RESET}{C.GREEN}!{C.RESET}")
                    else:
                        slow_print(f"  {C.YELLOW}Team full! {captured.name} was released.{C.RESET}")
                    press_enter()
                    fish_count += 1
                elif result == "lose":
                    slow_print(f"  {C.RED}Your creatures fainted! Heading back to town...{C.RESET}")
                    press_enter(); break

            # Ask to keep fishing
            cont_opts = ["🎣  Cast again", "← Leave fishing spot"]
            if self.inventory.get("Escape Rope", 0) > 0:
                cont_opts.insert(1, "🪢  Use Escape Rope (stop fishing)")
            keep = menu(f"  {C.GRAY}[{fish_count} catches]{C.RESET}", cont_opts)
            if keep != 0:
                if "Escape Rope" in cont_opts[keep] if keep < len(cont_opts) else False:
                    self.inventory["Escape Rope"] -= 1
                slow_print(f"  {C.CYAN}You reel in your line. {fish_count} catch(es) today.{C.RESET}")
                press_enter(); break

    # ── EXPLORE GROTTO ─────────────────────────
    def explore_grotto(self):
        """Enter the hidden grotto for this town, if one exists."""
        grotto = GROTTOS.get(self.town)
        if not grotto:
            slow_print(f"  {C.GRAY}No hidden grotto near {self.town}.{C.RESET}")
            press_enter(); return

        clear()
        section(f"🕳  {grotto['name'].upper()}")
        slow_print(f"  {C.GRAY}You slip through a hidden crevice and enter {grotto['name']}...{C.RESET}", 0.02)
        self._check_achievement("grotto_found")

        player_c = self._pick_lead()
        if player_c is None: return

        # Give grotto items (one random item from the pool)
        grotto_item = random.choice(grotto["items"])
        self.inventory[grotto_item] = self.inventory.get(grotto_item, 0) + 1
        slow_print(f"\n  {C.YELLOW}✦  You find a {C.BOLD}{grotto_item}{C.RESET}"
                   f"{C.YELLOW} tucked in the corner!{C.RESET}")
        press_enter()

        # Grotto creature encounters (2-4 fights, each optional)
        creature_pool = grotto["creatures"]
        max_encounters = random.randint(2, 4)
        encounters_done = 0
        badge_bonus = (len(self.badges) // 2) * 5

        while encounters_done < max_encounters:
            clear()
            section(f"🕳  {grotto['name']}")
            alive_hp = "  ".join(
                f"{C.BOLD}{c.name}{C.RESET} {hp_bar(c.hp, c.max_hp, 10)}"
                for c in self.team if c.is_alive()
            )
            if alive_hp:
                print(f"  {alive_hp}\n")

            opts = ["🔦  Venture deeper", "← Leave grotto"]
            go = menu("", opts)
            if go == 1:
                break

            # Encounter
            name, lo, hi = random.choice(creature_pool)
            lv = random.randint(lo + badge_bonus, hi + badge_bonus)
            wild = Creature(name, lv, is_player=False)
            slow_print(f"\n  {C.YELLOW}A wild {C.BOLD}{wild.name}{C.RESET}"
                       f"{C.YELLOW} leaps from the shadows! (Lv.{wild.level}){C.RESET}")
            press_enter()
            player_c = self._pick_lead(player_c)
            if player_c is None: break

            result, obj = run_battle(player_c, wild, self.inventory,
                                     self.team, wild=True, weather=None)
            if result == "win":
                self.seen.add(wild.name)
                self._count_battle()
                self.award_exp(player_c, wild)
                self.earn_money(max(wild.level * 15, 100))
                alive_after = [c for c in self.team if c.is_alive()]
                if alive_after and not player_c.is_alive():
                    player_c = alive_after[0]
            elif result == "caught":
                self._count_battle()
                captured = obj
                self.seen.add(captured.name)
                self.caught.add(captured.name)
                if captured.held_item:
                    stolen = captured.held_item
                    self.inventory[stolen] = self.inventory.get(stolen, 0) + 1
                    captured.held_item = None
                    slow_print(f"  {C.YELLOW}★  {captured.name} was holding {stolen}!{C.RESET}")
                if len(self.team) < 6:
                    self.team.append(captured)
                    slow_print(f"  {C.GREEN}★  {captured.name} joined your team!{C.RESET}")
                    self._check_achievement("first_catch")
                    self._check_pokedex_completion()
                    if len(self.team) == 6:
                        self._check_achievement("team_full")
                    # Offer nickname
                    slow_print(f"  {C.GRAY}Give {captured.name} a nickname? (blank to skip):{C.RESET}")
                    _nick = input("  > ").strip()[:10]
                    if _nick:
                        captured.nickname = _nick
                        slow_print(f"  {C.GREEN}Nicknamed {C.BOLD}{_nick}{C.RESET}{C.GREEN}!{C.RESET}")
                else:
                    slow_print(f"  {C.YELLOW}Team full! {captured.name} was released.{C.RESET}")
                press_enter()
            elif result == "lose":
                slow_print(f"  {C.RED}You were driven out of the grotto!{C.RESET}")
                press_enter(); break

            encounters_done += 1

            # Bonus item every 2nd encounter
            if encounters_done % 2 == 0 and encounters_done < max_encounters:
                bonus = random.choice(grotto["items"])
                self.inventory[bonus] = self.inventory.get(bonus, 0) + 1
                slow_print(f"  {C.CYAN}✦  You spot another {bonus} as you move deeper!{C.RESET}")
                press_enter()

        slow_print(f"  {C.CYAN}You emerge from {grotto['name']}.{C.RESET}")
        press_enter()

    # ── TOWN LOOP ──────────────────────────────

    def town_loop(self):
        while True:
            town_data = TOWNS[self.town]
            clear()
            banner(f"  {self.town}  ")
            slow_print(f"  {C.GRAY}{town_data['desc']}{C.RESET}", 0.01)

            # Revisit flavor text — show a short quote when the player has been here before
            if self.town in self.visited_towns:
                gym_badge = (town_data.get("gym") or {}).get("badge")
                gym_beaten = gym_badge and gym_badge in self.badges
                quotes = TOWN_REVISIT_QUOTES.get(self.town)
                if quotes:
                    quote = quotes[0] if gym_beaten and quotes[0] else quotes[1]
                    if quote:
                        slow_print(f"  {C.CYAN}✦  {quote}{C.RESET}", 0.01)
            else:
                self.visited_towns.add(self.town)

            # Day/Night display
            tod, tod_color, tod_icon = time_of_day()
            alive_count = sum(1 for c in self.team if c.is_alive())
            print(f"\n  {C.YELLOW}₽{self.money}{C.RESET}  │  "
                  f"Badges {C.YELLOW}{len(self.badges)}{C.RESET}/{len(REQUIRED_BADGES)}  │  "
                  f"Team {C.GREEN}{alive_count}{C.RESET}/{len(self.team)} alive  │  "
                  f"{tod_color}{tod_icon} {tod}{C.RESET}\n")

            opts = []
            if town_data.get("shop"):
                opts.append("🛒  Shop")
            if town_data.get("inn"):
                opts.append(f"🏨  Inn  (₽{town_data['inn']} — full heal)")
            if town_data.get("gym"):
                badge = town_data["gym"]["badge"]
                tag   = f" {C.GREEN}[✓]{C.RESET}" if badge in self.badges else ""
                opts.append(f"⚔  Gym — {town_data['gym']['leader']}{tag}")
            if town_data.get("wild_area"):
                opts.append(f"🌿  Explore {town_data['wild_area']}")
            if FISH_OLD_ROD.get(self.town) or FISH_GOOD_ROD.get(self.town):
                opts.append("🎣  Go Fishing")
            if GROTTOS.get(self.town):
                opts.append("🕳  Hidden Grotto")
            if self.town == "Champion Road":
                opts.append("🏆  Elite Four Rematch" if getattr(self, 'is_champion', False)
                            else "🏆  Challenge Elite Four")
            # Show rival battle option if one is pending in this town
            from engine.rival import RIVAL_ENCOUNTERS
            pending_enc = self.rival.next_encounter(len(self.badges))
            if pending_enc and pending_enc["trigger_town"] == self.town:
                opts.append(f"⚡  Rival Battle ({self.rival.name})")
            elif (getattr(self, 'is_champion', False) and self.town == "Champion Road"
                  and getattr(self.rival, 'starter', None)):
                opts.append(f"⚡  Rival Rematch ({self.rival.name})")
            if self.town in MOVE_TUTORS:
                opts.append("🎓  Move Tutor")

            opts += [f"🗺  Travel to {c}" for c in town_data["connections"]]
            opts += [
                "🎒  Bag",
                "👥  Creatures",
                "📖  Pokédex",
                "🏅  Badges",
                "📊  Trainer Card",
                "🗺  World Map",
                "💾  Save Game",
                "❌  Quit",
            ]

            choice = menu("What do you do?", opts)
            label  = opts[choice].split("  ", 1)[-1].strip()

            if label == "Shop":
                self.visit_shop(town_data["shop"], len(self.badges))
            elif label.startswith("Inn"):
                self.visit_inn(town_data["inn"])
            elif label.startswith("Gym"):
                self.challenge_gym(town_data["gym"])
            elif label.startswith("Explore"):
                self.explore(town_data["wild_area"])
            elif label == "Go Fishing":
                self.go_fishing()
            elif label == "Hidden Grotto":
                self.explore_grotto()
            elif label in ("Challenge Elite Four", "Elite Four Rematch"):
                self.challenge_elite_four()
            elif label.startswith("Rival Battle"):
                from engine.rival import RIVAL_ENCOUNTERS, run_rival_encounter
                pending_enc = self.rival.next_encounter(len(self.badges))
                if pending_enc:
                    run_rival_encounter(self, pending_enc)
            elif label.startswith("Rival Rematch"):
                from engine.rival import run_rival_rematch
                run_rival_rematch(self)
            elif label == "Move Tutor":
                self.visit_move_tutor(self.town)
            elif label.startswith("Travel to"):
                dest = label.replace("Travel to ", "")
                slow_print(f"  {C.CYAN}You travel to {dest}...{C.RESET}", 0.02)
                time.sleep(0.3)
                self.town = dest
                press_enter()
                # Auto-trigger rival if they're waiting in this town
                trigger_rival_if_due(self)
            elif label == "Bag":
                self.open_bag()
            elif label == "Creatures":
                self.open_creatures()
            elif label == "Pokédex":
                self.open_pokedex()
            elif label == "Badges":
                self.open_badges()
            elif label == "Trainer Card":
                self.open_stats()
            elif label == "World Map":
                show_world_map(self.town, self.badges)
            elif label == "Save Game":
                self.save(); press_enter()
            elif label == "Quit":
                if confirm("  Save before quitting?"):
                    self.save()
                slow_print("  Goodbye, trainer!"); sys.exit(0)


# ═══════════════════════════════════════════════
#  NEW GAME
# ═══════════════════════════════════════════════
def new_game(g):
    clear()
    banner("  CREATURES  —  A NEW ADVENTURE  ", C.CYAN)
    slow_print("""
  Welcome to the world of CREATURES!

  Wild creatures roam every corner of this land.
  Catch them, train them, and battle your way to the top!

  Tips:
    ✦  Visit the INN in towns to heal your full team
    ✦  Switch creatures mid-battle from the menu
    ✦  All alive teammates share EXP after battle
    ✦  Catch creatures to build a strong team (max 6)
    ✦  You need all 7 Gym Badges to enter the Elite Four
    ✦  Give Berries (from Bag → Held Items) for passive bonuses
    ✦  Visit Move Tutors in towns to learn powerful moves
    ✦  Search thoroughly — some areas hide free items!
""", 0.012)
    press_enter()

    name = ""
    while not name:
        name = input(f"  {C.CYAN}Enter your trainer name:{C.RESET} ").strip()
    g.player_name = name

    # ── Avatar / gender ──
    print()
    slow_print(f"  {C.CYAN}Choose your trainer avatar:{C.RESET}")
    avatar_opts = ["♂  (Male)", "♀  (Female)", "⚧  (Other)"]
    av_idx = menu("", avatar_opts)
    g.avatar = ["♂", "♀", "⚧"][av_idx]

    # ── Nuzlocke mode ──
    print()
    slow_print(f"  {C.YELLOW}━━━  CHALLENGE MODE  ━━━{C.RESET}")
    slow_print(f"  {C.RED}⚠  Nuzlocke:{C.RESET} If a creature faints, it is {C.BOLD}permanently lost{C.RESET}.")
    slow_print(f"  {C.GRAY}Only for experienced trainers. This cannot be undone.{C.RESET}")
    nuz_choice = menu("Enable Nuzlocke mode?", ["No  (normal game)", "Yes  (Nuzlocke — creatures die forever)"])
    g.nuzlocke = (nuz_choice == 1)
    if g.nuzlocke:
        slow_print(f"  {C.RED}⚠  Nuzlocke mode ON. Every battle matters.{C.RESET}")
    else:
        slow_print(f"  {C.GREEN}Normal mode. Fainted creatures can be revived.{C.RESET}")

    # ── Rival name ──
    print()
    rival_name = input(f"  {C.YELLOW}Enter your rival's name (default: Gary):{C.RESET} ").strip()
    g.rival.name = rival_name if rival_name else "Gary"

    clear()
    section("CHOOSE YOUR STARTER")
    slow_print("  Four creatures await their trainer...\n")
    starters = ["Flambit", "Leafling", "Aquapup", "Drakling"]
    for s in starters:
        d = CREATURES[s]
        t = "/".join(d["type"])
        print(f"  {C.BOLD}{s:<12}{C.RESET} [{C.CYAN}{t:<15}{C.RESET}]  "
              f"{C.GRAY}{d['desc']}{C.RESET}")
    print()
    opts = [f"{s}  [{'/'.join(CREATURES[s]['type'])}]" for s in starters]
    idx  = menu("Your starter:", opts)
    starter_name = starters[idx]
    starter = Creature(starter_name, 5)
    g.team.append(starter)
    slow_print(f"\n  {C.GREEN}★  You chose {C.BOLD}{starter_name}{C.RESET}{C.GREEN}!{C.RESET}")
    slow_print(f"  {C.GRAY}Professor Birch: «Take good care of it, {g.player_name}!»{C.RESET}")

    # ── Rival picks counter-starter ──
    g.rival.starter = COUNTER_STARTER.get(starter_name, "Flambit")
    slow_print(f"\n  {C.CYAN}{g.rival.name} chose {C.BOLD}{g.rival.starter}{C.RESET}"
               f"{C.CYAN} — your rival has entered the adventure!{C.RESET}")
    press_enter()


# ═══════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════
def main():
    clear()
    banner("  ✦  CREATURES  ✦  ", C.MAGENTA)
    print(f"""
{C.CYAN}     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗   ██╗██████╗ ███████╗
    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝
    ██║     ██████╔╝█████╗  ███████║   ██║   ██║   ██║██████╔╝█████╗
    ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║   ██║██╔══██╗██╔══╝
    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗
     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝{C.RESET}
    """)

    g     = Game()
    slots = list_save_slots()

    opts = ["New Game"]
    if slots:
        for slot_num, summary in slots:
            opts.insert(0, f"Continue Slot {slot_num}  ({summary})")
    opts.append("Quit")
    choice = menu("", opts)

    if opts[choice] == "Quit":
        sys.exit(0)
    elif opts[choice] == "New Game":
        # Pick save slot
        if slots:
            slot_opts = [f"Slot {s}  ({summary})" for s, summary in slots]
            slot_opts += [f"Slot {s}  (empty)" for s in range(1, 4)
                          if s not in [x[0] for x in slots]]
            slot_opts.append("← Cancel")
            si = menu("Save to which slot?", slot_opts)
            if si == len(slot_opts) - 1:
                main(); return
            # Parse slot number
            raw = slot_opts[si]
            g.save_slot = int(raw.split()[1])
        new_game(g)
    else:
        # Continue — find slot number from label
        label = opts[choice]
        slot_num = int(label.split()[2])
        saved = load_game(slot=slot_num)
        if not saved:
            slow_print(f"  {C.RED}Save file not found!{C.RESET}")
            press_enter(); main(); return
        g.save_slot   = slot_num
        g.player_name = saved["player_name"]
        g.town        = saved["town"]
        g.team        = saved["team"]
        g.inventory   = {k: 0 for k in ITEMS}
        for k, v in saved["inventory"].items():
            if k in g.inventory:
                g.inventory[k] = v
        g.badges      = saved["badges"]
        g.money       = saved["money"]
        g.steps       = saved.get("steps", 0)
        g.play_seconds = saved.get("play_seconds", 0)
        g._session_start = time.time()   # start fresh timer for this session
        g.achievements = saved.get("achievements", [])
        g.season      = saved.get("season", "Spring")
        g.seen        = set(saved.get("seen", []))
        g.caught      = set(saved.get("caught", []))
        g.is_champion = saved.get("is_champion", False)
        g.avatar      = saved.get("avatar", "♂")
        g.visited_towns = set(saved.get("visited_towns", []))
        g.nuzlocke    = saved.get("nuzlocke", False)
        g.repel_steps = saved.get("repel_steps", 0)
        g._defeated_trainers = set(saved.get("defeated_trainers", []))
        # Load rival state
        from engine.rival import RivalState
        rival_data = saved.get("rival")

        rival_data = saved.get("rival")
        if rival_data:
            g.rival = RivalState.from_dict(rival_data)
        slow_print(f"  {C.GREEN}Welcome back, {C.BOLD}{g.player_name}{C.RESET}{C.GREEN}!{C.RESET}")
        press_enter()

    g.town_loop()


if __name__ == "__main__":
    main()
