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

## Session 8 — Resume from mid-task cutoff (2026-06)

- [x] **Move-efficiency tips in post-battle summary** — status: done
  - Previous session had added `moves_used`, `moves_super`, `moves_resisted`, `enemy_types`
    fields to `BattleSummary` and wired the tip text into `show()`, but **never populated
    the counters** — they stayed zero every battle so tips never appeared.
  - This session completed the wiring: set `summary.enemy_types = list(enemy_c.types)` right
    after `summary = BattleSummary()` at battle start; then at the `player_attack` call site,
    look up the move's type via `MOVES.get(move_name, {}).get("type", "")`, compute
    effectiveness against `enemy_c.types` using `TYPE_CHART` (same logic as `type_hint()`),
    and only count moves with `power > 0` (excluding status moves like Growl).
  - Three tip tiers: ✅ green "Great type coverage!" if super > 0 and resisted == 0;
    ⚠ yellow "moves were resisted — try better coverage" if resisted > 0 and super == 0
    (includes the enemy type string e.g. "rock/steel-types"); 💡 cyan "Mixed effectiveness"
    if both super and resisted occurred. No tip shown if no damaging moves were used.
  - Verified: 10 tests passed — field init, all three branch conditions, TYPE_CHART lowercased
    key checks (water vs fire = 2x, normal vs ghost = 0x immune, fire vs rock resisted),
    counter tracking with real moves from MOVES dict (Water Gun counted as super vs fire,
    status move correctly excluded), source-level presence of all three counter increments.

## Session 9 — Resume from mid-task cutoff (2026-06)

- [x] **Creature glossary / lore entries** — status: done
  - Found this half-finished on session start: `git status` showed uncommitted edits to
    `data/creatures.py` and `main.py`, plus two untracked helper scripts (`_patch_lore.py`,
    `_test_lore.py`) — the previous session's own lore-expansion patch script and its
    verification test, left sitting there unrun. Running `_test_lore.py` immediately
    reproduced the exact failure the previous session would have hit: `FAIL: short lore
    entries: [('Flamclaw', 33), ('Infernox', 34)]`.
  - Root cause: for these 2 of 38 creatures (out of 38 total), the in-place line edit that
    inserted the new long-form lore line landed on the wrong source line — it overwrote the
    `"catch_rate"/"ability"` line for Flamclaw and the `"evolution"` line for Infernox instead
    of the old one-line `"desc"` field, leaving each entry with **two** `"desc"` keys in the
    same dict literal. Since Python dict literals silently let the later key win, the new lore
    text was dead on arrival — `CREATURES["Flamclaw"]["desc"]` still evaluated to the old
    33-character one-liner — while `catch_rate`/`ability` (Flamclaw) and `evolution` (Infernox)
    were missing entirely (confirmed via a throwaway audit script: `MISSING: [('Flamclaw',
    'catch_rate'), ('Flamclaw', 'ability'), ('Infernox', 'evolution')]`). `catch_rate`/`ability`
    being silently absent would have broken capture-rate math and ability lookups for that
    species the moment a player caught or battled one.
  - Fix: rewrote both dict blocks cleanly — restored `"catch_rate": 45, "ability": "Blaze"` for
    Flamclaw and `"evolution": {}` for Infernox, removed the dead duplicate `"desc"` lines, and
    kept the new long-form lore text the previous session had written (it was good prose, just
    mis-inserted).
  - Found a second, related gap while reviewing where `desc` is actually displayed: the previous
    session's task note assumed `desc` was "used only by the Pokédex detail view," but it's also
    printed in two other places that were never updated for the new ~250-character lore length —
    `open_creatures()`'s per-creature detail card and the starter-selection screen in
    `new_game()`. Both printed `desc` as a single unwrapped f-string segment, which would have
    rendered as one giant unbroken line the moment a player opened either screen. Fixed both with
    the same `textwrap.wrap(..., width=66-70)` pattern already used in the Pokédex view, just
    formatted to fit each screen's existing layout (multi-line under the name/type header for the
    starter screen; multi-line under the ability/nature/held-item block for the creature card).
  - Verified: `py_compile`/`ast.parse` clean on all touched files. Re-ran `_test_lore.py` —
    now passes (`PASS: all 38 creatures have desc >= 80 chars`, avg 266 chars). Wrote
    `_verify_lore_fix.py`: drives `Game._show_pokedex_entry()` directly for both previously-broken
    species and asserts the new lore text appears and the stale short text does not; asserts
    `CREATURES["Flamclaw"]["catch_rate"]/["ability"]` and `CREATURES["Infernox"]["evolution"]`
    are restored; asserts both newly-discovered unwrapped display sites now wrap. All passed.
    Manually inspected the rendered wrap output for all 4 starters plus a sample evolved form —
    reads cleanly at the terminal widths used. Also ran a full subprocess launch of `main.py`
    with scripted stdin through an existing save's Continue → town menu → Shop → Buy flow;
    confirmed it renders correctly end-to-end with no traceback (the only EOFError seen was the
    scripted input list running out, not a game fault — same caveat noted in Session 2/5).

- [x] **Type effectiveness chart — in-game reference menu** — status: done
  - The battle UI already showed per-move effectiveness hints (▲▲/▼/✗) against the current
    foe, but there was no way to see the *full* type chart at a glance. Added a
    "📘  Type Chart" option to the top-level town menu (between Pokédex and Badges).
  - Implementation: `show_type_chart()` in `ui/display.py` renders all 16 in-use creature
    types (the exact set found in `data/creatures.py`, not a generic 18-type list — no
    creature is Fighting or Fairy type in this game, so those columns would've been pure
    clutter) as a 16×16 attacker-rows × defender-columns grid, reading `TYPE_CHART` directly
    so the reference can never drift out of sync with the real battle math. Reused the exact
    same hint symbols/colors already used in the in-battle fight menu (`▲` yellow super
    effective, `▼` blue not very effective, `✗` gray immune, `·` gray neutral) for visual
    consistency rather than inventing a new color scheme. Also filled in the two missing
    `TYPE_COLORS` entries (`dragon`, `steel`) in `ui/display.py` while in there — both types
    were falling back to plain white in every other screen that uses `TYPE_COLORS` (creature
    cards, fight-menu move tags), a small pre-existing gap directly relevant to this feature.
  - Verified: `_test_type_chart.py` — (1) the chart's 16-type list exactly matches the set of
    types actually used across all 38 creatures; (2) 8 sample (attacker, defender) pairs
    spanning super/resisted/immune/neutral cases render the exact symbol+color implied by
    `TYPE_CHART`'s real values; (3) every rendered row (header + 16 data rows), with ANSI
    codes stripped, is the same visible width — confirms the grid stays column-aligned;
    (4) the menu option string, import, and `label == "Type Chart"` handler are all actually
    wired into `town_loop()` in main.py, not just defined and orphaned; (5) `py_compile` clean
    on both touched files. Also manually inspected the rendered grid output and spot-checked
    several rows by hand against `TYPE_CHART` (e.g. Fire row: resists itself/Water/Rock,
    super effective vs Grass/Ice — matches).

- [x] **Bug: Scope Lens held item silently did nothing** — status: done
  - Found while implementing the type chart (same crit-roll code path). `held_item_crit_bonus()`
    in `engine/battle.py` was fully implemented and correctly documented — Scope Lens's item
    `desc` says "Critical hit chance doubled," and the README lists it under held items — but
    the function was never called from anywhere in the codebase. `calc_damage()` in
    `engine/core.py` rolled crits with a hardcoded `random.randint(1, 16) == 1`, completely
    ignoring the holder's item. Net effect: every player who spent ₽2000 on a Scope Lens and
    equipped it got nothing for it, with no error or indication anything was wrong — pure
    silent dead weight in a held-item slot.
  - Fix: wired `held_item_crit_bonus(attacker)` into `calc_damage()`'s existing late-import
    block (alongside the ability multipliers, to avoid the circular `engine.battle` import),
    and used its result to pick a crit denominator of 8 (Scope Lens) or 16 (default) for the
    `random.randint(1, crit_denom) == 1` roll — exactly the 1-in-8 vs 1-in-16 split the
    function's own docstring already described.
  - Verified: `_test_scope_lens_fix.py` runs 20,000 damage-calc trials with a seeded RNG both
    without and with Scope Lens equipped — baseline crit rate landed at ~6.3% (expected
    ~6.25%), Scope Lens rate at ~12.4% (expected ~12.5%), confirming the doubling now actually
    happens. `py_compile` clean on both touched files; full existing regression suite
    (`_test_lore.py`, `_verify_lore_fix.py`, `_test_type_chart.py`) still passes — no
    behavior change to anything except crit chance for Scope Lens holders.


## New tasks — todo

- [x] **Friendship / affection system** — status: done
  - Verified Session 9's final state first: working tree clean and in sync with origin
    (commit `5f629e7`), all 6 core files `py_compile` clean, no TODO/FIXME/stub/conflict
    markers anywhere in the repo, and a real `main.py` launch (scripted stdin) rendered the
    banner, daily-bonus screen, and town menu correctly — only EOF came from the stdin
    script running out, the same harness caveat noted in Sessions 2/5/9, not a game fault.
    No task was left in-progress, so this picked up the next queued item fresh.
  - Implementation: `Creature.friendship` (0–100, `BASE_FRIENDSHIP = 70` default) added in
    `engine/core.py`, persisted via `to_dict`/`from_dict` (old saves without the key default
    to 70, same pattern as `nickname`/`is_shiny`). Sources of gain: +2 to the battle winner
    and +1 to each bench creature that received shared EXP (`award_exp()` in `main.py`), +1
    per level-up (`gain_exp()`), +2 whenever a one-use berry actually triggers for that
    creature (`check_held_item()` in `engine/battle.py` — status-cure, half-HP heal, and
    low-HP stat berries all award it at their existing trigger point).
  - Mechanical payoff at `BOND_THRESHOLD = 100` (maxed bond) — picked two small but real
    effects rather than one, so the system has more than a single flat number behind it:
    (1) crit-roll denominator drops by 4 in `calc_damage()` (stacks with Scope Lens, floored
    at 4) — verified statistically; (2) a 10%-chance, once-per-battle "bond save" in
    `Creature.take_damage()` that survives an otherwise-lethal hit at 1 HP with its own flavor
    line, mirroring the existing Sturdy implementation pattern; the one-per-battle flag
    (`_bond_save_used`) resets in `reset_stages()` exactly like Sturdy's own flag.
  - UI: `creature_card()` in `ui/display.py` shows a `♥♥♥♡♡`-style 5-heart bar plus a tier
    label (Distant / Friendly / Close Bond / Best Friends!) under the ability/nature line —
    gated on `show_exp` (the existing "this is the player's own creature" flag) so it never
    shows on enemy/wild cards.
  - Verified: new `_test_friendship.py` (kept in the repo alongside the project's other
    `_test_*.py` regression scripts) — default value + clamping in both directions,
    to_dict/from_dict round-trip, old-save fallback to the default, +1 on a forced level-up,
    bond-save procs at/above threshold across 500 guaranteed-lethal trials and never below
    threshold, confirms it only fires once per battle and clears via `reset_stages()`, and a
    20k-trial statistical check that the maxed-bond crit-rate is meaningfully higher than
    baseline (6.3% → ~8.0%, consistent with the 16→12 denominator change). Re-ran the full
    existing regression suite (`_test_lore.py`, `_verify_lore_fix.py`, `_test_type_chart.py`,
    `_test_scope_lens_fix.py`, `_test_move_tips.py`) — all still pass, confirming no
    regressions. Rendered `creature_card()` against a real save's team via a throwaway script
    (deleted after use) to confirm the heart bar/label actually display correctly at both the
    default (70 → "Friendly") and maxed (100 → "Best Friends!") tiers; `py_compile` clean on
    all five touched files.

## New tasks — todo

- [x] **Friendship-aware capture rate** — status: done
  - Verified Session 10's final state first: working tree clean and in sync with origin
    (commit `3204ab5`), all 6 core files `py_compile` clean, and the full existing test
    suite (`_test_friendship.py` + the 5 prior regression scripts) passed unchanged. No
    in-progress task was left hanging, so this picked up the queued follow-on fresh.
  - Implementation: `friendship_capture_bonus(lead)` in `engine/core.py` — returns a 1.0–1.10
    multiplier on the effective ball rate. No bonus below `FRIENDSHIP_CAPTURE_THRESHOLD = 80`
    bond; above it, scales linearly up to `FRIENDSHIP_CAPTURE_MAX_BONUS = 0.10` (+10%) at
    `MAX_FRIENDSHIP = 100`. `try_capture()` gained an optional `lead=None` kwarg (fully
    backward compatible — the one other call site and any future direct caller still works
    unchanged with no lead) that applies the bonus to `ball_rate` before the existing capture
    math runs untouched.
  - Threaded the player's active creature through as `lead`: `animated_capture()` in
    `engine/battle.py` gained the same `lead=None` kwarg, and its single call site (the
    in-battle Bag → capture-item handler) now passes `lead=player_c` — the active creature is
    already in scope there. Added a one-line flavor message ("X's calm presence settles the
    wild creature...") that only prints when the lead is actually at/above the 80-friendship
    threshold, so the bonus is visible/felt and not just a silent number.
  - Verified: new `_test_friendship_capture.py` — no-lead and below-threshold give exactly
    1.0x, exactly-at-threshold gives 1.0x (bonus starts strictly above it), max friendship
    gives exactly 1.10x, mid-range friendship interpolates strictly between the two: confirmed
    `try_capture()`'s default behavior (no `lead` arg at all) is bit-for-bit identical to
    passing `lead=None`. Used same-seed paired trials (reset RNG to the same seed before each
    of the two calls) across 2000 borderline-catch scenarios to prove the bonded lead's higher
    effective rate never produces *fewer* shakes or a missed catch where the unbonded case
    caught, and does produce strictly more shakes in some trials — this is a deterministic
    monotonicity proof rather than a noisy statistical sample, so it can't flake. Had to tune
    the test's wild-HP/ball-rate scenario once the first attempt revealed the 10% bonus was
    being swallowed by `int(a)` truncation at small magnitudes — confirmed via a throwaway
    debug script (deleted after use) that printed the intermediate `a`/`b` capture-formula
    values, then picked a low-HP/high-rate scenario where the delta survives truncation.
    Re-ran the full existing regression suite (`_test_friendship.py`, `_test_lore.py`,
    `_test_type_chart.py`, `_test_scope_lens_fix.py`, `_test_move_tips.py`) — all still pass.
    `py_compile` clean on both touched files.

## Session 10 — Battle Bag/menu polish (2026-06)

- [x] **Battle Bag/menu polish pass** — status: done
  - Ran both `_ux_check_capture.py` and `_ux_check_shakes.py` (the previous session's UX
    harnesses) to inspect the real rendered output before touching any code. Four UX issues
    found:
    1. **Calm presence / throw line crowding** — the friendship flavor line ("X's calm presence
       settles the wild creature…") printed with no pause before the throw line, so both lines
       appeared almost simultaneously. Fixed: added `time.sleep(0.3)` after the flavor line in
       `animated_capture()` so the player can actually read it before the throw text arrives.
    2. **Successful catch animation ended silently** — 4 shakes + blank line, then the calling
       code's "★ Gotcha!" printed. No in-animation signal that the catch succeeded. Fixed:
       replaced the blank `print()` on the caught branch with a `★ Click!` (green) with a
       0.6s delay, mirroring the `*shake*` timing — now the animation reads as a complete
       sequence: shake shake shake shake ★ Click! → ★ Gotcha!
    3. **Shake-count hints had inaccurate wording** — "One shake — so close!" (it really isn't),
       "Two shakes! … A Great Ball might do it" (player might already have one), "Three shakes
       — Try an Ultra Ball" (player might already be using one). All three revised to be more
       accurate and ball-agnostic: 1 shake → "try weakening further or upgrading your ball";
       2 shakes → "try a Great Ball or weaken more"; 3 shakes (now green) → "An Ultra or
       Master Ball should do it."
    4. **Stale "No effect." message for cure items** — applying e.g. Antidote when not poisoned
       just printed "No effect." with no explanation. Fixed: now shows either "X has no status
       condition." or "That item doesn't cure Burn." (etc.) so the player understands what
       happened and isn't left guessing.
  - **Bonus fix**: Heal item "recovered 0 HP!" when already at full HP was confusing. Refactored
    the heal branch to show "X is already at full HP!" when healed=0 and no status was cured,
    and to separately show "Status condition cleared!" if a Full Restore cured status on an
    already-full-HP creature (previously both cases merged into a single message).
  - Confirmed: calm presence + throw sequence now reads naturally; the "★ Click!" provides
    immediate visual closure on a successful catch before the celebratory "★ Gotcha!" line;
    shake hints now guide the player without recommending balls they might already be using.
  - No crowding/duplication with friendship "calm presence" and shake hints — they appear on
    separate logical events (capture attempt start vs. capture failure) so they never overlap.
  - Full regression suite passes; `py_compile` clean on `engine/battle.py`.

## New tasks — todo

- [x] **Weather ability interactions: verbal feedback** — status: done
  - Audit found the task description slightly overstated the problem: Ice Body and Speed Boost
    already had `end_of_turn` hooks with printed messages (the in-game log showed them fine).
    The real gaps were Swift Swim (purely a speed multiplier, completely silent) and
    Blaze/Overgrow/Torrent (per-hit damage boost, also silent when they activate).
  - **Swift Swim**: Added `on_entry` hook — fires `"🌧 X's Swift Swim kicked in! Speed doubled
    in the rain!"` when entering battle (or switching in) while weather is Rainy; silent in all
    other weather. Fires via the existing `fire_on_entry()` path already called at battle start
    and on every switch-in — no call-site changes needed.
  - **Blaze / Overgrow / Torrent**: Added `end_of_turn` hooks using a new helper
    `_starter_ability_notice(c, ability_name, move_type, icon, color)` — fires a one-shot
    colored notice the first time the creature's HP drops to ≤ 1/3 ("🔥 Flambit's Blaze
    activated! Fire moves are now powered up!"). Uses a per-creature flag
    (`_blaze_notified` etc.) to suppress repeats within the same send-in; flag cleared in
    `reset_stages()` (which already runs on battle start and switch-in) so it re-fires if
    the creature switches out and back in to low HP again.
  - `engine/core.py` `reset_stages()` extended with three new flag clears; no other files
    touched beyond `engine/battle.py`.
  - Verified: `_test_swift_swim.py` (3 assertions: fires in rain, silent in sunny/None,
    message wording) and `_test_ability_feedback.py` (6 assertions: Swift Swim + all three
    starter abilities at/above threshold, one-shot suppression, flag reset on switch).
    Full 8-file regression suite passes. `py_compile` clean on both touched files.

- [x] **Status condition duration UI** — status: done
  - Sleep and Confusion have turn counters (`sleep_turns`, `confusion_turns`); now shown
    in the creature card as `[SLP-2]` / `[CNF-3]` etc. Falls back to plain `[SLP]`/`[CNF]`
    when turns=0 (wake-up edge). Poison/Burn/Paralysis/Freeze unaffected (no turn counter
    to show). Implemented in `creature_card()` in `ui/display.py`. Verified via
    `_test_status_duration.py` (7 assertions, all pass). Full regression suite still passes.

- [x] **Move power visual tier in fight menu** — status: done
  - Added `_pwr_tier(pwr)` nested helper inside the fight-menu `else:` block in `run_battle()`
    — 4 tiers: `—` gray (status/power=0), `★` yellow (≤40), `★★` yellow (41–80), `★★★` red
    (81+). Padded to 4 chars width so all move lines stay column-aligned regardless of tier.
    Slotted between `Pwr:N` and the type tag so the line order reads naturally: name / PP /
    raw power / stars / type / effectiveness hint. Purely cosmetic — no logic change.
  - Verified: `ast.parse` + `py_compile` clean; `_pwr_tier` present with both ≤40 and ≤80
    thresholds and `★` char (U+2605) confirmed in the compiled file. Full regression suite
    unaffected.

- [x] **Town map: highlight current location** — status: done (was already implemented)
  - Verified against `ui/display.py`: `show_world_map()` already accepts `current_town` and
    `badges` params. The `is_here` check in the town-label loop sets `color = C.CYAN + C.BOLD`
    and `marker = '►'` for the current town, visually distinct from all other nodes. The legend
    at the bottom of the map explicitly notes `►Town (you are here)`. Called correctly from
    `main.py` as `show_world_map(self.town, self.badges)`. Feature was complete all along —
    task entry was stale.

## Session 11 — Resume from mid-task cutoff (2026-06)

- [x] **Held item shop: dedicated held-item vendor** — status: done
  - Previous session had fully implemented `visit_held_item_vendor()` in `main.py` and wired
    the "🧤 Item Specialist" option into the Dragonspire town menu, but left it uncommitted
    alongside a duplicate `slow_print` in `reorder_team()` and a spurious blank line injected
    before `lines = get_town_dialogue` in the "Talk to locals" handler. Both bugs fixed this
    session before pushing.
  - Vendor is Dragonspire-exclusive (guarded by `self.town == "Dragonspire"`). Sells all 5
    combat held items (Life Orb ₽4500, Choice Band ₽3500, Leftovers ₽3000, Shell Bell ₽3500,
    Scope Lens ₽3500) plus all 7 berries (Lum/Sitrus/Oran + the 4 seasonal berries that are
    otherwise RNG-only drops — Salac/Petaya/Apicot/Ganlon at ₽2000 each). Each item shows its
    in-game `desc` and how many the player already owns. Quantity prompt (1–9) before purchase.
    Correct money is deducted; items land in `self.inventory`.
  - Verified: `_test_vendor_tutor.py` (10 tests, all pass): method existence, Dragonspire gate,
    handler wired, all 5 combat items present, all 4 seasonal berries present, COVERAGE_TUTOR
    dict structure, coverage logic vars, skip-already-known logic, functional 3-pick sim for
    normal-only team, water-coverage skip for water-type team. Full 12-script regression suite
    passes. `py_compile` clean.

- [x] **Egg moves / tutor expansion: teach moves based on type** — status: done
  - Same commit as above (both features were together in the uncommitted diff).
  - Added `COVERAGE_TUTOR` dict (16 attacker-type → (move_name, cost) entries) at module level
    near `MOVE_TUTORS`. Modified `visit_move_tutor()`: when `town_name == "Dragonspire"`,
    computes which attacker types the team can already hit super-effectively (using `TYPE_CHART`
    against all defender types), then selects up to 3 moves from `COVERAGE_TUTOR` for uncovered
    types — skipping moves already in the fixed tutor list or already known by any team member.
    If any coverage moves are found, prints a cyan "I also sense your team could use some
    coverage moves..." line before showing the expanded menu (fixed 3 + up to 3 dynamic).
    On subsequent visits with better team coverage, fewer or zero extras are injected.
  - Verified: same `_test_vendor_tutor.py` tests 6–10.

- [x] **Battle: per-move accuracy display in fight menu** — status: done
  - Added `_acc_tag(acc)` helper alongside `_pwr_tier` in `engine/battle.py`. Shows a gray
    em-dash `—` for 100% accuracy (perfect = no clutter), white `XX%` for ≥90, yellow `XX%`
    for ≥75, red `XX%` for anything below. Slot inserted between the star-tier and the type
    tag: `Pwr:90  ★★★ Acc:—   [FIRE   ]  ▲▲`. Color-codes the risk at a glance without
    hiding information. Verified via `_test_acc_display.py` (8 assertions), full regression
    suite passes.


- [x] **Trainer battle weakness hints** — status: done
  - Scope expanded from rival-only to all trainer battles (gym leaders, Elite Four, random
    trainers, rival) — more useful and no extra complexity. Added a `Weak to:` line in
    `battle_ui()` in `engine/battle.py`, shown only when `wild=False`. Iterates all 16 game
    types, computes combined effectiveness against the enemy's type(s) via `TYPE_CHART`, and
    displays up to 4 weakness types as color-coded `[TYPE]` tags (reusing `TYPE_COLORS` from
    the existing fight menu) beneath the enemy creature card. Does not appear in wild battles.
  - Verified: `_test_weakness_hint.py` (7 assertions: py_compile, wild→no hint, trainer→hint
    present, correct types for Fire, TYPE_CHART agreement, dual-type renders without error,
    cap at ≤4 types). Full 11-script regression suite passes. `py_compile` clean.

- [x] **Achievement gallery** — status: done
  - Added `open_achievements()` method on `Game` in `main.py`. Displays all 12 achievements
    in a clear screen: `✓ Name` (yellow + bold) with the flavor `desc` indented below for
    earned ones; `○ Name` (gray) for locked. Shows `Unlocked: X/12` count at top, turning
    yellow when all are complete. Accessible from the town menu via new `🏆  Achievements`
    option (inserted after `📊  Trainer Card`). No data-layer changes needed — `achievements`
    list was already persisted via `save_game()`/`load_game()`. Verified via
    `_test_achievements.py` (7 tests: method existence, menu wiring, handler wiring, compile\n    clean, 0-/partial-/full-achievement renders). All 11 regression scripts still pass.

## Session 11 new tasks — todo

## Session 12 — Resume from mid-task cutoff (2026-06)

- [x] **Battle performance rating** — status: done
  - Found partially implemented on session start: `_grade()` method, `player_start_hp` field,
    and grade display in `show()` were all complete and correct in `engine/battle.py`. The
    task note in task.md was marked todo but the code was already there — verified it compiled
    and the logic was sound before touching anything.
  - Grade scoring: 100 pts base; -6 per turn beyond 3 free turns; -15 per item used;
    -10 per switch; -0.3 per % of lead's max HP taken. S ≥ 90, A ≥ 70, B ≥ 45, C = below.
    Grade shown as first line of the post-battle summary (after the section header, before
    turns/damage). Color-coded: S yellow+bold, A green+bold, B cyan, C gray.
  - Verified via `_test_session12.py`: S for perfect run (2t, 0 items, 0 switches, 5% dmg),
    A for clean run (5t, 0 items, 0 switches, 20% dmg), B for decent run (5t, 1 item,
    1 switch, 20% dmg), C for rough run (12t, 3 items, 2 switches, 80% dmg).

- [x] **Money penalty on trainer loss** — status: done
  - Also found partially implemented on session start: `apply_loss_penalty()` was defined in
    `main.py`, wired into gym/Elite Four/random-trainer losses, and wired into rival loss in
    `engine/rival.py`. One critical bug was present: the random-trainer for-loop (which
    battles a trainer's 1–3 creatures in sequence) had `lost = True` without a `break`
    — meaning after losing the first battle, the loop would attempt to start another battle
    with an already-wiped team. Fixed by restoring the `break` on line 1881.
  - Penalty: `max(100, min(1000, money // 10))` — 10% of current money, floored at ₽100,
    capped at ₽1000. Message: "You lost ₽N in the confusion of defeat...". Wild losses
    (explore, fish, grotto) are penalty-free — no call added there.
  - Verified via `_test_session12.py`: formula correct, all 3 main.py call sites present,
    rival.py call site present, break-after-lost confirmed via regex search.

- [x] **Fight menu: show move category (Phys/Spec/Stat)** — status: done
  - Added `_cat_tag(cat)` helper alongside `_pwr_tier` and `_acc_tag` in `run_battle()`'s
    fight-menu block. Returns red `Phys`, cyan `Spec`, or gray `Stat` (each 4 chars, padded)
    based on the move's `category` key. Slotted between `Acc:` and `[TYPE]` in the move
    option f-string so the column order reads: Name | PP | Pwr | Stars | Acc | Cat | [TYPE] |
    effectiveness hint.
  - Verified via `_test_session12.py`: helper present, all three branches confirmed, used in
    move_opts f-string, py_compile clean. Full 14-script regression suite passes unchanged.

## Session 12 new tasks — todo

- [x] **Gym leader pre-battle type preview** — status: done
  - Resumed from a previous session that was cut off mid-task: the feature was already fully
    coded in `data/creatures.py` and `main.py` (uncommitted) when this session started. Verified
    it was complete and correct before building anything on top of it, then committed it.
  - Added a `"type"` key to all 7 gym dicts in `TOWNS` (`data/creatures.py`). `challenge_gym()`
    in `main.py` now prints a `Specialist type : [TYPE]` line plus a `Weak to :` line (up to 4
    types, computed live against `TYPE_CHART` rather than hard-coded) and a `Team size :` line,
    shown right after the leader's quote and before the player picks their lead. The town menu's
    gym option also shows a color-coded `[TYPE]` tag next to the leader's name so the type is
    visible without entering the gym screen at all.
  - Verified via `_test_gym_preview.py` (10 assertions: compile-clean, all 7 gyms carry the
    correct type, `TYPE_CHART`/`TYPE_COLORS` imported correctly, preview lines present, weaknesses
    computed live and capped at 4, town-menu tag wired, gym routing unbroken, fire-type spot
    check). One stale quote-style assertion in the test itself was corrected (the implementation
    was already right). Full 15-script regression suite passes; `py_compile` clean across the
    whole repo; no merge-conflict markers found; smoke-launched `main.py` to confirm the title
    screen and menus render with no crash.

- [x] **Inn: choice of full heal vs cheaper partial heal** — status: done
  - `visit_inn()` in `main.py` now branches: if the team has anything to heal, it shows a 3-way
    `menu()` — Full Heal (₽cost, unchanged: full HP, cures status, restores all PP), Partial
    Heal (₽`max(1, cost // 2)`, restores `ceil(missing_hp / 2)` HP per creature only — status
    and PP are deliberately left untouched to make it a real trade-off, not just a cheaper
    full heal), or Cancel. The already-fully-healed "pay anyway" single-confirm path is
    unchanged. Insufficient-funds check now uses the price for whichever mode was picked.
  - Verified via `_test_inn_partial_heal.py` (10 assertions: cost formula, 3-way menu wiring,
    cancel exits without charging, correct branch-specific price deducted, full heal still
    untouched, partial heal touches HP only via the ceil-50% formula and never status/PP,
    money-guard uses the right price, numeric spot-check of the formula, already-full path
    unchanged) — one test-only branch-isolation bug was found and fixed during verification
    (the implementation itself was correct). Also hand-verified by scripting three live
    `visit_inn()` calls (Full Heal, Partial Heal, Cancel) with a damaged + poisoned creature:
    Full Heal → 29/29 HP, status cured, -₽300; Partial Heal → 22→26/29 HP (missing 7,
    ceil(7/2)=4), status still poisoned, -₽150; Cancel → no HP/status/money change. Full
    16-script regression suite passes; `py_compile` clean.

- [x] **Wild encounter level caps by badge count (hard cap)** — status: done
  - Added `capped_wild_level(lo, hi, badge_bonus=0)` to `engine/core.py`: rolls the same
    `[lo+bonus, hi+bonus]` range as before, but clamps both ends at `hi * 2` (the area's base
    `hi` doubled) before rolling, so a maxed-out badge_bonus on an early/low-`hi` area pins the
    level at the cap instead of overshooting it. Zero/low bonus behaves identically to the old
    plain `randint(lo, hi)` — this only ever pulls levels *down*, never changes them upward.
  - Replaced every raw `random.randint(lo + badge_bonus, hi + badge_bonus)` wild-level roll with
    a call to the shared helper: `random_wild()` in `engine/core.py` (the main per-area wild
    pool), plus all 4 matching call sites in `main.py` — the night-time ghost pool override and
    seasonal-bonus pool inside `explore()`, the fishing pool in `go_fishing()`, and the grotto
    creature pool in `explore_grotto()`. Random-trainer/gym/rival team level scaling
    (`lv + badge_bonus` on a *fixed* level, not a range) is a different mechanic and was
    deliberately left untouched — there's no "base hi" to overshoot there.
  - Verified via `_test_wild_level_cap.py` (9 assertions): zero-bonus range unchanged,
    moderate bonus shifts the range up uncapped, max bonus (15, from 7 badges) on a Lv.3-8 area
    pins at the 16 cap, a single-level pool (lo==hi) never crashes under an extreme bonus,
    a late-game area (hi=48) is correctly left alone since 48+15=63 is still under its 96 cap,
    `random_wild()` was hammered against the real `WILD_AREAS` entry with the smallest base
    `hi` (Dusty Cave, hi=7) at max badge_bonus and never exceeded the 14-level cap, all 4
    `main.py` call sites confirmed migrated off the raw formula, and the unrelated trainer-team
    scaling line confirmed untouched. Full 17-script regression suite passes; `py_compile`
    clean across the whole repo.

- [x] **Creatures menu: relearn a forgotten level-up move** — status: done
  - Found half-finished on session start: `git status` showed an uncommitted edit to
    `main.py` adding a "📖  Relearn move" option to the Creatures action menu, with no
    corresponding task.md entry (previous session was cut off before logging or committing).
    Verified it carefully before trusting it, since the action-menu list is index-driven
    (`ac == N`) and a half-finished insertion is exactly the kind of change that silently
    shifts every later branch off by one.
  - Found the implementation itself was actually complete and correct: the new option was
    inserted before "← Back to team" in the `actions` list, the existing `Back` branch was
    correctly renumbered from `ac == 4` to `ac == 5`, and the new `ac == 4` branch was
    inserted in between — matching the list order exactly. Logic: walks
    `CREATURES[name]["moves_learned"]` for every level ≤ the creature's current level,
    collects any move not already known into `eligible`, lets the player pick one (or shows
    a "no forgotten moves" message if the list is empty), then either appends it directly if
    there's a free move slot or prompts which existing move to forget — refreshing `c.pp` for
    the learned move either way.
  - Verified: `python -m py_compile` clean on all 6 core files. Confirmed `MD` (the
    `MOVES` alias used inside the new branch) is already imported in scope at the top of
    `open_creatures()` (line 912) and that `moves_learned` exists on all 38 creatures in
    `data/creatures.py`. Wrote and ran a scoped throwaway test (deleted after use) that
    asserted the menu option, the `ac == 4`/`ac == 5` branch indices, and ast-parsed the file
    cleanly, then exercised the real eligibility-computation logic against live creature data
    (Flamclaw at Lv.30 correctly resolves to `['Scratch', 'Ember', 'Bite', 'Slash',
    'Flamethrower']`, all of which exist in the `MOVES` table). Re-ran the full 17-script
    existing regression suite — all still pass, confirming the action-menu renumbering didn't
    disturb Reorder/Held item/Use item/Rename. `py_compile` clean across the whole repo.

## New tasks — todo

- [ ] **Bag: sort/filter long item lists** — status: todo
  - notes: Bag, Use-item, and held-item menus all render every matching inventory entry as a
    flat list with no grouping. Late-game, with 15-20+ distinct items (berries, balls, stones,
    combat items, cures), this gets hard to scan. Add category grouping (Balls / Healing /
    Status cures / Held items / Stones / Key items) with a sub-menu, or at minimum sort each
    existing list alphabetically instead of dict-insertion-order.

- [ ] **Move PP restore: partial-PP item (Ether/Elixir split)** — status: todo
  - notes: Currently only one PP-restore item type exists (restores all moves by a flat
    amount). Consider adding a cheaper single-move variant (Ether) alongside the existing
    all-moves variant (Elixir) for a real price/utility trade-off, mirroring the Full Heal vs
    Partial Heal pattern already used for the Inn.

- [ ] **Difficulty option at new-game (separate from Nuzlocke)** — status: todo
  - notes: Nuzlocke is an all-or-nothing permadeath toggle. A softer Easy/Normal/Hard
    difficulty pick (affecting wild/trainer level scaling multiplier and/or prize money)
    would let players tune challenge without the permadeath stakes.
