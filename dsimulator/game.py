"""
This module maintains the connection to a in-memory database storing the game state.
The database connection is stored as a global variable.
Functions are provided to initialize, manipulate, and query the game state database.

TODO: Implement load/save.
"""

import math
import os
import sqlite3
from dsimulator.defs import ROOT_DIR
from typing import List, Tuple

con = None
w = None  # weight graph of edges
num_vertex = 0  # number of vertex in game
distance_graph = None  # directed graph for map in the game, calculated in floyd_warshall
pi_graph = None  # parent graph indicating path for SP


def init_game():
    """Create the schema for the in-memory game state database, then populate it procedurally."""
    global con
    con = sqlite3.connect(":memory:")

    with open(os.path.join(ROOT_DIR, 'DDL.sql')) as fd:
        sqlFile = fd.read()
    sqlCmds = sqlFile.split(';')
    with con:
        for c in sqlCmds:
            con.execute(c)

    # Currently just inserting some testing data.
    # TODO: Implement procedural generation for the game world.
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


def query_inhabitant() -> Tuple[Tuple[str, ...], List[Tuple]]:
    """Return known inhabitant attribute names and values"""
    cur = con.execute('''SELECT inhabitant_id, name, h.building_name, workplace_id, custody, dead, gender
                         FROM inhabitant
                              JOIN building AS h
                              ON home_building_id = building_id''')
    return ('inhabitant_id', 'name', 'home_building_name', 'workplace_id', 'custody', 'dead', 'gender'), cur.fetchall()


def lockdown(building_id):
    """Set given building to lockdown"""
    con.execute('''
        UPDATE building
        SET lockdown = 1
        WHERE building_id = {0};'''.format(building_id))

def create_lockdown_buidling_view():
    con.execute('''
        CREATE VIEW lockdown_building AS
            SELECT building_id
            FROM building
            WHERE lockdown = 1;
                ''')


def query_inhabitant_relationship(subject_id):
    """Returns list of inhabitants having relations with subject"""
    cur = con.execute('''
        SELECT object_id, description
        FROM relationship
        WHERE subject = {0}'''.format(subject_id))
    return cur.fetchall()


def modify_suspect(inhabitant_id):
    """Sets/unsets given inhabitant in suspect"""
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


def query_vertex_weight():
    # Sets global variable vertex weight graph/array
    # used for floyd_warshall
    # Should be ran at the start of the game
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


def floyd_warshall(weight):
    """ sets global distance_graph (weight of shortest path)
        sets global Pi indicating path
        should be ran at the start of game after query_vertex_weight
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


def find_paths(start, end, time_limit):
    """ Returns a 2D list, each list is a path indicated by a sequence of vertex_ids

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
