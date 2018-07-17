import sqlite3
import contextlib
from io import StringIO

path_to_file = 'data/database.db'

con = sqlite3.connect("data/database.db")
tempfile = StringIO()
for line in con.iterdump():
    tempfile.write('%s\n' % line)
con.close()
tempfile.seek(0)

conn = sqlite3.connect(":memory:")
conn.cursor().executescript(tempfile.read())
conn.commit()

def execute_statement(statement):
    with contextlib.closing(conn.cursor()) as cursor:
        if isinstance(statement, list):
            for s in statement:
                cursor.execute(s)
        elif isinstance(statement, tuple):
            cursor.execute(statement[0], statement[1])
        else:
            cursor.execute(statement)

def execute_many(query, values):
    with contextlib.closing(conn.cursor()) as cursor:
        cursor.executemany(query, values)

def fetchall(statement):
    with contextlib.closing(conn.cursor()) as cursor:
        if isinstance(statement, list):
            for s in statement:
                cursor.execute(s)
                return cursor.fetchall()
        else:
            cursor.execute(statement)
            return cursor.fetchall()

def fetchone(statement):
    with contextlib.closing(conn.cursor()) as cursor:
        if isinstance(statement, list):
            for s in statement:
                cursor.execute(s)
        elif isinstance(statement, tuple):
            cursor.execute(statement[0], statement[1])
        else:
            cursor.execute(statement)
        return cursor.fetchone()

def get_connection():
    return conn
