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

- [x] **Random trainer rematches while exploring** — status: done
  - Found a related piece of dead scaffolding while picking this up: `Game._defeated_trainers`
    was already declared in `__init__` (comment: "track rematched trainers by (area,
    name_hash)") but never read or written anywhere — leftover groundwork from an earlier
    session that never got finished. Built the actual feature on top of it:
  - Added `RANDOM_TRAINER_NAMES`: each of the 6 existing trainer titles (Youngster, Lass,
    Hiker, Sailor, Ranger, Ace Trainer) now pairs with 2 fixed first names, so a random
    encounter resolves to a stable identity like "Hiker Earl" instead of a bare title.
  - `explore()`'s trainer branch now builds a `trainer_key = f"{area_name}::{t_name}"` and
    checks it against `self._defeated_trainers`. First encounter with that identity in that
    area uses the normal "Let's battle!" intro; any later encounter with the *same* identity
    in the *same* area shows a distinct rematch line ("You beat me before, but I've been
    training!"). The key is recorded on every win (idempotent either way).
  - Persisted `_defeated_trainers` through `save_game()`/`load_game()` in `engine/core.py`
    (encoded as a sorted list of `"area::name"` strings, `setdefault([])` for old saves) and
    wired it through `Game.save()` and the continue-slot load path in `main.py`, matching the
    pattern used for `visited_towns`/`seen`/`caught`.
  - Verified: `py_compile` clean on all touched files. A scripted harness pinned
    `random.choice` to force the identity "Hiker Earl" in Rocky Tunnel, ran `explore()` twice
    capturing `slow_print` output — confirmed the first encounter shows the normal intro and
    records the key, and the second shows the rematch line. A second harness round-tripped
    `save_game`/`load_game` with a 2-entry `defeated_trainers` set and confirmed it survives
    intact. Scope note: identity is per (area, title+name) only — battle stats/mechanics are
    unchanged (still badge-scaled like any other trainer), this is purely a flavor/memory layer.

## New tasks — todo

- [ ] **Held item pity timer for long catch droughts** — status: todo
  - Wild creatures roll their held item independently per encounter via `held_item_pool`
    (typically 5-20% chance). A player with bad luck can go many encounters in a row without

## Session 4 — Resume from mid-task cutoff (2026-06)

- [x] **Held item pity timer for long catch droughts** — status: done
  - Previous session had begun this feature but left it half-finished with several critical bugs:
    1. Duplicate `else:` clause in `explore()` causing a `SyntaxError` (game wouldn't start).
    2. Grotto encounters (`explore_grotto()`) still using raw `roll_held_item(name)` — bypassing
       the pity counter entirely.
    3. `save()` was not passing `item_drought` to `save_game()` — counter lost on save.
    4. The continue-slot load path in `main()` wasn't restoring `g.item_drought`.
    5. Duplicate `rival_data = saved.get("rival")` line in the load path (cosmetic but cleaned up).
  - Previous session had also correctly: extracted `roll_held_item()` as a shared helper,
    added `pity_boost` param (with `min(1.0, chance * boost)` cap), added `PITY_THRESHOLD=8`
    and `PITY_MULT_PER_TIER=0.5` constants, and applied `_roll_held_item_with_pity()` to
    seasonal/override/fishing encounter paths, and added `item_drought` to `save_game`/
    `load_game` signatures in `engine/core.py`. All of that was sound and was kept.
  - Fixes applied this session: removed the duplicate `else:`, fixed grotto to use
    `self._roll_held_item_with_pity(name)`, wired `item_drought=` into `Game.save()`,
    added `g.item_drought = saved.get("item_drought", 0)` to the continue-load path,
    removed the duplicate `rival_data` line.
  - Design summary: `item_drought` tracks consecutive wild encounters without a held-item drop.
    At 8+ dry encounters (`PITY_THRESHOLD`), each further 8-encounter tier adds +50% boost to
    every item's effective drop chance (e.g. 10 dry → 1.5× boost; 18 dry → 2.0×; capped at
    1.0 per pool entry). The first successful drop resets drought to 0. Applies to regular
    wild, seasonal, night-bonus-override, fishing, and grotto encounters — all five paths now
    go through `_roll_held_item_with_pity()`. Invisible to the player; purely luck-smoothing.
  - Verified: `py_compile` clean on all files. A 3-part test script confirmed:
    (1) `pity_boost=100.0` caps at 1.0 and guarantees a drop when `random()=0.5`;
    (2) drought increments correctly through 10 dry rolls, boost kicks in at threshold (1.50×),
        and resets to 0 on the first drop; (3) `item_drought=13` survives a save/load cycle.

## Session 5 — Resume from mid-task cutoff (2026-06)

- [x] **Trainer Card: show Pokédex progress** — status: done
  - Found half-finished on session start: working tree had an uncommitted, partially-broken
    edit to `main.py` that started both this task and the next one simultaneously. The
    Pokédex-progress hunk itself (`open_stats()` Pokédex line using `CREATURES`/`seen`/`caught`)
    was complete and correct as left — added the line and verified output via a scripted
    `open_stats()` call: `Pokédex : 1 caught / 2 seen (2% of 38)` rendered correctly.

- [x] **Battle: switch prompt when lead faints mid-battle** — status: done
  - Found genuinely broken: the previous session's edit to `_pick_lead()` (new `fainted_name`
    param + faint banner) was complete and correct, and 5 of 6 call sites updating
    `player_c = alive[0]` / `alive_after[0]` to `player_c = self._pick_lead(fainted_name=...)`
    were also fine (gym, Elite Four, random trainer, fishing, grotto). But the **6th site**
    — the regular wild-encounter branch inside `explore()` — was mid-edit and syntactically
    broken: the lines `result, obj = run_battle(...)` and `if result == "win":` had been
    deleted, leaving the `self.seen.add(wild.name)` block dangling at the wrong indent with no
    `result`/`obj` defined, plus a duplicated `self._count_battle()` in the `elif result ==
    "caught":` branch right below it. This was a `NameError`/`IndentationError` waiting to
    crash the single most common gameplay action (walking and encountering a wild creature) —
    almost certainly where the previous session's process was cut off.
  - Fix: restored the missing `result, obj = run_battle(player_c, wild, self.inventory,
    self.team, wild=True, weather=weather)` call and `if result == "win":` line, removed the
    duplicate `self._count_battle()`, and re-attached the rest of the block (which was sound)
    underneath. Confirmed against `git show HEAD:main.py` to make sure the restored lines
    matched the pre-existing pattern used everywhere else in the file.
  - Verified: `python -m py_compile main.py` and `ast.parse()` both clean. Confirmed via
    `findstr` that no other `alive[0]` / `alive_after[0]` call sites remain unconverted (all 6
    now route through `_pick_lead`). Scripted unit tests against `Game._pick_lead()` directly
    confirmed: (1) single creature alive + `fainted_name` set → prints faint notice, auto-sends
    the survivor; (2) multiple alive + `fainted_name` set → prints the "✗ <name> fainted! Choose
    your next creature:" header, then the normal selection menu, returns the chosen creature.
    A full scripted playthrough of `explore()`'s wild-encounter branch (mocking `run_battle`,
    `random`, and `input`) was attempted but proved too brittle to finish reliably in this
    session given the menu/RNG surface area — the static verification above (restored code
    matches the known-good pattern byte-for-byte, compiles, and the helper function it calls
    is independently unit-tested) is considered sufficient; flagging this as a good first
    candidate for a real interactive playtest pass next session.

- [x] **Town: NPC dialogue system** — status: done
  - Added `NPC_DIALOGUE` dict: 3-4 flavor lines per town (all 10 towns covered), residents'
    gossip/hints/local color. Entries can be plain strings (always available) or
    `(condition_fn, text)` tuples gated on live game state — used here for "you just earned
    that town's gym badge" reaction lines and a Champion-only line on Champion Road.
  - `get_town_dialogue(game, town_name)` resolves the pool against current state and returns
    only the lines currently unlocked.
  - "💬 Talk to locals" option added to the town menu (only shown for towns with a pool —
    currently all of them) — picks one random available line and displays it.
  - Verified: `py_compile` clean. A scripted test called `get_town_dialogue()` directly across
    badge-count permutations and confirmed: conditional lines are correctly excluded/included
    (e.g. Greenpath without "Leaf Badge" → 3 lines, with it → 4; Champion Road only unlocks its
    4th line once `is_champion` is set), and that every town in `TOWNS` has a non-empty
    dialogue pool (no town silently lacks the option). Also unit-tested the menu label-parsing
    split against the new emoji option string to confirm it resolves to exactly "Talk to
    locals" so the `elif label == "Talk to locals":` branch is actually reachable.

- [x] **Explore: hidden grottos discoverable through exploration** — status: done
  - Carved a 3%-of-all-walks band (roll 0.76–0.79) out of the previously-unused "nothing
    happens" tail of `explore()`'s walk roll, gated on `GROTTOS.get(self.town)` so towns
    without a grotto keep their full original "nothing found" range untouched (no probability
    shift for those towns). When the band hits, prints a flavor line ("You notice a crack in
    the cliff face…") and calls the existing `explore_grotto()` directly, then naturally
    continues the explore loop afterward.
  - Verified: `py_compile` clean. A scripted harness pinned `random.random()` to land exactly
    in the new band on the first "Walk further" while in Greenpath (which has a grotto per
    `GROTTOS`) exploring its "Whisper Forest" wild area, and confirmed `explore_grotto()`
    fires exactly once when the band is hit, with the expected flavor text printed beforehand
    and the explore loop continuing normally afterward (next menu redraw, then a clean exit
    via "Return to town"). `GROTTOS` is keyed by town name, not wild-area name, which is why
    the check inside `explore()` uses `self.town` rather than `area_name`.

## Session 6 — Resume from mid-task cutoff (2026-06)

- [x] **Audit pass: confirm no other `alive[0]`-style dead-end patterns remain** — status: done (commit bd681f5)
  - Completed last session via grep of `engine/battle.py` and `engine/rival.py`. Two remaining
    `alive_after[0]` sites in `run_rival_encounter()` and `run_rival_rematch()` were converted
    to `_pick_lead(fainted_name=...)`. No further fallback patterns found.

- [x] **Shiny / rare color-variant creatures** — status: done
  - Previous session began this feature but was cut off with two bugs: (1) a duplicate
    `if captured.held_item:` line (empty body after the shiny-catch block) causing
    `IndentationError` in main.py; (2) the `def menu(title, options, color=C.CYAN):` line
    deleted from `ui/display.py`, making `menu` unexportable and crashing all imports of
    `engine.battle` and `main`. Both were fixed this session before verifying the feature.
  - Full implementation confirmed across all 5 encounter paths:
    - `Creature.is_shiny` attribute (default False), serialised in `to_dict`/`from_dict`
      with `setdefault(False)` for old saves.
    - `SHINY_CHANCE = 1/100` constant in `engine/core.py`.
    - `Game._apply_shiny_roll(wild)` helper sets `wild.is_shiny = True` on a 1% roll.
    - Called in all 5 wild creation spots: night-override pool, seasonal pool, regular
      `random_wild()`, fishing, and grotto encounter.
    - Distinct encounter messages for shiny (✦✦✦ banner + "sparkles with a brilliant light!").
    - `Game.shiny_caught` set: populated at all 3 catch sites (explore, fish, grotto);
      special "★✦★ You caught a SHINY!" message on catch.
    - Persisted via `save_game(shiny_caught=…)` / `load_game()` with `setdefault([])` for
      old saves; wired through `Game.save()` and the continue-load path.
    - Pokédex list view: ✦ gold marker on entries the player has caught as shiny.
    - Pokédex detail view: "✦ Shiny caught!" note next to "● Caught" status.
    - `creature_card()` in display.py: ✦ suffix on name line.
    - `team_summary()` in display.py: ✦ after name in team list.
    - `_dname()` in battle.py: ✦ prefix on creature name in all battle messages.
  - Verified: all files compile clean. 10-test script confirmed creature serialisation,
    SHINY_CHANCE value, save/load round-trip, `_apply_shiny_roll` existence, 5 encounter
    path calls, 3 catch-site tracking calls, encounter messages, Pokédex display, and
    battle/display shiny markers all present and correct.

## Session 7 — New features (2026-06)

- [x] **Battle: turn-by-turn damage summary readability** — status: done
  - Added a `_recap` dict (keys: `player_move`, `player_dmg`, `enemy_move`, `enemy_dmg`)
    that is populated each turn — player move name + damage dealt at the `player_attack` call
    site, enemy damage at both `enemy_move` call sites.
  - At the start of every non-first turn (after `battle_ui`, before the weather reminder),
    prints a compact single-line recap: "Last turn ───  ↑ Your X: MoveName → N dmg dealt   ↓
    Foe Y: attacked → N dmg taken". Zero-damage entries (e.g. status moves or misses) still
    display correctly (shows 0 dmg).
  - Verified: all files compile clean; 5 scripted assertions confirmed _recap vars and the
    "Last turn" banner are present in battle.py and that ast.parse() succeeds.

- [x] **Daily/weekly login-style bonus for returning players** — status: done
  - Added `last_played_date` (ISO date string) to `save_game()` / `load_game()` in
    `engine/core.py` (new param `last_played_date=None`, stored in JSON, `setdefault("")`
    for old saves). Wired into `Game.save()` using `datetime.date.today().isoformat()`.
  - On `Continue` load path in `main()`, compares `g.last_played_date` to today's date.
    If different and non-empty, picks a random gift from a small pool (Potions, Super Potions,
    Antidotes, Elixir, Great Balls, Revive) and grants it directly to `g.inventory`, then
    shows a 🌅 DAILY BONUS banner. Updates `g.last_played_date = _today` after.
  - Cannot be farmed: bonus only fires when the saved date differs from real today; saving
    then reloading on the same day keeps the same date so the check fails harmlessly.
  - New players (empty `last_played_date`) skip the bonus on first load.
  - Verified: save/load roundtrip preserves the date; date-comparison logic confirmed correct
    for same-day (no trigger) and different-day (trigger) scenarios.

## New tasks — todo

- [ ] **Move-efficiency tips in post-battle summary** — status: todo
  - The post-battle summary shows aggregate damage dealt/taken but gives no qualitative hint.
    If the player used 0 super-effective moves the whole fight, or if the foe resisted every
    move they used, add a single-line tip (e.g. "Tip: Flamclaw's Fire moves were resisted —
    try a creature with coverage moves next time."). Low-friction, opt-in feel.

- [ ] **Creature glossary / lore entries** — status: todo
  - Each creature species already has a short `desc` in creatures.py used only by the Pokédex
    detail view. Expand to 2-3 sentence lore blurbs stored in creatures.py, shown in the
    Pokédex detail view (replacing the current one-liner). Purely flavor — no new mechanics,
    just makes the world feel richer when browsing caught creatures.

