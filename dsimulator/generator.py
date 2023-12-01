"""Generate the game world procedurally."""

import numpy as np
import random
from typing import List, Tuple
from faker import Faker

np.random.seed(0)


NUM_INHABITANTS = 1000
GENDERS = ['m', 'f']
CUSTODY_VALUES = [0, 1]
DEAD_VALUES = [0, 1]

con = None

def generate_inhabitant(num_inhab = 1000) -> str:
    global con
    result = ""
    template = "INSERT INTO inhabitant VALUES ({0},{1},{2},{3},{4},{5},0,0,{6});\n"
    # workplace data should be inserted before this function is called
    workplace_list = con.execute("SELECT * FROM workplace")
    fk = Faker('en_US') # use english names as this shall be an American town
    for i in range(num_inhab-1):
        gender = random.uniform(0,1)
        sex = None
        first_name = None
        if gender < 0.5:
            # generate male inhabitant
            sex = "m"
            first_name = fk.first_name_male()
        else:
            # generate female inhabitant
            sex = "f"
            first_name = fk.first_name_female()
        last_name = fk.last_name()
        workplace = random.choice(workplace_list) # randomly select a workplace tuple
        work = workplace[0] # extract workplace_id
        occupation = workplace[2] # extract occupation_id
        # query for the equivalent home building, occupation, income_range and home should be inserted before this function is called
        h_build = con.execute('''
                          SELECT home_building_id
                          FROM occupation, income_range JOIN home USING (income_level)
                          WHERE income >= low AND income < high AND
                            occupation_id = {0}
                          '''.format(occupation)).fetchall()[0][0]
        # loc_building is initialized to equal home_building
        result.append(template.format(i, first_name, last_name, h_build, h_build, work, sex))
        
    # setting an inhabitant with attributes matching the character of the killer (the killer is designated to be the last inhabitant)
    # this is for the purpose of tests
    
    killer_info = con.execute('''
                            SELECT home_building_id, workplace_id
                            FROM workplace JOIN occupation USING (occupation_id), income_range JOIN home USING (income_level)
                            WHERE occupation_name = "student" AND
                                income >= low AND income < high
                            ''')
    h_build = killer_info[0][0]
    work = killer_info[0][1]
    result.append(template.format(num_inhab-1, "Light", "Yagami", h_build, h_build, work, "m"))

def generate_relationship():
        
def generate_killer_info():
    ''' generate only one killer for testing purposes'''
    global con
    result = "INSERT INTO killer VALUES(0);\n"
    template = "INSERT killer_chara VALUES(0, {0}, {1});\n"
    result = result + template.format("rapist", 10)
    result = result + template.format("high income", 5)
    result = result + template.format("")
        
        
            

def generate_workplaces(num_inhabitants: int) -> List[str]:
    """Randomly generate a list of workplaces for each inhabitant."""
    workplaces = ["Tech Company", "Hospital", "University", "Retail Store", "Factory", "Law Firm", "Restaurant", "Bank", "Hotel", "Museum"]
    return [random.choice(workplaces) for _ in range(num_inhabitants)]


def generate_custody_status(num_inhabitants: int) -> List[str]:
    """Randomly generate a list of custody status for each inhabitant."""
    statuses = ["Free", "Under Custody"]
    return [random.choice(statuses) for _ in range(num_inhabitants)]


def generate_genders(num_inhabitants: int) -> List[str]:
    """Randomly generate a list of genders for each inhabitant."""
    return [random.choice(['Male', 'Female']) for _ in range(num_inhabitants)]


def generate_map() -> str:
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

    return result
