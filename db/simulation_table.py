from db.db_interface import execute_statement, fetchall
from db.db_helper import get_value_tuple, build_insert_query

table_name = "match_simulation"

def insert(**kwargs):
    query = build_insert_query(kwargs, table_name)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")

def insert_match(match):
    match_dict = match.to_dict()
    match_dict["match_id"] = match.id
    match_dict.pop('tournament', None)
    return insert(**match_dict)

def delete_all():
    query = 'delete from match_simulation;'
    execute_statement(query)