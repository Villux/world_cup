import datetime

from db.elo_table import select_latest_for_team, attach_match_to_current_rating, insert_many
from db.db_interface import fetchall, execute_many, fetchone, execute_statement

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

def get_current_elo(team):
    return select_latest_for_team(team)

def attach_elo_to_match(match_id, home_team, away_team):
    elo_A = get_current_elo(home_team)
    elo_B = get_current_elo(away_team)

    attach_match_to_current_rating(match_id, [home_team, away_team])
    return elo_A, elo_B

def update_elo_after_match(date, elo_home, elo_away, home_team, away_team, home_score, away_score, tournament):
    new_elo_home, new_elo_away = elo_rating_change_for_match(elo_home, elo_away, tournament, home_score, away_score)

    home_data = {"date": date, "team": home_team, "elo": new_elo_home}
    away_data = {"date": date, "team": away_team, "elo": new_elo_away}

    insert_many([home_data, away_data])

def calculate_elo_from_matches():
    statement = '''select date, home_team, away_team, home_score, away_score, tournament, id from match'''
    for match in fetchall(statement):
        match_id = match[6]
        date = match[0]
        home_team, away_team = match[1], match[2]
        home_score, away_score = match[3], match[4]
        tournament = match[5]

        elo_A, elo_B = attach_elo_to_match(match_id, home_team, away_team)
        update_elo_after_match(date, elo_A, elo_B, home_team, away_team, home_score, away_score, tournament)
