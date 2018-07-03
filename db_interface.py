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

def create_tables():
    drop_match_table = '''DROP TABLE IF EXISTS match;'''
    drop_player_attributes_table = '''DROP TABLE IF EXISTS player_attributes;'''

    execute_statement([drop_match_table, drop_player_attributes_table])

def import_match_results(filename='data/original/results.csv'):
    match_results = pd.read_csv(filename)
    match_results['date'] =  pd.to_datetime(match_results['date'], format='%Y-%m-%d')
    match_results["year"] = match_results["date"].dt.year
    match_results["simulation"] = False
    match_results = match_results.drop(['neutral'], axis=1)
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        match_results.to_sql('match', con=conn, index=True, index_label='id',)

def import_player_attributes(filename='data/generated/team_level_player_data.csv'):
    player_stats = pd.read_csv(filename)
    player_stats = player_stats.drop(['Unnamed: 0'], axis=1)
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn:
        player_stats.to_sql('player_attributes', con=conn)

if __name__ == "__main__":
    create_tables()
    import_match_results()
    import_player_attributes()
