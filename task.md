# Pokepy Task List

## Status legend
todo / in-progress / done / tested / blocked

## Session 1 — Audit (2025-06)
Fresh repo, single "initial commit". All files compile and import cleanly.
Game is structurally complete (battle, gyms, Elite Four, rival, held items, abilities, save/load).

### Bugs found during audit

- [x] **Save omits achievements + season** — status: done
  - Fixed in commit e75f454: both `achievements` and `season` now saved/restored.

- [x] **`battle100` achievement fires on every level-up, not at 100 battles** — status: done
  - Fixed in commit e75f454: now correctly checks battle count.

- [x] **Achievements `first_catch`, `first_fish`, `grotto_found`, `rival_winner`, `rich`, `team_full` are never triggered** — status: done
  - Fixed in commit c9ed4ea: all achievement triggers wired at correct game moments.

- [x] **Fishing has no UI** — status: done
  - `go_fishing()` method written (prev session) and wired into town_loop menu (this session).
  - 🎣 Go Fishing appears in every town that has fish pools.

- [x] **Grottos have no UI** — status: done
  - `explore_grotto()` method written (prev session) and wired into town_loop menu (this session).
  - 🕳 Hidden Grotto appears in 8 towns that have grotto data.

- [x] **Seasonal wilds/berries unused in explore()** — status: done
  - Fixed in commit 05c50c1: seasonal creatures spawn at 30% in season areas; seasonal berry added to hidden loot pool.

- [x] **Achievements not saved/loaded** — status: done
  - Fixed together with save fix (commit e75f454).

---

## Tasks — planned features / improvements

- [ ] **Move PP display in battle** — status: todo
  - When choosing a move, show current PP/max PP so player knows what's running low.
  - notes: low-effort, high-value UX improvement.

- [ ] **Enemy HP bar shows number** — status: todo
  - Show foe HP as `??? / ???` or `~60%` so player has information to strategize.
  - notes: currently foe HP bar only shows a visual bar with no numbers.

- [ ] **Nature system** — status: todo
  - Each creature gets a random nature (Adamant, Timid, Bold, etc.) that gives +10%/-10% to two stats.
  - Add at creature creation, display on creature card and battle stat screen.
  - notes: adds meaningful team-building depth.

- [ ] **Pokédex / creature registry** — status: todo
  - Track which creatures have been seen (encountered) and caught.
  - Show in a 📖 Pokédex menu option from town.
  - notes: core Pokémon QoL; motivates exploration/catching.

- [ ] **In-battle X-item use** — status: todo
  - Allow X Attack, X Defense, X Speed (new shop items) to be used from Bag during battle.
  - Currently boost items show "Use this during a battle" but are not implemented in-battle.
  - notes: add items to shop data, add in-battle handler in battle.py.

- [ ] **Post-game content** — status: todo
  - After Champion: Elite Four rematch (scaled to lv 70+), Champion title on Trainer Card.
  - notes: gives end-game players something to do.

- [ ] **Critical hit flash** — status: todo
  - Make "CRITICAL HIT!" stand out more visually (bold, bright red, extra newlines).
  - notes: tiny polish but feels much better in play.
