"""
This module maintains the connection to a in-memory database storing the game state.

The database connection is stored as a global variable.
Functions are provided to initialize, manipulate, and query the game state database.
"""

import math
import os
import sqlite3
from dsimulator.defs import ROOT_DIR
import dsimulator.generator as gen
from typing import List, Tuple

con = None
w = None  # weight graph of edges
num_vertex = 0  # number of vertex in game
distance_graph = None  # directed graph for map in the game, calculated in floyd_warshall
pi_graph = None  # parent graph indicating path for SP


def init_game() -> None:
    """Create the schema for the in-memory game state database, then populate it procedurally."""
    global con
    con = sqlite3.connect(":memory:")

    with open(os.path.join(ROOT_DIR, 'DDL.sql')) as fd:
        ddl = fd.read()
    with con:
        con.executescript(ddl)

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

        first_name, last_name = gen.generate_random_names(1)[0]
        cur = con.execute(
            'INSERT INTO home (home_building_id, income_level) VALUES (?, ?)', (vertex_id, income_level))
        con.execute('''INSERT INTO inhabitant (first_name, last_name, home_building_id, loc_building_id, custody, dead, gender)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (first_name, last_name, vertex_id, vertex_id, 0, 0, 'm'))


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


def query_vertex_weight() -> List[List[int]]:
    """
    Set global variable vertex weight graph/array.

    Used for floyd_warshall.
    Should be ran at the start of the game
    """
    global num_vertex
    global w

    cur = con.execute('''
        SELECT count(*) FROM vertex''')
    num_vertex = cur.fetchall()[0]  # the number of vertex

    # weight defaulted to inf
    w = [[math.inf for i in range(num_vertex)] for i in range(num_vertex)]

    for i in range(num_vertex):
        # weight of vertex to itself is 0
        w[i][i] = 0

    cur = con.execute('''
        SELECT * FROM edge''')
    edge_query = cur.fetchall()

    for edge in edge_query:
        # assigning weights based on query results
        w[edge[0]][edge[1]] = edge[2]

    return w


def floyd_warshall(weight: List[List[int]]) -> None:
    """
    Set global distance_graph (weight of shortest path).

    Set global Pi indicating path.
    Should be ran at the start of game after query_vertex_weight.
    """
    global w
    global num_vertex
    global distance_graph
    global pi_graph

    w = weight
    num_vertex = len(w)

    D = w.copy()
    PI = [[None for i in range(num_vertex)] for i in range(num_vertex)]

    # initializing pi_graph by recognizing adjacent vertex
    for i in range(num_vertex):
        for j in range(num_vertex):
            if i != j and w[i][j] < math.inf:
                PI[i][j] = i  # vertex j is adjacent to vertex i

    for k in range(num_vertex):
        tempD = [[0 for i in range(num_vertex)] for i in range(num_vertex)]
        tempPi = [[0 for i in range(num_vertex)] for i in range(num_vertex)]
        for i in range(num_vertex):
            for j in range(num_vertex):
                tempD[i][j] = min(D[i][j], D[i][k] + D[k][j])
                if D[i][j] > D[i][k] + D[k][j]:
                    tempPi[i][j] = PI[k][j]
                else:
                    tempPi[i][j] = PI[i][j]
        D = tempD
        PI = tempPi

    # Sets distance_graph and pi_graph
    distance_graph = D
    pi_graph = PI

    print('D : ')
    for d in D:
        print(d)

    print('PI : ')
    for pi in PI:
        print(pi)


def find_paths(start: int, end: int, time_limit: int) -> List[List[int]]:
    """
    Return a 2D list, each list is a path indicated by a sequence of vertex_ids.

    Args:
    start (int): vertex_id where the path starts
    end (int): vertex_id of the designation
    time_limit (int): within how many minutes
    """
    global num_vertex
    global pi_graph
    global distance_graph
    global w

    result = []

    if distance_graph[start][end] > time_limit:
        return result

    for inter_vertex in range(num_vertex):
        if inter_vertex == start:
            continue
        taken_time = w[start][inter_vertex]

        if taken_time == math.inf:
            continue

        if taken_time < time_limit:
            # Recursively retrieve the subpaths
            sub_paths = find_paths(inter_vertex, end, time_limit - taken_time)
            if sub_paths == []:
                continue
            for sub_path in sub_paths:
                result.append([inter_vertex] + sub_path)

    if start != end and w[start][end] < math.inf:
        result.append([end])

    result.append("re")
    return result
