from db_interface import fetchall, execute_many, fetchone, execute_statement

def expected(A, B):
    return 1 / (1 + 10 ** ((B - A) / 400))

def elo(old, exp, score, K):
    return old + K * (score - exp)

def get_new_elo(A, B, goals_A, goals_B, K):
    goals_diff = abs(goals_A - goals_B)
    if goals_diff == 2:
        K *= 1.5
    elif goals_diff == 3:
        K *= 1.75
    elif goals_diff > 3:
        K *= (1.75 + (goals_diff - 3) / 8)

    if goals_A > goals_B:
        score = 1
    elif goals_A == goals_B:
        score = 0.5
    else:
        score = 0
    return elo(A, expected(A, B), score, K)

def elo_rating_change_for_match(elo_A, elo_B, tournament, goals_A, goals_B):
    K = 30
    if tournament in ["FIFA World Cup"]:
        K = 60
    elif tournament in ["Confederations Cup", "Copa America", "UEFA Euro", "FIFA World Cup qualification"]:
        K = 50
    elif tournament in ["AFC Asian Cup", "Gold Cup", "CONCACAF Championship",
                        "Oceania Nations Cup", "African Cup of Nations"]:
        K = 50 * 0.85
    elif tournament in ["African Cup of Nations qualification", "AFC Asian Cup qualification",
                        "UEFA Euro qualification", "CONCACAF Championship qualification",
                        "Oceania Nations Cup qualification", "AFC Challenge Cup",
                        "AFC Challenge Cup qualification", "Gold Cup qualification"]:
        K = 40

    new_elo_A = get_new_elo(elo_A, elo_B, goals_A, goals_B, K)
    new_elo_B = get_new_elo(elo_B, elo_A, goals_B, goals_A, K)

    return new_elo_A, new_elo_B

def init_elo_for_every_team(init_date='1800-01-01', init_value=1500):
    statement = '''select home_team as teams from match
                   union
                   select away_team from match'''
    teams = [team[0] for team in fetchall(statement)]
    tuples = [(init_date, team, init_value, False) for team in teams]
    execute_many("insert into elo_rating (date, team, elo, simulation) values (?, ?, ?, ?)", tuples)

def calculate_elo_from_matches():
    statement = '''select date, home_team, away_team, home_score, away_score, tournament, id from match'''
    for match in fetchall(statement):
        match_id = match[6]
        date = match[0]
        home_team, away_team = match[1], match[2]
        home_score, away_score = match[3], match[4]
        tournament = match[5]

        query = 'SELECT id, elo FROM elo_rating WHERE team=? AND date<=? AND match_id IS NULL ORDER BY date DESC;'
        id_a, elo_A = fetchone((query, (home_team, date)))
        id_b, elo_B = fetchone((query, (away_team, date)))

        elo_home, elo_away = elo_rating_change_for_match(elo_A, elo_B, tournament, home_score, away_score)

        execute_many("update elo_rating set match_id=? where id=?",
            [(match_id, id_a),
            (match_id, id_b)])

        execute_many("insert into elo_rating (date, team, elo, simulation) values (?, ?, ?, ?)",
            [(date, home_team, elo_home, False),
            (date, away_team, elo_away, False)])

def init_elo_table():
    drop_elo_table = '''DROP TABLE IF EXISTS elo_rating;'''
    create_elo_table = '''CREATE TABLE elo_rating
                    (id integer PRIMARY KEY AUTOINCREMENT,
                    date text, team text, elo real, simulation integer,
                    match_id integer,
                    FOREIGN KEY(match_id) REFERENCES match(id));'''

    execute_statement([drop_elo_table, create_elo_table])

if __name__ == "__main__":
    init_elo_table()
    init_elo_for_every_team()
    calculate_elo_from_matches()