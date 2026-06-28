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

- [ ] **Post-game content** — status: todo
  - After Champion: Elite Four rematch at lv 70+, Champion title on Trainer Card.

- [ ] **Pokédex entry detail view** — status: todo
  - From the Pokédex list, select a caught/seen creature to view its full dex entry (types, base stats,
    abilities, evolution line). Currently the list only shows name + type.
  - notes: natural follow-up now that the Pokédex list itself is wired in and working.
