import pandas as pd
import numpy as np
import random

import mysql



np.random.seed(0)  


NUM_INHABITANTS = 1000
GENDERS = ['m', 'f']
CUSTODY_VALUES = [0, 1]
DEAD_VALUES = [0, 1]


def generate_random_names(num_names):
    first_names = ["Ivan", "Anastasia", "Mikhail", "Ekaterina", "Dmitry", "Olga", "Alexei", "Svetlana", "Sergei", "Irina","Amir", "Fatima", "Omar", "Layla", "Ali", "Zahra", "Yasir", "Noor", "Samir", "Huda","Aarav", "Priya", "Vihaan", "Diya", "Arjun", "Anika", "Ishaan", "Meera", "Dhruv", "Rani","Haruto", "Yuki", "Mei", "Hiroshi", "Sakura", "Daiki", "Hana", "Takumi", "Aiko ","Kenji ","John", "Jane", "Chris", "Anna", "Tom", "Emily", "Mike", "Sarah", "Robert", "Laura"]
    last_names = ["Smirnov", "Ivanov", "Kuznetsov", "Sokolov", "Popov", "Lebedev", "Kozlov", "Novikov", "Morozov", "Petrov","Al-Sayed", "Hassan", "Abdullah", "Al-Amir", "Farid", "Mahmoud", "Fakhoury", "Najjar", "Saleh", "Barakat","Patel", "Singh", "Kumar", "Sharma", "Gupta", "Mehta", "Joshi", "Shah", "Iyer", "Reddy","Kim", "Lee", "Nguyen", "Chen", "Wang", "Li", "Yoshida", "Tanaka", "Zhang", "Huang","Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
    return [random.choice(first_names) + " " + random.choice(last_names) for _ in range(num_names)]

##def generate_workplaces(num_inhabitants, num_workplaces):
    return [random.randint(1, num_workplaces) for _ in range(num_inhabitants)]

##def generate_custody_status(num_inhabitants):
    return [random.choice([0, 1]) for _ in range(num_inhabitants)]

##def generate_genders(num_inhabitants):
    return [random.choice(['m', 'f']) for _ in range(num_inhabitants)]

def generate_workplaces(num_inhabitants):
    workplaces = ["Tech Company", "Hospital", "University", "Retail Store", "Factory", "Law Firm", "Restaurant", "Bank", "Hotel", "Museum"]
    return [random.choice(workplaces) for _ in range(num_inhabitants)]

def generate_custody_status(num_inhabitants):
    statuses = ["Free", "Under Custody"]
    return [random.choice(statuses) for _ in range(num_inhabitants)]

def generate_genders(num_inhabitants):
    return [random.choice(['Male', 'Female']) for _ in range(num_inhabitants)]


inhabitant_data = {
    "inhabitant_id": np.arange(1, NUM_INHABITANTS + 1),
    "name": generate_random_names(NUM_INHABITANTS),
    "home_building_id": np.random.randint(1, 201, size=NUM_INHABITANTS),
    "loc_building_id": np.random.randint(1, 201, size=NUM_INHABITANTS),
    "workplace_type": generate_workplaces(NUM_INHABITANTS),  
    "custody_status": 0, 
    "dead": 0,
    "gender": generate_genders(NUM_INHABITANTS)
}


df_inhabitants = pd.DataFrame(inhabitant_data)
conn = mysql.connect('C:\Users\徐善若\Desktop\cs310')
df_inhabitants.to_sql('inhabitant', conn, if_exists='replace', index=False)
conn.close()
df_inhabitants.head()