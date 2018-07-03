from db_interface import execute_statement, fetchall

insert_query = '''insert into match
        (date, home_team, away_team, home_score, away_score, tournament, city, country, year, simulation)
        value (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

def insert(**kwargs):
    values = (kwargs["date"],
              kwargs["home_team"],
              kwargs["away_team"],
              kwargs["home_score"],
              kwargs["away_score"],
              kwargs["tournament"],
              kwargs["city"],
              kwargs["country"],
              kwargs["year"],
              kwargs["simulation"])
    execute_statement((insert_query, values))
    return execute_statement("select last_insert_rowid()")

def get_matches():
    statement = '''select date, home_team, away_team, id from match'''
    return fetchall(statement)