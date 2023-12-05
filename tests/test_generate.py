"""Generate some test objects."""

import sqlite3


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
