import sqlite3
import contextlib
import pandas as pd

path_to_file = 'data/database.db'

def execute_statement(statement):
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        with conn:
            with contextlib.closing(conn.cursor()) as cursor:
                if isinstance(statement, list):
                    for s in statement:
                        cursor.execute(s)
                elif isinstance(statement, tuple):
                    cursor.execute(statement[0], statement[1])
                else:
                    cursor.execute(statement)

def execute_many(query, values):
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        with conn:
            with contextlib.closing(conn.cursor()) as cursor:
                cursor.executemany(query, values)

def fetchall(statement):
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        with conn:
            with contextlib.closing(conn.cursor()) as cursor:
                if isinstance(statement, list):
                    for s in statement:
                        cursor.execute(s)
                        return cursor.fetchall()
                else:
                    cursor.execute(statement)
                    return cursor.fetchall()

def fetchone(statement):
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        with conn:
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
    return contextlib.closing(sqlite3.connect(path_to_file))