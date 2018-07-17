from db.db_interface import execute_statement, fetchall
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