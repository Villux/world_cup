import pandas as pd
from db_interface import get_connection, execute_statement

def get_mutual_matches_between_dates(home_team, away_team, start, end):
    query = f"select home_team, home_score, away_team, away_score \
        from match \
        where date BETWEEN '{start}' AND '{end}' AND \
        (home_team='{home_team}' OR away_team='{away_team}' OR home_team='{away_team}' OR away_team='{home_team}');"

    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_mutual_matches(home_team, away_team, date):
    query = f"select home_team, home_score, away_team, away_score \
        from match \
        where date < '{date}' AND \
        ((home_team='{home_team}' AND away_team='{away_team}') OR (home_team='{away_team}' AND away_team='{home_team}'));"
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_value_tuple(row):
    return tuple(row.values())

def build_insert_query(data):
    columns = data.keys()
    placeholders = ["?"] * len(columns)
    query = f"insert into goal_feature ({','.join(columns)}) values ({','.join(placeholders)})"
    return query

def insert(**kwargs):
    query = build_insert_query(kwargs)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")
