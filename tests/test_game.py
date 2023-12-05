"""Run some tests on the game module."""

import dsimulator.game as game

game.init_game()

game.next_day()
game.next_day()
game.next_day()
print(game.con.execute("SELECT count(distinct building_id) FROM lockdown_building").fetchall())
print(game.con.execute("SELECT * FROM victim").fetchall())
print(game.con.execute("select * from commonality").fetchall())

cur = game.con.execute('SELECT * FROM income_range')
print('income_range:')
print(cur.fetchall())

cur = game.con.execute('SELECT * FROM occupation')
print('occupation:')
print(cur.fetchall())

cur = game.con.execute('SELECT * FROM building')
print('building:')
print(cur.fetchall())

cur = game.con.execute('SELECT * FROM workplace')
print('workplace:')
print(cur.fetchall())

game.query_shortest_path()
print('1 -> 4 less than 100 mins:')
print(game.query_via_point_constraint(1, 4, 100))

game.query_loc_time_inhabitant()
cur = game.con.execute('SELECT * FROM dist LIMIT 10')
print('dist:')
print(cur.fetchall())
cur = game.con.execute('SELECT * FROM loc_time LIMIT 10')
print('loc_time:')
print(cur.fetchall())
