import os
import sqlite3
from dsimulator.defs import ROOT_DIR

def init_game():
    global con
    con = sqlite3.connect(":memory:")

    with open(os.path.join(ROOT_DIR, 'DDL.sql')) as fd:
        sqlFile = fd.read()
    sqlCmds = sqlFile.split(';')
    with con:
        for c in sqlCmds:
            con.execute(c)

    for row in con.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        print(row)
