from db.db_interface import execute_statement, execute_many, fetchone
from db.db_helper import get_value_tuple, build_insert_query

table_name = "elo_rating"

def insert(**kwargs):
    query = build_insert_query(kwargs, table_name)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")

def insert_many(elo_rows):
    query = build_insert_query(elo_rows[0], table_name)
    values = []
    for row in elo_rows:
        values.append(get_value_tuple(row))
    execute_many(query, values)

def select_latest_for_team(team, date):
    query = 'SELECT elo FROM elo_rating WHERE team=? AND date < ? ORDER BY date DESC;'
    return fetchone((query, (team,date)))[0]

def attach_match_to_current_rating(match_id, team):
    if isinstance(team, list):
        values = [(match_id, t) for t in team]
    else:
        values = [(match_id, team)]
    execute_many("update elo_rating set match_id=? where match_id IS NULL and team=?", values)

def delete_elos_after_date(date):
    query = 'delete from elo_rating where date > ?;'
    execute_statement((query, (date,)))
