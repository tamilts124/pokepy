# ═══════════════════════════════════════════════════════════
#  RIVAL SYSTEM
#  A rival trainer who grows alongside the player, battling
#  at five key story moments with escalating teams & taunts.
# ═══════════════════════════════════════════════════════════

import time
from engine.core import Creature
from ui.display  import (C, clear, slow_print, banner, section,
                          team_summary, press_enter, confirm)
from engine.battle import run_battle

# ─────────────────────────────────────────────────────────
#  RIVAL STARTER SELECTION
#  Rival always picks the starter that's strong against yours
# ─────────────────────────────────────────────────────────
COUNTER_STARTER = {
    "Flambit":  "Aquapup",   # water beats fire
    "Leafling": "Flambit",   # fire beats grass
    "Aquapup":  "Leafling",  # grass beats water
    "Drakling": "Aquapup",   # water is safe vs dragon starter
}

# ─────────────────────────────────────────────────────────
#  RIVAL ENCOUNTER DEFINITIONS
#  trigger_badges: battle fires after the player has earned
#                  this many badges and travels to trigger_town.
#  Each encounter lists the rival's team as (name, level).
# ─────────────────────────────────────────────────────────
RIVAL_ENCOUNTERS = [
    # ── Encounter 0: Before 1st badge — rival boasts in Greenpath ──
    {
        "id": 0,
        "trigger_badges": 0,
        "trigger_town": "Greenpath",
        "phase": "early",
        "intro": [
            "Well, well… if it isn't {player}!",
            "I've already scouted this gym. Fern's Leafling is grass-type.",
            "My {rival_starter} will tear right through it.",
            "You'd better hope you can keep up with me!",
        ],
        "win_lines": [
            "N-no way… I was distracted, that's all.",
            "Next time I won't go easy on you, {player}.",
        ],
        "lose_lines": [
            "Ha! I knew you were still a rookie.",
            "Come back when you're actually a challenge.",
        ],
        # Team is built dynamically in rival_team_for_encounter()
    },
    # ── Encounter 1: After badge 3, in Ashveil ──
    {
        "id": 1,
        "trigger_badges": 3,
        "trigger_town": "Ashveil",
        "phase": "mid_early",
        "intro": [
            "Three badges already, {player}? I'm impressed… barely.",
            "I've got three too, obviously. And my team is way stronger.",
            "Don't think you can just coast on luck forever.",
        ],
        "win_lines": [
            "Fine, fine. You got me this time.",
            "I'll be twice as strong next time we meet.",
        ],
        "lose_lines": [
            "You're still behind me. Don't forget that.",
            "Keep grinding, {player}. You'll need it.",
        ],
    },
    # ── Encounter 2: After badge 5, in Mistveil ──
    {
        "id": 2,
        "trigger_badges": 5,
        "trigger_town": "Mistveil",
        "phase": "mid",
        "intro": [
            "Five badges… I have to admit, you're for real.",
            "I've been training non-stop since our last battle.",
            "{player}, this fight is going to be different.",
            "I need to know — which of us is truly stronger?",
        ],
        "win_lines": [
            "…You've grown. I wasn't expecting that.",
            "I need to push harder. I won't let this slide.",
        ],
        "lose_lines": [
            "I'm stronger. Remember that when you reach the Elite Four.",
            "You've gotten better, {player}. But I'm still ahead.",
        ],
    },
    # ── Encounter 3: After badge 7, at Champion Road entrance ──
    {
        "id": 3,
        "trigger_badges": 7,
        "trigger_town": "Champion Road",
        "phase": "late",
        "intro": [
            "Seven badges. You and me, side by side. I never thought it'd come to this.",
            "I won't hold back, {player}. Not even a little.",
            "One of us walks through that gate first. Let's settle this.",
        ],
        "win_lines": [
            "…",
            "You're the real deal, {player}. I respect that.",
            "Go win it. And if you don't, I'll never let you forget it.",
        ],
        "lose_lines": [
            "See you on the other side of the Elite Four.",
            "I'll get there first. Count on it.",
        ],
    },
    # ── Encounter 4: Final rival battle — AFTER the Elite Four ──
    {
        "id": 4,
        "trigger_badges": 99,   # special trigger — set by code after Elite Four
        "trigger_town":  "__post_elite__",
        "phase": "final",
        "intro": [
            "You actually did it.",
            "Champion {player}… That sounds strange, but right.",
            "I've been waiting here. I knew you'd make it.",
            "One last time. No titles, no excuses.",
            "Just you, me, and everything we've worked for.",
        ],
        "win_lines": [
            "Ha… of course.",
            "You beat the Elite Four AND you beat me.",
            "I don't know whether to be angry or proud.",
            "…Probably proud.",
            "Don't you dare forget where you started, {player}.",
        ],
        "lose_lines": [
            "I won. But you made me work for every second of it.",
            "You're a Champion. Don't let anyone tell you otherwise.",
            "Go rest. You've earned it.",
        ],
    },
]

# ─────────────────────────────────────────────────────────
#  RIVAL TEAM BUILDER
#  Scales dynamically with encounter phase and starter choice
# ─────────────────────────────────────────────────────────
def rival_team_for_encounter(rival_starter, encounter_id, rival_wins):
    """
    Returns a list of (creature_name, level) for the rival's team.
    rival_starter: the rival's starter creature name
    encounter_id:  which of the 5 encounters (0–4)
    rival_wins:    how many times rival has beaten the player (affects bonus creature level)
    """
    # Rival's starter evolves through the game
    STARTER_EVOLUTIONS = {
        "Flambit":  [("Flambit", 10), ("Flamclaw", 25), ("Flamclaw", 35),
                     ("Infernox", 46), ("Infernox", 58)],
        "Leafling": [("Leafling", 10), ("Thornbush", 25), ("Thornbush", 35),
                     ("Goliavine", 46), ("Goliavine", 58)],
        "Aquapup":  [("Aquapup", 10), ("Tidalfin", 25), ("Tidalfin", 35),
                     ("Abyssking", 46), ("Abyssking", 58)],
        "Drakling": [("Drakling", 10), ("Drakonis", 25), ("Drakonis", 35),
                     ("Wyrmax", 46), ("Wyrmax", 58)],
    }

    starter_stage = STARTER_EVOLUTIONS.get(rival_starter, [("Flambit", 10)])[encounter_id]
    boost = rival_wins  # each player-loss bumps rival's partner slightly

    teams = {
        0: [starter_stage, ("Buzzbee", 9)],
        1: [starter_stage, ("Sparkit", 22), ("Pebblur", 21)],
        2: [starter_stage, ("Voltfang", 33), ("Ghostlet", 31), ("Skywing", 30)],
        3: [starter_stage, ("Spectrex", 44), ("Stormcrest", 43),
            ("Ironclaw", 43), ("Drakonis", 45)],
        4: [starter_stage, ("Spectrex", 56), ("Stormcrest", 55),
            ("Ironclaw", 56), ("Wyrmax", 57), ("Glacivore", 55)],
    }

    raw = teams.get(encounter_id, [starter_stage])
    # Apply boost to non-starter mons
    boosted = [raw[0]] + [(name, lv + boost) for name, lv in raw[1:]]
    return boosted


# ─────────────────────────────────────────────────────────
#  RIVAL ART
# ─────────────────────────────────────────────────────────
RIVAL_ART_PHASES = {
    "early": f"""
{C.CYAN}    (ò_ó)/
   /|    |\\
   || ★  ||
   /\\    /\\{C.RESET}""",
    "mid_early": f"""
{C.CYAN}    (ó_ò)/
   /|    |\\
   ||★★  ||
   /\\    /\\{C.RESET}""",
    "mid": f"""
{C.CYAN}    (•_•)/
   /|    |\\
  [|★★★  |]
   /\\    /\\{C.RESET}""",
    "late": f"""
{C.YELLOW}    (◣_◢)/
   /|    |\\
  ███████
   /\\    /\\{C.RESET}""",
    "final": f"""
{C.MAGENTA}    (◕‿◕)/
   /|    |\\
  ╔═══════╗
  ║ RIVAL ║
  ╚═══════╝{C.RESET}""",
}


# ─────────────────────────────────────────────────────────
#  RIVAL STATE  (attached to Game object)
# ─────────────────────────────────────────────────────────
class RivalState:
    def __init__(self):
        self.name          = "Gary"
        self.starter       = None    # set during new_game()
        self.battles_done  = []      # list of encounter IDs completed
        self.rival_wins    = 0       # times rival beat the player
        self.player_wins   = 0       # times player beat the rival

    def to_dict(self):
        return {
            "name":         self.name,
            "starter":      self.starter,
            "battles_done": self.battles_done,
            "rival_wins":   self.rival_wins,
            "player_wins":  self.player_wins,
        }

    @classmethod
    def from_dict(cls, d):
        rs = cls()
        rs.name         = d.get("name", "Gary")
        rs.starter      = d.get("starter")
        rs.battles_done = d.get("battles_done", [])
        rs.rival_wins   = d.get("rival_wins", 0)
        rs.player_wins  = d.get("player_wins", 0)
        return rs

    def next_encounter(self, badge_count):
        """Return the next RIVAL_ENCOUNTERS entry that should fire, or None."""
        for enc in RIVAL_ENCOUNTERS:
            if enc["id"] in self.battles_done:
                continue
            if enc["trigger_badges"] == 99:
                continue   # post-elite — triggered manually
            if badge_count >= enc["trigger_badges"]:
                return enc
        return None


# ─────────────────────────────────────────────────────────
#  RIVAL ENCOUNTER SCENE
# ─────────────────────────────────────────────────────────
def _fmt(text, player, rival):
    return text.replace("{player}", player).replace("{rival_starter}", rival.starter or "rival")

def run_rival_encounter(game, encounter):
    """
    Show the rival intro, fight their team, handle win/loss,
    print outro. Updates rival state. Returns "win" | "lose".
    """
    rival  = game.rival
    enc_id = encounter["id"]
    phase  = encounter.get("phase", "early")

    clear()
    banner(f"  ★  RIVAL  {rival.name.upper()}  ★  ", C.MAGENTA)
    art = RIVAL_ART_PHASES.get(phase, RIVAL_ART_PHASES["early"])
    print(art)

    # Score line
    score_tag = (f"  {C.YELLOW}[You {game.rival.player_wins}–{game.rival.rival_wins} "
                 f"{rival.name}]{C.RESET}")
    slow_print(score_tag)
    print()

    for line in encounter["intro"]:
        slow_print(f"  {C.BOLD}{rival.name}{C.RESET}: «{_fmt(line, game.player_name, rival)}»")
        time.sleep(0.25)
    press_enter()

    # Build rival team
    rival_team_spec = rival_team_for_encounter(rival.starter, enc_id, rival.rival_wins)

    # Player picks lead
    alive = [c for c in game.team if c.is_alive()]
    if not alive:
        slow_print(f"  {C.RED}All your creatures fainted! Visit an Inn first.{C.RESET}")
        press_enter()
        return "skipped"

    from ui.display import menu, hp_bar
    opts = [f"{c.name} Lv.{c.level}  {hp_bar(c.hp, c.max_hp, 12)}" for c in alive]
    idx  = menu("Lead with which creature?", opts)
    player_c = alive[idx]

    battle_result = "win"
    for cname, lv in rival_team_spec:
        enemy = Creature(cname, lv, is_player=False)
        result, obj = run_battle(player_c, enemy, game.inventory,
                                 game.team, wild=False,
                                 trainer_name=rival.name)
        if result == "win":
            game.steps += 1
            game.award_exp(player_c, enemy)
            alive_after = [c for c in game.team if c.is_alive()]
            if alive_after and not player_c.is_alive():
                player_c = alive_after[0]
        elif result == "lose":
            battle_result = "lose"
            break

    # Outro
    clear()
    banner(f"  ★  RIVAL  {rival.name.upper()}  ★  ", C.MAGENTA)
    print(art)

    if battle_result == "win":
        rival.player_wins += 1
        if rival.player_wins >= 3:
            game._check_achievement("rival_winner")
        prize = enc_id * 500 + 500
        game.earn_money(prize)

        for line in encounter["win_lines"]:
            slow_print(f"  {C.BOLD}{rival.name}{C.RESET}: «{_fmt(line, game.player_name, rival)}»")
            time.sleep(0.2)
    else:
        rival.rival_wins += 1
        slow_print(f"\n  {C.RED}You lost to {rival.name}...{C.RESET}")
        for line in encounter["lose_lines"]:
            slow_print(f"  {C.BOLD}{rival.name}{C.RESET}: «{_fmt(line, game.player_name, rival)}»")
            time.sleep(0.2)

    rival.battles_done.append(enc_id)
    print()
    slow_print(f"  {C.YELLOW}[Score: You {rival.player_wins}–{rival.rival_wins} {rival.name}]{C.RESET}")
    press_enter()

    game.save()
    return battle_result


def trigger_rival_if_due(game):
    """
    Call this each time the player enters a town.
    If a rival encounter is due (badge count + town match), fire it.
    """
    if not hasattr(game, "rival") or game.rival.starter is None:
        return

    enc = game.rival.next_encounter(len(game.badges))
    if enc is None:
        return
    if enc["trigger_town"] != game.town:
        return

    run_rival_encounter(game, enc)


def trigger_post_elite_rival(game):
    """
    Called manually after beating the Elite Four.
    Fires the final rival encounter (id == 4).
    """
    if not hasattr(game, "rival") or game.rival.starter is None:
        return
    final_enc = next((e for e in RIVAL_ENCOUNTERS if e["id"] == 4), None)
    if final_enc and 4 not in game.rival.battles_done:
        run_rival_encounter(game, final_enc)
