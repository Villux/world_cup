from db.db_interface import execute_statement
from db.db_helper import get_value_tuple, build_insert_query

table_name = "goal_feature"

def insert(**kwargs):
    query = build_insert_query(kwargs, table_name)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")
