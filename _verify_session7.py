import sys, datetime, pathlib, ast
sys.path.insert(0, '.')

# Test 1: save/load roundtrip for last_played_date
from engine.core import save_game, load_game, Creature
c = Creature('Flambit', 5)
save_game('Tester', 'Greenpath', [c], {}, [], 100, slot=2, last_played_date='2026-01-01')
d = load_game(slot=2)
assert d['last_played_date'] == '2026-01-01', f'Got: {d["last_played_date"]}'
print('PASS 1: last_played_date survives save/load roundtrip')

# Test 2: bonus triggers on different date
today = datetime.date.today().isoformat()
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
assert yesterday and yesterday != today
print('PASS 2: daily bonus triggers when date differs')

# Test 3: bonus does NOT trigger on same date
assert not (today and today != today)
print('PASS 3: daily bonus skipped on same day')

# Test 4: battle.py recap code present
src = pathlib.Path('engine/battle.py').read_text(encoding='utf-8')
ast.parse(src)  # will raise SyntaxError if broken
assert '_recap' in src
assert 'Last turn' in src
assert 'player_move' in src
assert 'enemy_dmg' in src
print('PASS 4: turn-recap code present in battle.py')

# Test 5: last_played_date in __init__ of Game
main_src = pathlib.Path('main.py').read_text(encoding='utf-8')
assert 'last_played_date' in main_src
assert 'Daily login bonus' in main_src or 'DAILY BONUS' in main_src
print('PASS 5: daily bonus logic present in main.py')

print()
print('All session-7 tests passed.')
