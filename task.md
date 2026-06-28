# Pokepy Task List

## Status legend
todo / in-progress / done / tested / blocked

## Session 1 — Audit (2025-06)
Fresh repo, single "initial commit". All files compile and import cleanly.
Game is structurally complete (battle, gyms, Elite Four, rival, held items, abilities, save/load).

### Bugs found during audit — all resolved

- [x] **Save omits achievements + season** — status: done (commit e75f454)
- [x] **`battle100` achievement fires on wrong condition** — status: done (commit e75f454)
- [x] **Achievement triggers missing** — status: done (commit c9ed4ea)
- [x] **Fishing has no UI** — status: done (commit a6dcf09)
- [x] **Grottos have no UI** — status: done (commit a6dcf09)
- [x] **Seasonal wilds/berries unused** — status: done (commit 05c50c1)
- [x] **Achievements not saved/loaded** — status: done (commit e75f454)

---

## Tasks — planned features / improvements

- [x] **Move PP display in battle** — status: done
  - Already implemented at battle.py line 1032: shows `PP cur/max` next to each move in the fight menu.

- [x] **Enemy HP bar shows number** — status: done
  - `hp_bar()` in display.py returns `hp/max_hp` numerically; both sides use creature_card → hp_bar.

- [x] **Nature system** — status: done (commit 034b431)
  - 25 natures each give +10% to one stat and -10% to another (5 neutral).
  - Applied in `_calc_stat`, persisted via `to_dict`/`from_dict`, shown in creature card, detail screen (▲/▼ markers on stat table), and in-battle 📊 Stats view.

- [x] **Critical hit flash** — status: done (commit b5613b5)
  - "Critical hit!" now shown as a bold red banner on its own line instead of inline.

- [x] **Pokédex / creature registry** — status: done
  - `Game.seen`/`Game.caught` sets, save/load wiring, `_check_pokedex_completion`, and full
    `open_pokedex()` display method. `📖  Pokédex` option wired into town menu.

- [x] **Pokédex completion reward** — status: done
  - `_check_pokedex_completion()` grants a free Master Ball + fires `pokedex_complete` achievement.

- [x] **In-battle X-item use** — status: done
  - X Attack/Defense/Sp.Atk/Sp.Def wired. Fixed silent bug: X Speed now correctly threads
    `_xspd_boost` into `effective_spd()` for turn-order comparisons.

- [x] **Post-game content** — status: done
  - `is_champion` flag, Champion achievement, ★ Champion ★ on Trainer Card.
  - Elite Four Rematch at lv70+ once champion.

- [x] **Pokédex entry detail view** — status: done
  - Selectable entries open `_show_pokedex_entry()`: types/desc always; stats/ability/evo if caught.

- [x] **Rival rematch / extended post-game** — status: done (commit a2f510a)
  - `run_rival_rematch()` in engine/rival.py, repeatable at Champion Road, lv70+ scaled.

- [x] **Battle log / replay** — status: done (commit 0457750)
  - `BATTLE_LOG` deque in display.py; `📜  Log` option in battle menu shows last 15 lines pageable.

- [x] **Trainer Card gender / avatar** — status: done (commit 19a4bed)
  - ♂/♀/⚧ choice at new game, shown on Trainer Card, saved/loaded.

- [x] **Sound / terminal bell on key events** — status: done (commit fa9ed8d)
  - `print('\a')` on catch (battle.py), level-up, evolution, and badge earned (main.py).

- [x] **Consumable item descriptions in battle Bag** — status: done (commit e7aee4d)
  - battle.py line 1077: `bag_opts` built with `ITEMS[item]['desc']` inline.

- [x] **Move description tooltip in fight menu** — status: done (commit e7aee4d)
  - battle.py line 1049: move `desc` shown on a sub-line below each move in fight menu.

- [x] **Held item display on enemy creature card** — status: done
  - display.py `creature_card()` already shows `held_item` for all creatures (friend and foe).
  - Wild creatures get items from `held_item_pool`; shown as `[ItemName]` on their card.

- [x] **Move learning choice — "Don't learn" UX** — status: done
  - Explicit "Don't learn <move>" option present at all 3 learn-move call sites in main.py.
  - Full move stats (type, power, PP, desc) shown for both the new and existing moves.

- [x] **Wild area creature level scaling by badge count** — status: done (commit f8cd728)
  - `badge_bonus = (len(self.badges) // 2) * 5`: +5 per 2 badges (max +17 at 7 badges).
  - Applied to wild encounters, seasonal encounters, override pools, and random trainer teams.
  - `random_wild()` in core.py accepts `badge_bonus` kwarg.

- [x] **Town revisit flavor text** — status: done (commit f8cd728)
  - `TOWN_REVISIT_QUOTES` dict in main.py: gym-beaten quote and general-revisit quote per town.
  - `Game.visited_towns` set tracks first visits; flavor line shown on subsequent entries.
  - `visited_towns` saved/loaded via `save_game`/`load_game` (core.py updated).

---

## New tasks — todo

- [ ] **Catch rate feedback in battle** — status: todo
  - When a capture ball breaks free, show how close it was ("Almost had it! 3 shakes" vs "It
    escaped immediately"). Currently always generic "broke free". The `shakes` count is already
    returned by `animated_capture()` — just display it as flavor text.

- [ ] **Shop stock scales with badge count** — status: todo
  - Early shops only sell Potions and Capture Balls. Later shops unlock better items but only if
    you travel there. Make shops in earlier towns progressively stock better items as you earn
    badges (e.g. Great Ball unlocks at badge 2, Super Potion at badge 1). Improves pacing.

- [ ] **Trainer Card: playtime display** — status: todo
  - The Trainer Card tracks `self.steps` (battle count) but not real playtime. Add a
    `play_seconds` int to Game that is incremented on save and shown on the Trainer Card as
    "Playtime: Xh Ym". Simple and adds a nice personal stat.

- [ ] **Nuzlocke / challenge mode flag** — status: todo
  - Add an optional "Nuzlocke" mode toggle at new-game: if enabled, any creature that faints is
    permanently removed from the team (deleted, not just fainted). Show a dramatic death message.
    Stored as `Game.nuzlocke: bool`, checked after every battle loss in `award_exp`.

- [ ] **Creature nickname system** — status: todo
  - After catching a wild creature, offer the player the option to give it a nickname (short
    string, ≤10 chars). Store as `Creature.nickname`; display nickname (if set) in battle and
    menus instead of species name, with species in parentheses. Save/load via `to_dict`/`from_dict`.

- [ ] **Battle weather visual enhancement** — status: todo
  - Weather is shown as a single line at battle start but never again unless the player looks.
    Print a brief weather reminder line at the start of each turn (e.g. "☀ Sunny boosts Fire
    moves!") so players remember it's active. Only show when weather is non-None.

- [ ] **Move type color in fight menu** — status: todo
  - The fight menu shows move name, PP, power, and desc — but the move's type is not color-coded.
    Use the existing `TYPE_COLORS` dict from display.py to tint the type tag next to each move
    name in the fight menu. Purely visual, zero gameplay impact.

- [ ] **Inn "heal preview" before paying** — status: todo
  - Currently the Inn shows the team summary, asks for payment confirmation, then heals. Add a
    per-creature preview of how much HP/PP each will recover before the player confirms payment,
    so they can make an informed choice (e.g. if everything is already full, they see that).

- [ ] **Evolution Stone items** — status: todo
  - Add Fire Stone, Water Stone, Leaf Stone, Thunder Stone to the ITEMS dict. Some creatures
    (e.g. Flambit → Flamclaw, Aquapup → Tidalfin) gain an alternate evolution path triggered by
    using the stone from the Bag. Define which creatures accept which stone in CREATURES data.
    Implement stone-use in `open_bag()` → calls `creature.evolve()`.

- [ ] **Creature sorting in team view** — status: todo
  - The Creatures menu lists team members in the order they were caught. Add a sort option:
    "Sort by Level", "Sort by HP %", "Sort by Name". Useful for quickly finding the right
    creature in a large team.
