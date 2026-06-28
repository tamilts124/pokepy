# Pokepy Task List

## Status legend
todo / in-progress / done / tested / blocked

## Session 1 — Audit (2025-06)
Fresh repo, single "initial commit". All files compile and import cleanly.
Game is structurally complete (battle, gyms, Elite Four, rival, held items, abilities, save/load).

### Bugs found during audit

- [x] **Save omits achievements + season** — status: in-progress
  - `Game.save()` calls `save_game(...)` but never passes `achievements=self.achievements` or `season=self.season`.
  - Load path in `main()` also doesn't restore them to the `Game` object.
  - Fix: pass both args in `save()`, restore both on load.

- [ ] **`battle100` achievement fires on every level-up, not at 100 battles** — status: todo
  - Line 119: fires inside `if etype == "levelup"` — should check `self.steps >= 100`.

- [ ] **Achievements `first_catch`, `first_fish`, `grotto_found`, `rival_winner`, `rich`, `team_full` are never triggered** — status: todo
  - `_check_achievement` is only called for `battle100` and `first_evolution`.
  - Each needs a call at the right moment:
    - `first_catch` → after a successful catch in `explore()`
    - `first_fish` → after a fishing catch
    - `grotto_found` → when grotto is first discovered/entered
    - `rival_winner` → after `rival.player_wins >= 3`
    - `rich` → when `self.money >= 10000`
    - `team_full` → when team reaches 6 members

- [ ] **Fishing has no UI** — status: todo
  - `FISH_OLD_ROD`, `FISH_GOOD_ROD` tables exist. `Old Rod` starts in inventory.
  - No "Go Fishing" option in town menu. Players can't fish at all.

- [ ] **Grottos have no UI** — status: todo
  - `GROTTOS` data (8 towns with creature pools + items) exists and is imported.
  - No option in town menu or explore to enter a grotto.
  - `grotto_found` achievement is also unreachable without this.

- [ ] **Seasonal wilds/berries unused in explore()** — status: todo
  - `SEASONAL_WILDS` and `SEASONAL_BERRY` are imported but `explore()` never applies them.
  - Wild pool should be augmented with seasonal creatures.
  - Seasonal berry should occasionally appear as hidden loot in explore.

- [ ] **Achievements not saved/loaded** — status: todo (blocked on save fix above)
  - Even after fixing the save args, `main()` load path needs to restore `g.achievements`.

---

## Tasks — planned features / improvements

- [ ] **Post-game content** — status: todo
  - After Champion: allow rematch of Elite Four (scaled up), Champion title on trainer card.

- [ ] **Pokédex / creature registry** — status: todo
  - Track which creatures have been seen and caught. Show in a menu option.

- [ ] **Battle narration improvements** — status: todo
  - Show enemy HP bar numerically (current/max or %) so player has more information.
  - Flash "CRITICAL HIT!" more visibly.

- [ ] **In-battle item use expanded** — status: todo
  - Allow X-items (X Attack etc.) to be used from the bag mid-battle.
  - Currently `boost` type items show "Use this during a battle" but aren't implemented in-battle.

- [ ] **Move PP display in battle** — status: todo
  - When choosing a move, show current PP/max so player knows what's running low.

- [ ] **Nature system** — status: todo
  - Each creature could have a nature (Adamant, Timid, etc.) that gives +10%/-10% to two stats.
  - Add at creature creation (random), display in creature card.
