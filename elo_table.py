from db_interface import execute_statement, execute_many, fetchone

def get_value_tuple(row):
    return tuple(row.values())

def build_insert_query(elo_data):
    columns = elo_data.keys()
    placeholders = ["?"] * len(columns)
    query = f"insert into elo_rating ({','.join(columns)}) values ({','.join(placeholders)})"
    return query

def insert(**kwargs):
    query = build_insert_query(kwargs)
    values = get_value_tuple(kwargs)
    execute_statement((query, values))
    return execute_statement("select last_insert_rowid()")

def insert_many(elo_rows):
    query = build_insert_query(elo_rows[0])

    values = []
    for row in elo_rows:
        values.append(get_value_tuple(row))
    execute_many(query, values)

def select_latest_for_team(team):
    query = 'SELECT elo FROM elo_rating WHERE team=? AND match_id IS NULL ORDER BY date DESC;'
    return fetchone((query, (team,)))[0]

def attach_match_to_current_rating(match_id, team):
    if isinstance(team, list):
        values = [(match_id, t) for t in team]
    else:
        values = [(match_id, team)]
    execute_many("update elo_rating set match_id=? where match_id IS NULL and team=?", values)
