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

con = None
day = 0
resig_day = 15


def init_game() -> None:
    """Create the schema for the in-memory game state database, then populate it procedurally."""
    global con
    global day
    global resig_day

    # check_same_thread=False is necessary for allowing query by UI handler.
    # I am not sure why the UI is still multithreaded even though I turned on manual callback management.
    con = sqlite3.connect(":memory:", check_same_thread=False)

    run_script('DDL.sql')

    gen.generate_map(con)
    gen.generate_home(con)
    gen.generate_workplace(con)
    gen.generate_inhabitants_and_relationships(con)
    gen.generate_test_killer(con)
    gen.init_status(con)
    init_commonality_view()
    init_kill_trigger()
    create_lockdown_building_view()
    create_modified_edge_view()


def next_day() -> None:
    """End the turn and proceed to the next day."""
    global day
    day += 1

    query_shortest_path()
    print('Queried `dist`')
    query_loc_time_inhabitant()
    print('Queried `loc_time`')
    victim = select_victim()
    print('Selected the victim')
    if victim is not None:
        kill_inhabitant(select_victim())
    print('Victim killed')


def end_game_condition(examined_inhabitant: int = None) -> Tuple[bool, bool]:
    """Return whether if game has ended and if the player has won."""
    global day
    global resig_day
    game_end = False
    game_win = False
    if day >= resig_day:
        game_end = True
    if examined_inhabitant is not None:
        killer_id = con.execute("SELECT killer_id FROM status").fetchone()[0]
        if examined_inhabitant == killer_id:
            game_win = True
    return (game_end, game_win)


def kill_inhabitant(victim: int) -> None:
    """Insert `(victim_id, scene_vertex_id, min_of_death)` into `victim` table."""
    global con
    global day
    with con:
        con.execute("INSERT INTO victim VALUES (?,?,?,?)", (victim[0], day, victim[2], victim[1]))


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

    # check_same_thread=False is necessary for allowing query by UI handler.
    # I am not sure why the UI is still multithreaded even though I turned on manual callback management.
    con = sqlite3.connect(":memory:", check_same_thread=False)

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


def list_building() -> List[Tuple[int, int, int, str]]:
    """Return a list of basic building information for all buildings."""
    cur = con.execute('''SELECT x, y, building_id, building_name
                           FROM building
                           JOIN vertex
                                ON building_id=vertex_id''')
    return cur.fetchall()


def query_building_summary(building_id: int) -> Tuple[str, int, int]:
    """Get the name and lockdown status of a building and whether it is a home."""
    cur = con.execute('SELECT building_name, lockdown FROM building WHERE building_id = ?', (building_id,))
    building_name, lockdown = cur.fetchone()
    cur = con.execute('SELECT COUNT(*) FROM home WHERE home_building_id = ?', (building_id,))
    home = cur.fetchone()[0]
    return building_name, lockdown, home


def query_home_income(building_id: int) -> Tuple[int, int, int]:
    """Get the income range of a home building."""
    cur = con.execute('''SELECT low, high
                           FROM home
                                JOIN
                                income_range
                                USING(income_level)
                          WHERE home_building_id = ?''',
                      (building_id,))
    return cur.fetchone()


def query_workplace_occupation(building_id: int) -> Tuple[Tuple[str, ...], Tuple]:
    """List the occupations for the occupations in a building."""
    cur = con.execute('''SELECT occupation_name, income, arrive_min, leave_min
                           FROM workplace
                                JOIN occupation
                                USING(occupation_id)
                          WHERE workplace_building_id = ?''',
                      (building_id,))
    return ('occupation_name', 'income', 'arrive_min', 'leave_min'), \
        cur.fetchall()


def lockdown(building_id: int) -> None:
    """Set given building to lockdown."""
    con.execute('''
        UPDATE building
        SET lockdown = 1
        WHERE building_id = {0};'''.format(building_id))


def create_lockdown_building_view() -> None:
    """Create a view of building that only contains building under lockdown."""
    con.execute('''
        CREATE VIEW lockdown_building AS
            SELECT building_id
            FROM building
            WHERE lockdown = 1;
                ''')


def create_modified_edge_view() -> None:
    """Create edge adjusted for lockdown buildings."""
    con.execute('''
                CREATE VIEW modified_edge AS
                    SELECT *
                    FROM edge
                    WHERE NOT EXISTS (SELECT *
                        FROM lockdown_building
                        WHERE `start` = building_id OR `end` = building_id
                    )
                ''')


def query_inhabitant_relationship(subject_id: int) -> List[Tuple]:
    """Return the list of inhabitants having relations with subject."""
    cur = con.execute('''
        SELECT first_name, last_name, description
          FROM relationship
               JOIN inhabitant
               ON inhabitant_id = object_id
         WHERE subject_id = {0}'''.format(subject_id))
    return cur.fetchall()


def modify_suspect(inhabitant_id: int) -> None:
    """Set/unset given inhabitant in suspect."""
    cur = con.execute('''
        SELECT *
        FROM suspect
        WHERE inhabitant_id = {0}'''.format(inhabitant_id))
    # not sure about the format of query result
    # will empty query return empty list?
    if cur.fetchall() is None:
        con.execute('''
            INSERT INTO suspect
            VALUES ({0})'''.format(inhabitant_id))
    else:
        con.execute('''
            DELETE FROM suspect
            WHERE inhabitant_id = {0}'''.format(inhabitant_id))

# TODO: Exclude buildings under lockdown.


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


def init_commonality_view() -> None:
    """Initialize the view for victims' common attributes."""
    with con:
        run_script('victim_common_attribute.sql')


def init_kill_trigger() -> None:
    """Add the trigger to kill the inhabitant after insertion on `victim`."""
    with con:
        run_script('kill_trigger.sql')


def query_loc_time_inhabitant() -> None:
    """
    Insert the location-time tuples of all inhabitants into `loc_time`.

    query_shortest_path() must be run before calling this function.
    """
    init_loc_time()

    # Currently, the inhabitant may leave home after 7:00 (420 mins)
    # and must return home before 19:00 (1140 mins).
    # Also only those with a workplace is considered.

    # adjusted to remove dead inhabitant from query
    with con:
        con.execute('''INSERT INTO src_dst (inhabitant_id, src, dst, t_src, t_dst)
                           WITH t AS(
                               SELECT inhabitant_id, home_building_id, workplace_building_id, arrive_min, leave_min
                                 FROM inhabitant
                                      JOIN workplace
                                      USING(workplace_id)
                                      JOIN occupation
                                      USING(occupation_id)
                                WHERE workplace_id IS NOT NULL AND dead <> 1
                           )
                           SELECT inhabitant_id, home_building_id, workplace_building_id, 420, arrive_min
                             FROM t
                            UNION
                           SELECT inhabitant_id, workplace_building_id, home_building_id, leave_min, 1140
                             FROM t''')

    query_loc_time()


def run_script(file_name: str) -> None:
    """Execute the script file given the file name."""
    with open(os.path.join(ROOT_DIR, file_name)) as fd:
        script = fd.read()
    with con:
        con.executescript(script)


def query_inhabitant(income_lo: int = None, income_hi: int = None, occupation: str = None, gender: str = None, dead: bool = None, home_building_id: int = None, home_building_name: str = None, workplace_building_id: int = None, workplace_building_name: str = None, custody: bool = None, suspect: bool = None) -> Tuple[Tuple[str, ...], Tuple]:
    """Query inhabitant given the user-specified predicate."""
    global con
    required_tables = ""
    required_predicate = ""
    if income_lo is not None or income_hi is not None \
            or occupation is not None \
            or workplace_building_id is not None or workplace_building_name is not None:
        required_tables = "NATURAL JOIN workplace NATURAL JOIN occupation JOIN building AS w ON workplace_building_id = w.building_id"

        if income_lo is not None:
            required_predicate = required_predicate + " AND income >= " + str(income_lo)
        if income_hi is not None:
            required_predicate = required_predicate + " AND income <= " + str(income_hi)

        if occupation is not None:
            required_predicate = required_predicate + " AND occupation_name = '{0}'".format(occupation)

    if gender is not None:
        required_predicate = required_predicate + " AND gender = '{0}'".format(gender)

    if dead is False:
        required_predicate = required_predicate + " AND dead = 0"
    elif dead is True:
        required_predicate = required_predicate + " AND dead = 1"
    if custody is False:
        required_predicate = required_predicate + " AND custody = 0"
    elif custody is True:
        required_predicate = required_predicate + " AND custody = 0"

    if home_building_id is not None:
        required_predicate = required_predicate + " AND h.building_id = {0}".format(home_building_id)
    if home_building_name is not None:
        required_predicate = required_predicate + " AND h.building_name = '{0}'".format(home_building_name)
    if workplace_building_id is not None:
        required_predicate = required_predicate + " AND w.building_id = {0}".format(workplace_building_id)
    if workplace_building_name is not None:
        required_predicate = required_predicate + " AND w.building_name = '{0}'".format(workplace_building_name)

    if suspect is True:
        required_predicate = required_predicate + " AND EXISTS(SELECT * FROM suspect WHERE suspect.inhabitant_id = inhabitant.inhabitant_id)"
    elif suspect is False:
        required_predicate = required_predicate + " AND NOT EXISTS(SELECT * FROM suspect WHERE suspect.inhabitant_id = inhabitant.inhabitant_id)"

    query = """ SELECT inhabitant_id, first_name, last_name, h.building_name, workplace_id, custody, dead, gender
                  FROM inhabitant
                       JOIN building AS h
                       ON home_building_id = h.building_id """ + required_tables \
            + '\nWHERE TRUE ' + required_predicate
    # print(query)
    cur = con.execute(query)
    return ('inhabitant_id', 'first_name', 'last_name', 'home_building_name', 'workplace_id', 'custody', 'dead', 'gender'), \
        cur.fetchall()


def query_inhabitant_detail(inhabitant_id: int) -> Tuple[Tuple[str, ...], Tuple]:
    """Return the details for a given inhabitant."""
    cur = con.execute('''SELECT inhabitant_id, first_name, last_name,
                                custody, dead, gender,
                                h.building_name, h.lockdown,
                                w.building_name, w.lockdown,
                                occupation_name, income,
                                arrive_min, leave_min
                           FROM inhabitant
                                JOIN building AS h
                                ON home_building_id = h.building_id
                                JOIN workplace
                                USING(workplace_id)
                                JOIN building AS w
                                ON workplace_building_id = w.building_id
                                JOIN occupation
                                USING(occupation_id)
                          WHERE inhabitant_id = ?''',
                      (inhabitant_id,))

    return ('inhabitant_id', 'first_name', 'last_name',
            'custody', 'dead', 'gender',
            'home_building_name', 'home_lockdown',
            'workplace_building_name', 'workplace_lockdown',
            'occupation_name', 'income',
            'arrive_min', 'leave_min'), \
        cur.fetchone()


def query_via_point_constraint(start: int, end: int, mins: int) -> List[Tuple[int]]:
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


# TODO: Exclude counts after an inhabitant has been killed.
# TODO: Test this with inhabitant data.


def query_witness_count(vertex_id: int) -> List[Tuple[str, str, int]]:
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


def query_victim_commonality() -> List[Tuple]:
    """List the common attributes among victims."""
    cur = con.execute("SELECT * FROM commonality")
    return cur.fetchall()


def select_victim() -> Tuple:
    """Select a single victim."""
    with open(os.path.join(ROOT_DIR, "kill_sequence.sql")) as fd:
        script = fd.read()
    con.executescript(script)

    # The following query outputs one tuple containing information of the selected victim:
    # inhabitant_id, scene_vertex_id, min_of_death, weighted_sum (killer characteristics fulfilled)
    cur = con.execute('''
        SELECT pot_victim.inhabitant_id, pot_victim.vertex_id AS scene_vertex_id, (ABS(RANDOM())%(end_min-start_min) + start_min) AS min_of_death, weight_sum
        FROM (SELECT inhabitant_id, vertex_id, sum(chara_weight) AS weight_sum
            FROM weighed_pot_victim
            GROUP BY inhabitant_id, vertex_id) AS sub, pot_victim
        WHERE sub.inhabitant_id = pot_victim.inhabitant_id AND
                sub.vertex_id = pot_victim.vertex_id AND
                ABS(RANDOM())%(end_min-start_min) + start_min IS NOT NULL
        ORDER BY weight_sum DESC
        LIMIT 1;
    ''')
    return cur.fetchone()
