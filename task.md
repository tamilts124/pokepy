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
  - Session 2025-06 (this session): resumed from a crash mid-task. Found the previous session had:
    - Implemented `Game.seen`/`Game.caught` sets, save/load wiring, `_check_pokedex_completion`,
      and a full `open_pokedex()` display method — but left it **uncommitted**, and **not wired into
      the town menu** (matches task.md's old "in-progress" note).
    - Also left a corrupted line in `engine/core.py` (`data[\"version\"] = 1` — literal backslashes,
      a syntax error) that would have crashed on any legacy (pre-version) save file migration.
    - The `"pokedex_complete"` key was referenced by `_check_pokedex_completion()` but never defined
      in the `ACHIEVEMENTS` dict, so it would have silently failed to announce/record.
  - Fixed in this session: repaired the syntax error in `core.py`, added the missing
    `pokedex_complete` achievement entry, and added a `📖  Pokédex` option to the town menu wired to
    `open_pokedex()`. Verified via `py_compile` and an actual run (entered the menu, paged through
    the Pokédex list, confirmed no crash).
  - notes: Pokédex completion reward (Master Ball) logic already existed in `_check_pokedex_completion`
    — see next task, now also effectively done as a side effect of this fix.

- [x] **Pokédex completion reward** — status: done
  - `_check_pokedex_completion()` (in main.py) grants a free Master Ball + fires the
    `pokedex_complete` achievement once `len(self.caught) >= len(CREATURES)`. Fixed alongside the
    Pokédex task above (achievement entry was missing; now added).

- [x] **In-battle X-item use** — status: done
  - On inspection, X Attack/Defense/Sp.Atk/Sp.Def/Speed were already fully wired into the battle Bag
    menu (engine/battle.py `idata["type"] == "boost"` branch) — not a stub, contrary to the old
    task note. However, found a real bug while verifying: X Speed's boost was applied to the
    per-battle `boosts` dict but never actually consulted anywhere — `Creature.effective_spd()`
    (used for turn-order speed comparisons) only read persistent stat *stages*, so buying and using
    X Speed printed "Speed rose!" but had **zero effect on turn order** — a silent no-op.
  - Fixed by mirroring the existing X Defense/Sp.Def pattern: added a `_xspd_boost` attribute on
    Creature, set it in the boost-item branch, reset it at battle start and at every switch-in
    (3 sites), and applied it inside `effective_spd()` in engine/core.py.
  - Verified with an isolated unit check (`effective_spd()` increases correctly when `_xspd_boost`
    is set) plus a full `py_compile` pass on all touched files.

- [x] **Post-game content** — status: done
  - After becoming Champion: fires the previously-dead `"champion"` achievement (it was defined in
    `ACHIEVEMENTS` but never triggered anywhere — another stale/unfired achievement, same class of
    bug as the Pokédex one above), sets a new persistent `Game.is_champion` flag (saved/loaded via
    `save_game`/`load_game`), and shows a `★  Champion  ★` title line on the Trainer Card.
  - Elite Four Rematch: once `is_champion` is True, the Champion Road menu option becomes
    "🏆  Elite Four Rematch" instead of "Challenge Elite Four", and every Elite Four member's level
    is scaled to `max(70, original_level + 20)` for the fight (verified: all 4 challengers land at
    70+, Champion Aria's team still hits hardest at 76–80). Rematches don't re-fire the achievement
    or the post-Elite-Four rival cutscene (first-clear only).
  - Verified via `py_compile`, an isolated scaling-logic check, and a Game-instantiation smoke test.

- [x] **Pokédex entry detail view** — status: done
  - The Pokédex list entries are now selectable menu options (instead of plain `print()` lines).
    Selecting a seen-or-caught creature opens `_show_pokedex_entry()`: shows types and description
    always; if caught, also shows a full base-stat bar chart, ability, and evolution target/level
    (or "(final form)"); if only seen, shows a teaser prompting the player to catch one. Unseen
    ("???") entries are still listed but selecting one is a no-op (nothing to reveal yet).
  - Verified via `py_compile` and a direct call to `_show_pokedex_entry()` for both the
    caught and seen-only states (confirmed correct branch content for each).

- [x] **Rival rematch / extended post-game** — status: done
  - Added `run_rival_rematch()` in engine/rival.py: a repeatable post-game battle against the rival's
    final-encounter team, scaled the same way as the Elite Four rematch (`max(70, lv + 20)` per
    creature). Available from the Champion Road town menu as "⚡  Rival Rematch (<name>)" once
    `is_champion` is True and a story rival encounter isn't currently pending in that town (falls
    back correctly behind any still-pending scripted encounter). Updates the player/rival win-loss
    score and grants ₽2000 on a win, but does not touch `battles_done` or re-fire story achievements
    — it's purely a repeatable post-game fight, separate from the one-time 5-encounter arc.
  - Verified via `py_compile`, a scaling-logic check (confirmed all 6 rematch-team members land at
    70+), and a direct test of the town-menu option-building logic (confirms the option appears
    once champion, and correctly defers to a still-pending story encounter when one exists).

- [ ] **Battle log / replay** — status: todo
  - Let the player view a short scrollback of the last few battle messages (or a post-battle
    turn-by-turn replay) — currently messages scroll past quickly with `slow_print` and there's no
    way to review what just happened beyond the existing end-of-battle summary.
