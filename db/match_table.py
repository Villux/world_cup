import pandas as pd

from db.db_interface import execute_statement, fetchall, get_connection
from db.db_helper import get_value_tuple, build_insert_query

table_name = "match"

def insert(**kwargs):
    query = build_insert_query(kwargs, table_name)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")

def get_matches():
    statement = '''select date, home_team, away_team, id from match'''
    return fetchall(statement)


def get_mutual_matches_between_dates(home_team, away_team, start, end):
    query = f"select home_team, home_score, away_team, away_score \
        from match \
        where date > '{start}' AND date < '{end}' AND \
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

def delete_simulations():
    query = 'delete from match where simulation=1;'
    execute_statement(query)