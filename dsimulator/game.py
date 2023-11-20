import os
import sqlite3
from dsimulator.defs import ROOT_DIR

con = None


def init_game():
    global con
    con = sqlite3.connect(":memory:")

    with open(os.path.join(ROOT_DIR, 'DDL.sql')) as fd:
        sqlFile = fd.read()
    sqlCmds = sqlFile.split(';')
    with con:
        for c in sqlCmds:
            con.execute(c)

    with con:
        cur = con.execute('INSERT INTO vertex (x, y) VALUES (1, 2)')
        vertex_id = cur.lastrowid
        con.execute(
            'INSERT INTO building (building_id, building_name, lockdown) VALUES (?, ?, ?)', (vertex_id, 'Home', 0))

        cur = con.execute(
            'INSERT INTO income_range (low, high) VALUES (1000, 2000)')
        income_level = cur.lastrowid

        cur = con.execute(
            'INSERT INTO home (home_building_id, income_level) VALUES (?, ?)', (vertex_id, income_level))
        con.execute('INSERT INTO inhabitant (name, home_building_id, loc_building_id, custody, dead) VALUES (?, ?, ?, ?, ?)',
                    ('John Doe', vertex_id, vertex_id, 0, 0))


def query_inhabitant():
    cur = con.execute('''SELECT inhabitant_id, name, h.building_name, workplace_id, custody, dead, gender
                         FROM inhabitant
                              JOIN building AS h
                              ON home_building_id = building_id''')
    return ('inhabitant_id', 'name', 'home_building_name', 'workplace_id', 'custody', 'dead', 'gender'), cur.fetchall()
