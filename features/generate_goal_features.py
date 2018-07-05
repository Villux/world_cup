import datetime
import pandas as pd
import numpy as np
from dateutil.parser import parse

from db.goal_feature_table import insert
from db.match_table import get_matches, get_mutual_matches, get_mutual_matches_between_dates

def get_goal_data_from_input_data(data):
    columns = ["goal_diff_with_away", "home_goals_with_away", "away_goals_with_home", "home_goal_mean", "away_goal_mean"]

    goal_data = {}
    for key, value in data.items():
        if key in columns:
            goal_data[key] = value
    return goal_data

def get_median_goals(data, home, away):
    home_data = data[(data['home_team'] == home) | (data['away_team'] == home)]
    home_goal_mean = pd.concat([home_data[(home_data['home_team'] == home)]["home_score"],
                                 home_data[(home_data['away_team'] == home)]["away_score"]]).mean()

    away_data = data[(data['home_team'] == away) | (data['away_team'] == away)]
    away_goal_mean = pd.concat([away_data[(away_data['home_team'] == away)]["home_score"],
                                 away_data[(away_data['away_team'] == away)]["away_score"]]).mean()

    if np.isnan(home_goal_mean):
        home_goal_mean = 0
    if np.isnan(away_goal_mean):
        away_goal_mean = 0
    return float(home_goal_mean), float(away_goal_mean)

def get_previous_goals(data, home, away):
    home_team_goals = pd.concat([data[(data['home_team'] == home)]["home_score"],
                                 data[(data['away_team'] == home)]["away_score"]])
    away_team_goals = pd.concat([data[(data['home_team'] == away)]["home_score"],
                                 data[(data['away_team'] == away)]["away_score"]])

    home_goals = home_team_goals.sum()
    away_goals = away_team_goals.sum()
    goal_diff = home_goals - away_goals
    if np.isnan(goal_diff) or goal_diff == False:
        goal_diff = float(0)

    home_avg = home_team_goals.mean()
    away_avg = away_team_goals.mean()

    if np.isnan(home_avg):
        home_avg = 0
    if np.isnan(away_avg):
        away_avg = 0

    return float(goal_diff), float(home_avg), float(away_avg)

def get_mutual_matches_for_window(home_team, away_team, end, lag_years=4):
    start = end - datetime.timedelta(days=365 * lag_years)
    return get_mutual_matches_between_dates(home_team, away_team, start, end)

def calculate_goal_features_for_match(date, home_team, away_team):
    df = get_mutual_matches(home_team, away_team, date)
    goal_diff_with_away, home_goals_with_away, away_goals_with_home = get_previous_goals(df, home_team, away_team)

    df = get_mutual_matches_for_window(home_team, away_team, parse(date))
    home_goal_mean, away_goal_mean = get_median_goals(df, home_team, away_team)

    goal_data = {
        "goal_diff_with_away": goal_diff_with_away,
        "home_goals_with_away": home_goals_with_away,
        "away_goals_with_home": away_goals_with_home,
        "home_goal_mean": home_goal_mean,
        "away_goal_mean": away_goal_mean
    }
    return goal_data

def insert_with_match_id(match_id, data):
    data["match_id"] = match_id
    insert(**data)


def calculate_features_for_matches():
    for match in get_matches():
        match_id = match[3]
        date = match[0]
        home_team, away_team = match[1], match[2]
        goal_data = calculate_goal_features_for_match(date, home_team, away_team)
        insert_with_match_id(match_id, goal_data)
