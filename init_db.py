import time
import pandas as pd

from db_interface import execute_many, get_connection, execute_statement, fetchall
from elo import calculate_elo_from_matches
from generate_goal_features import calculate_features_for_matches

tables = ["match", "elo_rating", "player_attribute", "goal_feature"]

def delete_tables():
    for table in tables:
        query = f"DROP TABLE IF EXISTS {table};"
        execute_statement(query)

def init_elo_table():
    def init_elo_for_every_team(init_date='1800-01-01', init_value=1500):
        statement = '''select home_team as teams from match
                    union
                    select away_team from match'''
        teams = [team[0] for team in fetchall(statement)]
        tuples = [(init_date, team, init_value) for team in teams]
        execute_many("insert into elo_rating (date, team, elo) values (?, ?, ?)", tuples)

    create_elo_table = '''CREATE TABLE elo_rating
                    (id integer PRIMARY KEY AUTOINCREMENT,
                    date text, team text, elo real,
                    match_id integer,
                    FOREIGN KEY(match_id) REFERENCES match(id));'''

    execute_statement(create_elo_table)
    init_elo_for_every_team()

def import_match_results(filename='data/original/results.csv'):
    match_results = pd.read_csv(filename)
    match_results['date'] =  pd.to_datetime(match_results['date'], format='%Y-%m-%d')
    match_results["year"] = match_results["date"].dt.year
    match_results["simulation"] = False
    match_results = match_results.drop(['neutral'], axis=1)
    with get_connection() as conn:
        match_results.to_sql('match', con=conn, index=True, index_label='id')

def import_player_attributes(filename='data/generated/team_level_player_data.csv'):
    player_stats = pd.read_csv(filename)
    player_stats = player_stats.drop(['Unnamed: 0'], axis=1)
    with get_connection() as conn:
        player_stats.to_sql('player_attribute', con=conn, index=True, index_label='id')

def init_goal_features_table():
    create = '''CREATE TABLE goal_feature
                    (id integer PRIMARY KEY AUTOINCREMENT,
                    goal_diff_with_away real,
                    home_goals_with_away real,
                    away_goals_with_home real,
                    home_goal_mean real,
                    away_goal_mean real,
                    match_id integer,
                    FOREIGN KEY(match_id) REFERENCES match(id));'''

    execute_statement(create)

if __name__ == "__main__":
    start = time.time()

    delete_tables()
    import_match_results()
    import_player_attributes()
    init_elo_table()
    calculate_elo_from_matches()
    init_goal_features_table()
    calculate_features_for_matches()

    print("RUN TIME")
    end = time.time()
    print(end - start)
