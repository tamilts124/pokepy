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

- [ ] **Critical hit flash** — status: todo
  - Make "Critical hit!" stand out more: bold + bright colour + own line.
  - notes: currently inline in gray — easy miss mid-battle.

- [ ] **Pokédex / creature registry** — status: in-progress
  - Track seen + caught creatures; show in a 📖 Pokédex menu from town.
  - notes: needs `seen` and `caught` sets on Game, population on encounter/catch, and a display menu.

- [ ] **In-battle X-item use** — status: todo
  - X Attack / X Defense / X Speed usable from Bag during battle (not just "use this in battle" message).
  - notes: items already in ITEMS dict as "boost" type; need in-battle branch in battle.py bag handler.

- [ ] **Post-game content** — status: todo
  - After Champion: Elite Four rematch at lv 70+, Champion title on Trainer Card.

- [ ] **Pokédex completion reward** — status: todo
  - Unlock a Master Ball or other prize when player catches all creatures.
  - notes: natural companion to Pokédex feature above.
