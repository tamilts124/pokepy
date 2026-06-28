"""
Verify gym/E4 win-loss tracking (Trainer Card breakdown feature).
1. Game.__init__ sets gym_wins/gym_losses/e4_attempts/e4_clears to 0.
2. save_game/load_game round-trip these fields correctly.
3. Old saves (missing the keys) default to 0 via setdefault.
4. challenge_gym increments gym_wins on win, gym_losses on loss.
5. challenge_elite_four increments e4_attempts on confirm, e4_clears on full clear.
6. open_stats source references the new fields.
"""
import sys, os, json, inspect
sys.path.insert(0, os.path.dirname(__file__))

import main as M
from engine.core import save_game, load_game, save_file_path

# Test 1: Game.__init__ defaults
g = M.Game.__new__(M.Game)
M.Game.__init__(g)
assert g.gym_wins == 0 and g.gym_losses == 0
assert g.e4_attempts == 0 and g.e4_clears == 0
print("PASS 1: Game.__init__ sets all four counters to 0")

# Test 2: save/load round trip
g.player_name = "Tester"
g.gym_wins, g.gym_losses, g.e4_attempts, g.e4_clears = 5, 2, 3, 1
TEST_SLOT = 99
save_game(g.player_name, g.town, [], g.inventory, g.badges, g.money,
          slot=TEST_SLOT, rival=g.rival, gym_wins=g.gym_wins,
          gym_losses=g.gym_losses, e4_attempts=g.e4_attempts, e4_clears=g.e4_clears)
loaded = load_game(slot=TEST_SLOT)
assert loaded["gym_wins"] == 5 and loaded["gym_losses"] == 2
assert loaded["e4_attempts"] == 3 and loaded["e4_clears"] == 1
print("PASS 2: save_game/load_game round-trip the four fields correctly")

# Test 3: old save missing the keys defaults to 0
path = save_file_path(TEST_SLOT)
with open(path) as f:
    data = json.load(f)
for k in ("gym_wins", "gym_losses", "e4_attempts", "e4_clears"):
    del data[k]
with open(path, "w") as f:
    json.dump(data, f)
loaded2 = load_game(slot=TEST_SLOT)
assert loaded2["gym_wins"] == 0 and loaded2["gym_losses"] == 0
assert loaded2["e4_attempts"] == 0 and loaded2["e4_clears"] == 0
print("PASS 3: missing keys (old saves) default to 0 via setdefault")

os.remove(path)

# Test 4: source-level checks for increment call sites
src = inspect.getsource(M.Game.challenge_gym)
assert "self.gym_wins = getattr(self, 'gym_wins', 0) + 1" in src
assert "self.gym_losses = getattr(self, 'gym_losses', 0) + 1" in src
print("PASS 4: challenge_gym increments gym_wins on win and gym_losses on loss")

src2 = inspect.getsource(M.Game.challenge_elite_four)
assert "self.e4_attempts = getattr(self, 'e4_attempts', 0) + 1" in src2
assert "self.e4_clears = getattr(self, 'e4_clears', 0) + 1" in src2
print("PASS 5: challenge_elite_four increments e4_attempts on confirm, e4_clears on full clear")

# Test 6: open_stats displays the breakdown
src3 = inspect.getsource(M.Game.open_stats)
assert "gym_wins" in src3 and "gym_losses" in src3
assert "e4_attempts" in src3 and "e4_clears" in src3
print("PASS 6: open_stats references all four counters for display")

print("\nAll gym/E4 stats tests passed.")
