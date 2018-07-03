import datetime
import pandas as pd
import numpy as np
from dateutil.parser import parse

from db_interface import fetchall, execute_many, fetchone, execute_statement, get_connection

def get_median_goals(data, home, away):
    home_data = data[(data['home_team'] == home) | (data['away_team'] == home)]
    home_goal_mean = pd.concat([home_data[(home_data['home_team'] == home)]["home_score"],
                                 home_data[(home_data['away_team'] == home)]["away_score"]]).mean()

    away_data = data[(data['home_team'] == away) | (data['away_team'] == away)]
    away_goal_mean = pd.concat([away_data[(away_data['home_team'] == away)]["home_score"],
                                 away_data[(away_data['away_team'] == away)]["away_score"]]).mean()

    if np.isnan(home_goal_mean):
        home_goal_mean = 0
    if np.isnan(away_goal_mean):
        away_goal_mean = 0
    return float(home_goal_mean), float(away_goal_mean)

def get_previous_goals(data, home, away):
    home_team_goals = pd.concat([data[(data['home_team'] == home)]["home_score"],
                                 data[(data['away_team'] == home)]["away_score"]])
    away_team_goals = pd.concat([data[(data['home_team'] == away)]["home_score"],
                                 data[(data['away_team'] == away)]["away_score"]])

    home_goals = home_team_goals.sum()
    away_goals = away_team_goals.sum()
    goal_diff = home_goals - away_goals
    if np.isnan(goal_diff) or goal_diff == False:
        goal_diff = float(0)

    home_avg = home_team_goals.mean()
    away_avg = away_team_goals.mean()

    if np.isnan(home_avg):
        home_avg = 0
    if np.isnan(away_avg):
        away_avg = 0

    return float(goal_diff), float(home_avg), float(away_avg)

def calculate_goal_features_for_match(date, home_team, away_team, match_id):
    query = f"select home_team, home_score, away_team, away_score \
        from match \
        where date < '{date}' AND \
        ((home_team='{home_team}' AND away_team='{away_team}') OR (home_team='{away_team}' AND away_team='{home_team}'));"
    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    goal_diff_with_away, home_goals_with_away, away_goals_with_home = get_previous_goals(df, home_team, away_team)

    max_date = parse(date)
    min_date = max_date - datetime.timedelta(days=4)

    query = f"select home_team, home_score, away_team, away_score \
        from match \
        where date BETWEEN '{min_date}' AND '{max_date}' AND \
        home_team='{home_team}' OR away_team='{away_team}' OR home_team='{away_team}' OR away_team='{home_team}';"

    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    home_goal_mean, away_goal_mean = get_median_goals(df, home_team, away_team)

    insert_query = "insert into goal_feature (goal_diff_with_away, home_goals_with_away, away_goals_with_home, match_id, home_goal_mean, away_goal_mean) values (?, ?, ?, ?, ?, ?)"
    execute_statement((insert_query, (goal_diff_with_away, home_goals_with_away, away_goals_with_home, match_id, home_goal_mean, away_goal_mean)))

def init_goal_features_table():
    drop = '''DROP TABLE IF EXISTS goal_feature;'''
    create = '''CREATE TABLE goal_feature
                    (id integer PRIMARY KEY AUTOINCREMENT,
                    goal_diff_with_away real,
                    home_goals_with_away real,
                    away_goals_with_home real,
                    home_goal_mean real,
                    away_goal_mean real,
                    match_id integer,
                    FOREIGN KEY(match_id) REFERENCES match(id));'''

    execute_statement([drop, create])

def calculate_features_for_matches():
    statement = '''select date, home_team, away_team, id from match'''
    for match in fetchall(statement):
        match_id = match[3]
        date = match[0]
        home_team, away_team = match[1], match[2]
        calculate_goal_features_for_match(date, home_team, away_team, match_id)

if __name__ == "__main__":
    init_goal_features_table()
    calculate_features_for_matches()
