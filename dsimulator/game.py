"""
This module maintains the connection to a in-memory database storing the game state.

The database connection is stored as a global variable.
Functions are provided to initialize, manipulate, and query the game state database.
"""

import os
import sqlite3
from dsimulator.defs import ROOT_DIR
import dsimulator.generator as gen
from typing import List, Tuple
import math

con = None
w = None  # weight graph of edges
num_vertex = 0  # number of vertex in game
distance_graph = None  # directed graph for map in the game, calculated in floyd_warshall
pi_graph = None  # parent graph indicating path for SP


def init_game() -> None:
    """Create the schema for the in-memory game state database, then populate it procedurally."""
    global con
    con = sqlite3.connect(":memory:")

    run_script('DDL.sql')

    # Currently just inserting some testing data.
    # TODO: Implement procedural generation for the game world.
    with con:
        cur = con.executescript(gen.generate_map())
        # cur = con.execute('INSERT INTO vertex (x, y) VALUES (1, 2)')
        # vertex_id = cur.lastrowid
        vertex_id = 0
        con.execute(
            'INSERT INTO building (building_id, building_name, lockdown) VALUES (?, ?, ?)', (vertex_id, 'Home', 0))

        cur = con.execute(
            'INSERT INTO income_range (low, high) VALUES (1000, 2000)')
        income_level = cur.lastrowid

        # first_name, last_name = gen.generate_random_names(1)[0]
        first_name, last_name = 'John', 'Doe'
        cur = con.execute(
            'INSERT INTO home (home_building_id, income_level) VALUES (?, ?)', (vertex_id, income_level))
        con.execute('''INSERT INTO inhabitant (first_name, last_name, home_building_id, loc_building_id, custody, dead, gender)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (first_name, last_name, vertex_id, vertex_id, 0, 0, 'm'))

        gen.generate_home(con)
        gen.generate_workplace(con)
        # con.execute(gen.generate_inhabitant(con))


def close_game() -> None:
    """Close the connection to game state database."""
    global con
    con.close()
    con = None


SAVE_DIR = os.path.expanduser('~/.dsimulator')
SAVE_LIST = os.path.join(SAVE_DIR, "save.db")


def to_save_path(save_id: int) -> str:
    """Convert the save slot id to the full path to the database."""
    return os.path.join(SAVE_DIR, str(save_id) + '.db')


def create_save_list() -> None:
    """Create the database that stores the list of save slots if it does not exist."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    list_con = sqlite3.connect(SAVE_LIST)
    with list_con:
        list_con.execute('''CREATE TABLE IF NOT EXISTS save(
                                save_id   INTEGER NOT NULL,
                                timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                          PRIMARY KEY(save_id)
                            )''')
    list_con.close()


def list_save() -> List[Tuple[int, str]]:
    """Get a list of the save slots."""
    create_save_list()
    list_con = sqlite3.connect(SAVE_LIST)
    cur = list_con.execute('''  SELECT save_id, datetime(timestamp)
                                  FROM save
                              ORDER BY timestamp DESC''')
    result = cur.fetchall()
    list_con.close()
    return result


def read_save(save_id: int) -> None:
    """Read the saved database into the in-memory database."""
    global con
    con = sqlite3.connect(":memory:")
    save_con = sqlite3.connect(to_save_path(save_id))
    with save_con:
        save_con.backup(con)
    save_con.close()


def write_save(save_id: int = None) -> None:
    """Write the in-memory database into the save file (on-disk database)."""
    global con
    create_save_list()

    list_con = sqlite3.connect(SAVE_LIST)
    with list_con:
        if save_id is None:
            cur = list_con.execute('INSERT INTO save DEFAULT VALUES')
            save_id = cur.lastrowid
        else:
            list_con.execute('REPLACE INTO save (save_id) VALUES (?)', (save_id,))
    list_con.close()

    save_con = sqlite3.connect(to_save_path(save_id))
    with save_con:
        con.backup(save_con)
    save_con.close()


def delete_save(save_id: int) -> None:
    """Delete the save slot."""
    list_con = sqlite3.connect(SAVE_LIST)
    with list_con:
        list_con.execute('DELETE FROM save WHERE save_id = ?', (save_id,))
    list_con.close()

    os.remove(to_save_path(save_id))


def list_inhabitant() -> Tuple[Tuple[str, ...], List[Tuple]]:
    """Return all inhabitants' attribute names that are known by the player and the respective values."""
    cur = con.execute('''SELECT inhabitant_id, first_name, last_name, h.building_name, workplace_id, custody, dead, gender
                           FROM inhabitant
                                JOIN building AS h
                                ON home_building_id = building_id''')
    return ('inhabitant_id', 'first_name', 'last_name', 'home_building_name', 'workplace_id', 'custody', 'dead', 'gender'), \
        cur.fetchall()


def list_vertex() -> List[Tuple[int, int]]:
    """Return a list of coordinates for all vertices."""
    cur = con.execute('SELECT x, y FROM vertex')
    return cur.fetchall()


def list_edge() -> List[Tuple[int, int, int, int, int]]:
    """
    Return a list of start-end coordinates and cost for all edges in one direction.

    As the map edges are added twice for two directions, only those with start < end will be considered.
    """
    cur = con.execute('''SELECT s.x, s.y, e.x, e.y, cost_min
                           FROM edge
                                JOIN vertex AS s
                                ON start = s.vertex_id
                                JOIN vertex AS e
                                ON end = e.vertex_id
                          WHERE start < end''')
    return cur.fetchall()


def list_building() -> List[Tuple[int, int]]:
    """Return a list of coordinates for all buildings."""
    cur = con.execute('''SELECT x, y
                           FROM building
                           JOIN vertex
                                ON building_id=vertex_id''')
    return cur.fetchall()


def lockdown(building_id: int) -> None:
    """Set given building to lockdown."""
    con.execute('''
        UPDATE building
        SET lockdown = 1
        WHERE building_id = {0};'''.format(building_id))


def create_lockdown_buidling_view() -> None:
    """Create a view of building that only contains building under lockdown."""
    con.execute('''
        CREATE VIEW lockdown_building AS
            SELECT building_id
            FROM building
            WHERE lockdown = 1;
                ''')


def query_inhabitant_relationship(subject_id: int) -> List[Tuple]:
    """Return the list of inhabitants having relations with subject."""
    cur = con.execute('''
        SELECT object_id, description
        FROM relationship
        WHERE subject = {0}'''.format(subject_id))
    return cur.fetchall()


def modify_suspect(inhabitant_id: int) -> None:
    """Set/unset given inhabitant in suspect."""
    cur = con.execute('''
        SELECT *
        FROM suspect
        WHERE inhabitant_id = {0}'''.format(inhabitant_id))
    # not sure about the format of query result
    # will empty query return empty list?
    if cur.fetchall() == []:
        con.execute('''
            INSERT INTO suspect
            VALUES ({0})'''.format(inhabitant_id))
    else:
        con.execute('''
            DELETE FROM suspect
            WHERE inhabitant_id = {0}'''.format(inhabitant_id))


def query_shortest_path() -> None:
    """Get the shortest path between all vertex pairs in a temp table `dist`."""
    with con:
        run_script('shortest_path.sql')


def init_loc_time() -> None:
    """Initialize the `src_dst` and `loc_time` table."""
    with con:
        run_script('init_loc_time.sql')


def query_loc_time() -> None:
    """Insert the location-time tuples into `loc_time`, specifying paths that satisfy the constraints given in `src_dst`."""
    with con:
        run_script('query_loc_time.sql')


def query_loc_time_inhabitant() -> None:
    """Insert the location-time tuples of all inhabitants into `loc_time`."""
    query_shortest_path()

    init_loc_time()

    # Currently, the inhabitant may leave home after 7:00 (420 mins)
    # and must return home before 19:00 (1140 mins).
    # Also only those with a workplace is considered.
    with con:
        con.execute('''INSERT INTO src_dst (inhabitant_id, src, dst, t_src, t_dst)
                           WITH t AS(
                               SELECT inhabitant_id, home_building_id, workplace_building_id, arrive_min, leave_min
                                 FROM inhabitant
                                      JOIN workplace
                                      USING(workplace_id)
                                      JOIN occupation
                                      USING(occupation_id)
                                WHERE workplace_id IS NOT NULL
                           )
                           SELECT inhabitant_id, home_building_id, workplace_building_id, 420, arrive_min
                             FROM t
                            UNION
                           SELECT inhabitant_id, workplace_building_id, home_building_id, leave_min, 1140
                             FROM t''')

    query_loc_time()


def run_script(file_name: str) -> None:
    with open(os.path.join(ROOT_DIR, file_name)) as fd:
        script = fd.read()
    with con:
        con.executescript(script)


def test() -> None:
    """General testing function."""

    cur = con.execute('SELECT * FROM income_range')
    print('income_range:')
    print(cur.fetchall())

    cur = con.execute('SELECT * FROM occupation')
    print('occupation:')
    print(cur.fetchall())

    cur = con.execute('SELECT * FROM building')
    print('building:')
    print(cur.fetchall())

    cur = con.execute('SELECT * FROM workplace')
    print('workplace:')
    print(cur.fetchall())

    query_shortest_path()
    print('1 -> 4 less than 100 mins:')
    print(query_via_point_constraint(1, 4, 100))

    return

    query_loc_time_inhabitant()
    cur = con.execute('SELECT * FROM dist LIMIT 10')
    print('dist:')
    print(cur.fetchall())
    cur = con.execute('SELECT * FROM loc_time LIMIT 10')
    print('loc_time:')
    print(cur.fetchall())


def user_inhabitant_query(income_lo=0, income_hi=math.inf, occupation=None, gender="gender", dead=None, home_building_name="home_building_name", custody=None, suspect=None):
    """Returns the query result inputted by the player
    """
    global con
    required_tables = ""
    required_predicate = ""
    if income_lo != 0 or income_hi != math.inf or occupation != None:
        required_tables = "NATURAL JOIN workplace NATURAL JOIN occupation "
        if income_hi != math.inf:
            required_predicate = required_predicate + " AND income >= " + str(income_lo) + " AND income <= " + str(income_hi)
        else:
            required_predicate = required_predicate + " AND income >= " + str(income_lo)

        if occupation != None:
            required_predicate = required_predicate + " AND occupation_name = '{0}'".format(occupation)

    if dead == False:
        required_predicate = required_predicate + " AND dead = 0"
    elif dead == True:
        required_predicate = required_predicate + " AND dead = 1"
    if custody == False:
        required_predicate = required_predicate + " AND custody = 0"
    elif custody == True:
        required_predicate = required_predicate + " AND custody = 0"

    if suspect == True:
        required_predicate = required_predicate + " AND EXISTS(SELECT * FROM suspect WHERE suspect.inhabitant_id = inhabitant.inhabitant_id)"
    elif suspect == False:
        required_predicate = required_predicate + " AND NOT EXISTS(SELECT * FROM suspect WHERE suspect.inhabitant_id = inhabitant.inhabitant_id)"

    '''
    print("""
                SELECT inhabitant_id, name, home.building_name, workplace_id, custody, dead, gender
                FROM inhabitant NATURAL JOIN building AS home """ + required_tables +
                """
                WHERE gender = {0} AND home_building_name = '{1}'""".format(gender, home_building_name) + required_predicate)
    '''
    cur = con.execute("""
                SELECT inhabitant_id, name, home.building_name, workplace_id, custody, dead, gender
                FROM inhabitant NATURAL JOIN building AS home """ + required_tables +
                      """
                WHERE gender = {0} AND home_building_name = '{1}'""".format(gender, home_building_name) + required_predicate)
    return cur.fetchall()


def query_via_point_constraint(start: int, end: int, mins: int):
    """
    List all the vertices v where the path start -> v -> end is not longer than mins.

    query_shortest_path() must be run before calling this function.
    """

    cur = con.execute('''SELECT a.dst
                           FROM dist AS a
                                JOIN dist AS b
                                ON a.dst = b.src
                          WHERE a.src = ? AND b.dst = ? AND a.d + b.d <= ?''',
                      (start, end, mins))
    return cur.fetchall()


# TODO: Test this with inhabitant data.


def query_witness_count(vertex_id: int):
    """
    List the name and the number of times that each inhabitant has been seen in a vertex.

    query_loc_time() must be run before calling this function.
    """
    cur = con.execute('''SELECT first_name, last_name, COUNT(*) AS c
                           FROM loc_time AS a
                                JOIN inhabitant
                                USING(inhabitant_id)
                                JOIN loc_time AS b
                                ON a.inhabitant_id <> b.inhabitant_id
                                   AND a.vertex_id = b.vertex_id
                                   AND ((a.arrive <= b.arrive AND b.arrive <= a.leave)
                                        OR (a.arrive <= b.leave AND b.leave <= a.leave))
                          WHERE a.vertex_id = ?
                       GROUP BY a.inhabitant_id
                       ORDER BY c DESC''',
                      vertex_id)
    return cur
