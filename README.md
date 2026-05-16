# Creatures — A Terminal RPG

> **Catch, train, and battle your way to the championship — entirely in your terminal.**

A fully-featured Pokémon-inspired RPG built in Python. No GUI, no dependencies beyond the standard library. ANSI colour, animated text, a hand-crafted world map, 5-encounter rival story, weather system, held items, abilities, and a full Elite Four — all running in your command prompt.

---

## Features

**World & exploration**
- 10 interconnected towns across a hand-drawn ASCII world map
- 7 gyms, each with a unique leader, type specialty, and story quote
- Wild areas with day/night bonuses (ghost-types appear more at night)
- Seasonal weather that shifts every 7 days and affects move power
- Hidden item finds, random trainer encounters, and hidden grottos while exploring

**Battle system**
- Speed-based turn order with priority moves (Quick Attack always goes first)
- Physical / Special split — each move uses the correct attacking and defending stat
- Full stat stages (−6 to +6) for Attack, Defense, Sp. Atk, Sp. Def, Speed, Accuracy
- 6 status conditions: Poison, Burn, Paralysis, Sleep, Freeze, Confusion
- Type effectiveness chart with super-effective, resisted, and immune matchups
- Critical hits, accuracy checks, and miss chance
- Multi-hit moves (2–5 hits), two-turn charge moves, and Leech drain
- Weather modifiers: Sunny, Rainy, Sandstorm, Hail — each boost or suppress move types and deal end-of-turn chip damage
- Post-battle summary (damage dealt/taken, turns, items used, switches)

**Held items**
- Berries (Lum, Sitrus, Oran, Salac, Petaya, Apicot, Ganlon) — one-use, auto-trigger on condition
- Combat items: Life Orb (+30% damage, recoil), Choice Band (+50% Atk, move-lock), Leftovers (EOT heal), Shell Bell (drain on hit), Scope Lens (double crit chance)

**Abilities**
- Blaze / Overgrow / Torrent — starter abilities that trigger at low HP
- Intimidate — lowers foe Attack on entry
- Thick Fat, Dragon Skin, Rock Head — damage reduction
- Static, Poison Touch, Spore Cloud — retaliation proc on contact
- Levitate — full Ground immunity
- Swift Swim — doubles Speed in Rain
- Speed Boost — +1 Speed every end-of-turn
- Ice Body — heals in Hail
- Sturdy — survive a one-hit KO at full HP (once per switch-in)

**Progression**
- Catch wild creatures with Capture Ball, Great Ball, Ultra Ball, or Master Ball
- Shared EXP: all living bench members gain split experience after battle
- Level-up with stat recalculation, new move learning, and optional evolution
- Move replacement UI when a creature already knows 4 moves
- Move Tutors in 6 towns — spend money to teach powerful techniques
- Rare Candy support (from bag or item menu)
- 3-slot save system with per-slot summaries

**Rival system**
- Name your rival at the start; they pick the counter-starter to yours
- 5 scripted encounters with escalating teams, unique dialogue, and ASCII art
- Rival score tracked across the whole game (You X–Y Rival)
- Final battle unlocks after completing the Elite Four

**Quality of life**
- Full Bag, Creatures, Badges, and Trainer Card menus accessible from any town
- In-battle type-effectiveness hints on every move (▲▲ super, ▼ not very, ✗ immune)
- In-battle stat stage viewer (📊 Stats option)
- Team reorder and move reorder menus
- Held item assignment and take-back from the Creatures hub
- Auto-save after each gym badge and rival battle
- Achievement system (11 milestones)
- Inn for full team heal + PP restore

---

## Project structure

```
pokepy/
├── main.py              # Game loop, town logic, explore, gym, Elite Four
├── engine/
│   ├── core.py          # Creature class, damage calc, save/load, weather
│   ├── battle.py        # Battle loop, AI, abilities, held item triggers
│   └── rival.py         # Rival encounters, team scaling, story scenes
├── ui/
│   └── display.py       # ANSI colours, HP bars, menus, world map renderer
├── data/
│   └── creatures.py     # All creature data, moves, items, towns, wild pools
└── save_slot{1-3}.json  # Save files (auto-generated)
```

---

## Requirements

- Python 3.8 or higher
- A terminal with ANSI colour support
  - Windows: Windows Terminal or PowerShell (recommended); classic `cmd.exe` works but colours may vary
  - macOS / Linux: any standard terminal

No third-party packages required.

---

## Running the game

```bash
cd pokepy
python main.py
```

On first launch you will be prompted to enter your trainer name, your rival's name, and choose one of four starter creatures.

---

## Starters

| Name | Type | Ability | Evolves |
|---|---|---|---|
| Flambit | Fire | Blaze | → Flamclaw → Infernox |
| Leafling | Grass | Overgrow | → Thornbush → Goliavine |
| Aquapup | Water | Torrent | → Tidalfin → Abyssking |
| Drakling | Dragon | Dragon Skin | → Drakonis → Wyrmax |

Your rival always chooses the starter that is strong against yours.

---

## Gym order

| # | Town | Leader | Type | Badge |
|---|---|---|---|---|
| 1 | Greenpath | Fern | Grass | Leaf Badge |
| 2 | Stonepeak | Granite | Rock | Rock Badge |
| 3 | Ashveil | Cinder | Fire | Ember Badge |
| 4 | Frostholm | Blizara | Ice | Frost Badge |
| 5 | Mistveil | Myra | Psychic | Mystic Badge |
| 6 | Shadowmere | Umbra | Ghost | Shadow Badge |
| 7 | Dragonspire | Draven | Dragon | Dragon Badge |

Collect all 7 badges to challenge the Elite Four at Champion Road.

---

## Controls

The game is entirely menu-driven. Type the number of your choice and press Enter. In battle:

| Option | Description |
|---|---|
| ⚔ Fight | Choose a move. Type hints show effectiveness vs the foe. |
| 🎒 Bag | Use a healing item, capture ball, or PP restore. |
| 🔄 Switch | Swap to another creature on your team. |
| 📊 Stats | View current stat stages for both sides. |
| 🏃 Run | Attempt to flee (wild battles only; success scales with Speed). |

---

## Tips

- Visit the **Inn** in each town to fully heal your team and restore all PP.
- Give **Berries** to creatures as held items before tough battles — they trigger automatically.
- **Leftovers** on a bulky creature compounds fast: 1/16 max HP every end-of-turn.
- The **Move Tutor** in Dragonspire teaches Earthquake and Dragon Rage — worth the price.
- At **night** (9 PM – 6 AM local time), ghost-types appear more frequently in wild areas.
- Use **Escape Rope** to exit a wild area instantly without risking another encounter.
- Rival battles are triggered when you enter a specific town with enough badges — they don't expire, so you can heal first.

---

## Save files

Saves are written to `save_slot1.json`, `save_slot2.json`, and `save_slot3.json` in the project root. The game auto-saves after every gym badge and rival battle. You can also save manually from the town menu.

Save files are plain JSON and human-readable if you want to inspect them.

---

## License

MIT — do whatever you like with it.
