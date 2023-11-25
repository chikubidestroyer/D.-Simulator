import pandas as pd
import numpy as np
import random

#import mysql



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

def generate_map():
    result = ''
    for y in range(10):
        for x in range(10):
            result = result + 'INSERT INTO vertex VALUES({0}, {1}, {2});\n'.format(y*10+x, x, y)
    
    template = 'INSERT INTO edge VALUES({0}, {1}, {2});\n'
    for y in range(10):
        for x in range(10):
            y_temp = random.randint(10,20)
            x_temp = random.randint(10,20)
            if y != 9:
                result = result + template.format(y*10+x, (y+1)*10+x, y_temp)
                result = result + template.format((y+1)*10+x, y*10+x, y_temp)
            if x != 9:
                result = result + template.format(y*10+x, y*10+x+1, x_temp)
                result = result + template.format(y*10+x+1, y*10+x, x_temp)
                
    for y in range(9):
        x = random.randint(1,3)
        while x < 10:
            up_or_down = random.randint(0,1)
            if x == 0:
                if up_or_down == 0:
                    result = result + template.format(y*10+x, (y+1)*10+x+1, random.randint(10,20))
                else:
                    result = result + template.format((y+1)*10+x+1, y*10+x, random.randint(10,20))
            elif x == 9:
                if up_or_down == 0:
                    result = result + template.format(y*10+x, (y+1)*10+x-1, random.randint(10,20))
                else:
                    result = result + template.format((y+1)*10+x-1, y*10+x, random.randint(10,20))
            else:
                if up_or_down == 0:
                    result = result + template.format(y*10+x, (y+1)*10+x+random.choice([-1,1]), random.randint(10,20))
                else:
                    result = result + template.format((y+1)*10+x+random.choice([-1,1]), y*10+x, random.randint(10,20))
            x = x + random.randint(1,3)
            
    return result

