"""Generate the game world procedurally."""

import sqlite3
import numpy as np
import random
from faker import Faker

np.random.seed(0)


NUM_INHABITANTS = 1000
GENDERS = ['m', 'f']
CUSTODY_VALUES = [0, 1]
DEAD_VALUES = [0, 1]
fk = Faker('en_US')  # use english names as this shall be an American town


def get_free_vertex(con: sqlite3.Connection) -> int:
    """Return a random vertex without a building."""
    cur = con.execute('''SELECT vertex_id
                           FROM vertex
                          WHERE NOT EXISTS (SELECT * FROM building WHERE building_id = vertex_id)
                       ORDER BY RANDOM()
                          LIMIT 1''')
    return cur.fetchone()[0]


def generate_home(con: sqlite3.Connection, building_per_range: int = 2) -> None:
    """Generate the homes and income ranges given the database connection containing vertices."""
    income_name = ['Low Income Home', 'Medium Income Home', 'High Income Home']
    income = [(1, 30000), (30000, 90000), (90000, None)]  # [1,3000), [3000,90000), [90000,inf) this was the bug from previous meeting
    with con:
        for n, r in zip(income_name, income):
            cur = con.execute('INSERT INTO income_range (low, high) VALUES (?, ?)', r)
            income_level = cur.lastrowid

            for i in range(building_per_range):
                home_building_id = get_free_vertex(con)
                con.execute('INSERT INTO building (building_id, building_name, lockdown) VALUES (?, ?, ?)',
                            (home_building_id, n + ' ' + str(i + 1), 0))
                con.execute('INSERT INTO home (home_building_id, income_level) VALUES (?, ?)',
                            (home_building_id, income_level))


def generate_workplace(con: sqlite3.Connection, num_occupation: int = 30, num_building: int = 30, occupation_per_building: int = 3) -> None:
    """Generate the workplaces (occupations and buildings) given the database connection containing vertices."""
    with con:
        # Generate the occupations.
        for _ in range(num_occupation):
            occupation_name = fk.job()
            income = random.randint(1, 100) * 1000
            arrive_min = random.randint(8, 10) * 60
            leave_min = random.randint(16, 18) * 60
            con.execute('INSERT INTO occupation (occupation_name, income, arrive_min, leave_min) VALUES (?, ?, ?, ?)',
                        (occupation_name, income, arrive_min, leave_min))

        # Generate the working buildings.
        for _ in range(num_building):
            building_id = get_free_vertex(con)

            # Use a company name as the name of the building.
            building_name = fk.company()
            while True:
                cur = con.execute('SELECT COUNT(*) FROM building WHERE building_name = ?', (building_name,))
                if cur.fetchone()[0] == 0:
                    break
                building_name = fk.company()

            con.execute('INSERT INTO building (building_id, building_name, lockdown) VALUES (?, ?, ?)',
                        (building_id, building_name, 0))

            # Connect buildings with occupations.
            con.execute('''INSERT INTO workplace (workplace_building_id, occupation_id)
                               SELECT ?, occupation_id
                                 FROM occupation
                             ORDER BY RANDOM()
                                LIMIT ?''',
                        (building_id, occupation_per_building))


def generate_inhabitants_and_relationships(con: sqlite3.Connection, num_inhab: int = 1000) -> None:
    """Generate inhabitants and relationships."""
    template_inhabitant = "INSERT INTO inhabitant VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?);"
    template_relationship = "INSERT INTO relationship VALUES (?, ?, ?);"
    # Get workplace data
    workplace_list = con.execute("SELECT * FROM workplace").fetchall()

    # Generate inhabitants
    inhabitants = []
    for i in range(num_inhab - 1):
        gender = 'm' if random.uniform(0, 1) < 0.5 else 'f'
        first_name = fk.first_name_male() if gender == 'm' else fk.first_name_female()
        last_name = fk.last_name()

        # Randomly select a workplace tuple
        workplace = random.choice(workplace_list)
        work = workplace[0]  # workplace_id
        occupation = workplace[2]  # occupation_id

        # Query for the equivalent home building, occupation, and income_range
        h_build = con.execute('''
            SELECT home_building_id
            FROM occupation, income_range JOIN home USING (income_level)
            WHERE income >= low AND (income < high OR high IS NULL) AND
                occupation_id = ?
            ORDER BY random()
        ''', (occupation,)).fetchone()[0]

        # Insert inhabitant into the database
        with con:
            con.execute(template_inhabitant, (i, first_name, last_name, h_build, h_build, work, gender))

        # Save inhabitant details for later relationship generation
        inhabitants.append({
            'id': i,
            'gender': gender,
            'first_name': first_name,
            'last_name': last_name,
            'home_building': h_build,
            'workplace_id': work
        })

    # Set an inhabitant with attributes matching the character of the killer
    killer_info = con.execute('''
        SELECT home_building_id, workplace_id
        FROM workplace JOIN occupation USING(occupation_id), income_range JOIN home USING(income_level)
        WHERE income >= low AND (income < high OR high IS NULL)
    ''').fetchone()

    # Insert killer inhabitant
    with con:
        # killer_info['home_building_id'], killer_info['home_building_id'], killer_info['workplace_id']
        con.execute(template_inhabitant, (num_inhab - 1, "Light", "Yagami", killer_info[0],
                                          killer_info[0], killer_info[1], 'm'))

    # Generate relationships between inhabitants
    for inhabitant in inhabitants:
        # Consistent relationships based on common sense
        different_inhabitants = [other for other in inhabitants if other['id'] != inhabitant['id']]
        # Get random relationship type
        # relationship_type = random.choice(["Relative", "Friend", "Enemy", "Colleague"])

        # Get a related inhabitant based on gender and last name
        related = [
            other for other in different_inhabitants if
            other['last_name'] == inhabitant['last_name']
        ]
        with con:
            for relative in related:
                con.execute(template_relationship, (inhabitant['id'], relative['id'], "Relative"))
                different_inhabitants.remove(relative)

        enemy = random.choice(different_inhabitants)
        different_inhabitants.remove(enemy)
        with con:
            con.execute(template_relationship, (inhabitant['id'], enemy['id'], "Enemy"))

        friend = random.choice(different_inhabitants)
        different_inhabitants.remove(friend)
        with con:
            con.execute(template_relationship, (inhabitant['id'], friend['id'], "Friend"))

        colleagues = [
            other for other in different_inhabitants if
            other['workplace_id'] == inhabitant['workplace_id']
        ]

        for colleague in colleagues:
            with con:
                con.execute(template_relationship, (inhabitant['id'], colleague['id'], "Colleague"))


def generate_map(con: sqlite3.Connection) -> None:
    """Return a query that inserts a random-generated map into the database."""
    result = ''
    for y in range(10):
        for x in range(10):
            result = result + 'INSERT INTO vertex VALUES({0}, {1}, {2});\n'.format(y * 10 + x, x, y)

    template = 'INSERT INTO edge VALUES({0}, {1}, {2});\n'
    for y in range(10):
        for x in range(10):
            y_temp = random.randint(10, 20)
            x_temp = random.randint(10, 20)
            if y != 9:
                result = result + template.format(y * 10 + x, (y + 1) * 10 + x, y_temp)
                result = result + template.format((y + 1) * 10 + x, y * 10 + x, y_temp)
            if x != 9:
                result = result + template.format(y * 10 + x, y * 10 + x + 1, x_temp)
                result = result + template.format(y * 10 + x + 1, y * 10 + x, x_temp)

    for y in range(9):
        x = random.randint(1, 3)
        while x < 10:
            up_or_down = random.randint(0, 1)
            if x == 0:
                if up_or_down == 0:
                    result = result + template.format(y * 10 + x, (y + 1) * 10 + x + 1, random.randint(10, 20))
                else:
                    result = result + template.format((y + 1) * 10 + x + 1, y * 10 + x, random.randint(10, 20))
            elif x == 9:
                if up_or_down == 0:
                    result = result + template.format(y * 10 + x, (y + 1) * 10 + x - 1, random.randint(10, 20))
                else:
                    result = result + template.format((y + 1) * 10 + x - 1, y * 10 + x, random.randint(10, 20))
            else:
                if up_or_down == 0:
                    result = result + template.format(y * 10 + x, (y + 1) * 10 + x + random.choice([-1, 1]), random.randint(10, 20))
                else:
                    result = result + template.format((y + 1) * 10 + x + random.choice([-1, 1]), y * 10 + x, random.randint(10, 20))
            x = x + random.randint(1, 3)

    for insert_statement in result.split(';'):
        con.execute(insert_statement)


def generate_test_killer(con: sqlite3.Connection) -> None:
    """Generate only one killer for testing purposes."""
    con.execute("INSERT INTO killer VALUES(0)")
    template = "INSERT INTO killer_chara VALUES(0, ?, ?)"
    con.execute(template, ("rapist", 15))
    con.execute(template, ("high income", 5))
    con.execute(template, ("colleague", 10))


def init_status(con: sqlite3.Connection) -> None:
    """Initialize status to constant for tests."""
    # resignation day is set to 15 for now
    con.execute("INSERT INTO status VALUES(0, 1, 15, 0, 999)")
