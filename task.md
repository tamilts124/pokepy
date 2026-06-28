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

## Session 2 — Verification audit (2026-06)

- [x] **Bug: instant crash on default Windows console (cp1252)** — status: done
  - Verified all "done" tasks against real code (compiled cleanly, no TODO/stub/conflict
    markers found) and confirmed working tree was clean / in sync with previous session.
  - Found via actual launch test: `UnicodeEncodeError` on the very first banner print
    (box-drawing + emoji characters) when stdout uses the legacy `cp1252` codepage that
    classic `cmd.exe` defaults to on Windows — game crashed before showing any menu, with
    no workaround short of manually running `chcp 65001` first. Not caught by any previous
    session because dev/testing happened in a UTF-8-capable terminal.
  - Fix: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` /
    `sys.stderr.reconfigure(...)` added at the very top of `main.py`, wrapped in try/except
    for safety. Re-verified: banner, town menu, and gym intro now render fully with no
    encoding crash under a simulated cp1252 environment; only remaining EOF stems from the
    test harness having no stdin attached, not from the game itself.

## New tasks — todo

- [x] **Catch rate feedback in battle** — status: done (commit a74d4b9)
  - When a capture ball breaks free, shake-count hints shown: 0/1/2/3 shakes each give distinct
    flavor text guiding the player on how close they were and what to try next.

- [x] **Shop stock scales with badge count** — status: done
  - `BADGE_BONUS_STOCK` list in `visit_shop()` defines badge thresholds for 13 items. On every
    shop visit, bonus items are merged into the town's base stock without duplicates. Result:
    returning to Greenpath with 3 badges shows Super Potion, Great Ball, Hyper Potion etc.
    Existing `BADGE_LOCKED` gating is preserved and still hides items from later towns too.

- [x] **Trainer Card: playtime display** — status: done
  - `play_seconds` field added to `Game`, `save_game()`, `load_game()`, and the load path in
    `main()`. Accumulated each save (session elapsed time). Old saves default to 0 gracefully.
    Trainer Card now shows "Playtime: Xh YYm" below Battles.

- [x] **Nuzlocke / challenge mode flag** — status: done
  - `Game.nuzlocke` bool added; toggled at new-game with a clear warning prompt.
  - `_nuzlocke_purge()` called at end of `award_exp()`: finds fainted creatures, prints a
    dramatic bordered death notice, permanently removes them from `self.team`.
  - If the last creature dies, game exits with a final message.
  - `nuzlocke` persisted via `save_game()`/`load_game()` with `setdefault(False)` for old saves.
  - Trainer Card shows `⚠ NUZLOCKE` mode banner when enabled.

- [x] **Creature nickname system** — status: done (commit 8721b95)
  - After catching a wild creature, offer the player the option to give it a nickname (short
    string, ≤10 chars). Store as `Creature.nickname`; display nickname (if set) in battle and
    menus instead of species name, with species in parentheses. Save/load via `to_dict`/`from_dict`.
  - Nickname prompt at all 3 catch sites (explore, fish, grotto). Rename option in Creatures menu.
    `_dname()` in battle.py, `creature_card()` in display.py, team list + detail banner in main.py all updated.

- [x] **Battle weather visual enhancement** — status: done (commit c887dde)
  - Brief weather reminder printed at the start of each turn when weather is active.

- [x] **Move type color in fight menu** — status: done (commit 353d438)
  - TYPE_COLORS applied to type tag next to move name in fight menu. Uppercase type label.

- [x] **Inn "heal preview" before paying** — status: done
  - `visit_inn()` now shows a per-creature preview table (HP gain, PP restore status, active
    status condition) before the payment confirmation. Tells the player exactly what they gain,
    and if the team is already full shows a special message with an optional "pay anyway" prompt.

- [x] **Evolution Stone items** — status: done
  - Added Fire Stone, Water Stone, Leaf Stone, Thunder Stone to `ITEMS` (type `"stone"`).
  - `stone_evolution` dict added to the 4 affected first-stage creatures: Flambit (Fire Stone
    → Flamclaw), Aquapup (Water Stone → Tidalfin), Leafling (Leaf Stone → Thornbush), Sparkit
    (Thunder Stone → Voltfang) — same target species as the normal level evolution, just usable
    early. All other creatures unaffected (`.get("stone_evolution", {})` defaults to empty).
  - Stone-use wired into `open_creatures()` → "Use item": shows a confirm prompt, calls
    `creature.evolve()` on yes, consumes the stone only if confirmed, fires the
    `first_evolution` achievement and terminal bell, matching the existing level-up evolution UX.
  - Stones added to both `NON_HOLDABLE` sets (can't be wasted as a held item) and to
    `BADGE_BONUS_STOCK` (purchasable in any shop from 2 badges onward) so the feature is
    actually reachable in a normal playthrough, not dead code.
  - Evolution hints shown in both the Creatures-menu detail card and the Pokédex entry view.
  - Verified: `py_compile` clean on all files; a scripted-stdin test drove the real
    `open_creatures()` UI end-to-end (pick creature → Use item → pick Fire Stone → confirm)
    and confirmed Flambit→Flamclaw, new move learned, stone consumed, achievement fired; a
    second run confirmed declining the prompt leaves the creature and stone untouched.
    Old-save compatibility confirmed via the existing `inventory` merge-by-key load path
    (missing stone keys default to 0).

- [x] **Evolution Stones for remaining elemental lines** — status: done (design decision: no new stones)
  - Investigated all 11 candidate lines (Ghostlet, Iceling, Drakling, Steelbit, Mudpup, Skywing,
    Venomfang, Psychling, Mushrump, Shellcrab, Ashpup) in `data/creatures.py`. None of them are
    pure Fire/Water/Grass/Electric — their types are Dragon, Steel, Ground/Water, Flying/Normal,
    Poison, Psychic, Grass/Poison, Water/Rock, Ghost, Ice. Reusing one of the 4 existing stones
    on any of them would be thematically wrong (e.g. a "Fire Stone" evolving the Dragon line
    makes no sense), so this isn't a copy-paste job — it would require 8-9 brand new stone
    items (Dragon/Steel/Ground/Flying/Poison/Psychic/Ghost/Ice/Rock Stone), each needing its own
    shop slot, `NON_HOLDABLE` entry, and Pokédex hint.
  - Decision: leave all 11 level-only. The 4 existing stones intentionally cover only the 3
    elemental starters (Flambit/Aquapup/Leafling) plus Sparkit, as an early-route "skip the
    wait" perk on lines the player meets first — not a universal mechanic. Doubling the item
    list with a stone per remaining type would dilute that rarity and bloat every shop's stock
    for marginal benefit, since all 11 lines already evolve at a reasonable level (20-28) with
    no level-gating complaints raised in testing. Revisit only if a future playthrough surfaces
    a specific line that feels like it evolves too late.

- [x] **Creature sorting in team view** — status: done
  - Added "🔃 Sort team" option to the Creatures menu alongside the existing "🔀 Reorder team".
    Sub-menu offers: Sort by Level (desc), Sort by HP % (least healthy first), Sort by Name (A→Z,
    respects nicknames). Implemented as `_sort_team_menu()` — sorts `self.team` in-place.

## Session 3 — Resume after mid-task cutoff (2026-06)

- [x] **Repel items** — status: done
  - Found this half-finished on session start: `git diff` showed uncommitted work adding
    Repel/Super Repel/Max Repel to `ITEMS`, a `Game.repel_steps` counter, the "repel" bag-use
    branch, and the wild-encounter intercept in `explore()` — but several integration points
    were missing, which would have made the feature unreachable or lossy in a real playthrough:
    - Repels were never added to any shop's stock or `BADGE_BONUS_STOCK`, so they could never
      actually be bought.
    - Repels were missing from both `NON_HOLDABLE` sets in `main.py`, so they could be wasted
      as a held item slot instead of a bag consumable.
    - `repel_steps` was not persisted — `save_game()`/`load_game()` in `engine/core.py` didn't
      accept/store/restore it, and the `Game.save()`/load-slot path in `main.py` didn't pass it
      through, so an active Repel would silently reset to 0 on save/reload.
  - Fixes applied: added Repel (1 badge), Super Repel (3 badges), Max Repel (5 badges) to
    `BADGE_BONUS_STOCK`; added all three to both `NON_HOLDABLE` sets; added `repel_steps`
    param to `save_game()`/`load_game()` (with `setdefault(0)` for old saves) and wired it
    through `Game.save()` and the continue-slot load path.
  - Verified: `py_compile` clean on all files. Built a scripted harness that monkeypatched
    `random.random`/`input`/`time.sleep` to drive `Game.explore()` end-to-end — confirmed a
    3-charge Repel blocks exactly 3 wild encounters, prints the correct "X encounters left"
    message each time, prints "Repel wore off!" at 0, and that the very next encounter after
    it expires correctly falls through to a real wild battle. A second harness drove
    `visit_shop()` and confirmed Repel/Super Repel/Max Repel appear in the Buy list only once
    the right badge count is reached. A third harness round-tripped `save_game`/`load_game`
    and confirmed `repel_steps` survives a save/load cycle. Scope note: by design Repel only
    blocks the regular wild-area "Walk further" encounter roll in `explore()` — it does not
    suppress random trainer encounters or hidden item finds (matches the in-code comment left
    by the previous session), and does not apply to fishing or grottos (separate, deliberate
    activities, not passive wandering).

- [x] **Repel: visible charge counter while exploring** — status: done
  - Added a `🛡 Repel active: N encounters left` line to the `explore()` status header,
    shown right under the team HP bars whenever `self.repel_steps > 0`.
  - Verified via a scripted harness (captured stdout from a real `explore()` call with
    `repel_steps=2`) that the indicator text renders on the very first screen.

- [x] **Fishing & grotto encounters missing badge-count level scaling** — status: done
  - Found while reviewing `explore()`'s badge-scaling pattern: `go_fishing()` and
    `explore_grotto()` both rolled wild levels straight from each town's base `(lo, hi)` range
    with no `badge_bonus`, unlike regular wild/trainer encounters which already get
    `+5 per 2 badges`. Net effect: fish and grotto creatures became trivially weak (and
    increasingly useless to catch/fight) in the back half of the game while regular wild
    encounters kept pace.
  - Fix: added the same `badge_bonus = (len(self.badges) // 2) * 5` calc to both functions and
    applied it to the `random.randint(lo, hi)` rolls in each.
  - Verified with a scripted harness (6 badges → expected +15): forced a fishing bite and a
    grotto encounter, monkeypatched `run_battle` to capture the wild creature's level before
    battle, and confirmed both came back within the badge-boosted range (e.g. Stonepeak's
    12-20 Old Rod pool produced Lv.31, i.e. base+15).

## New tasks — todo

- [ ] **Random trainer rematches while exploring** — status: todo
  - `explore()`'s random trainer encounters (the 18% roll) currently have no rematch/cooldown
    tracking at all — every walk can re-roll the same trainer archetype indefinitely, which is
    fine for grinding but means there's no sense of "named" trainers to remember, unlike gym
    leaders/rivals. Consider giving a handful of random trainers per area a fixed name + seed
    so repeat encounters feel like rematches rather than anonymous reskins, or leave as-is if
    that's judged not worth the complexity for a feature whose whole point is throwaway grinding.
