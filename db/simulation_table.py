import pandas as pd
from db.db_interface import execute_statement, fetchall, fetchone, get_connection
from db.db_helper import get_value_tuple, build_insert_query

table_name = "match_simulation"

def insert(**kwargs):
    query = build_insert_query(kwargs, table_name)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")

def delete_all():
    query = 'delete from match_simulation;'
    execute_statement(query)

def get_outcome_count_query(team, match_id, home_team=True):
    team_field = "home_team"
    if not home_team:
        team_field = "away_team"

    return f"select count(outcome), outcome from match_simulation where match_id={match_id} AND {team_field}='{team}' group by outcome"

def get_number_of_simulations_for_match(match_id):
    query = f"select count(*) from match_simulation where match_id={match_id}"
    return fetchone(query)[0]

def get_win_probability(team, match_id):
    query = get_outcome_count_query(team, match_id, home_team=True)
    home_team_outcomes = dict((outcome, count) for count, outcome in fetchall(query))

    query = get_outcome_count_query(team, match_id, home_team=False)
    away_team_outcomes = dict((outcome, count) for count, outcome in fetchall(query))

    total_number_of_matches = get_number_of_simulations_for_match(match_id)

    return (home_team_outcomes.get(1, 0) + away_team_outcomes.get(-1, 0))/total_number_of_matches


def store_simulation_results(filename):
    simulations = pd.read_sql_query("""select * from match_simulation;""", get_connection())
    simulations.to_csv(filename)
