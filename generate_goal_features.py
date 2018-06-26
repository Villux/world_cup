import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count

def get_median_goals(row):
    home = row["home_team"]
    away = row["away_team"]
    max_date = row["date"]
    min_date = row["date"] - pd.Timedelta(days=365 * 4)

    home_data = dataset[
        ((dataset['home_team'] == home) | (dataset['away_team'] == home)) &
        (dataset['date'] < max_date) &
        (dataset['date'] > min_date)]

    home_goal_mean = pd.concat([home_data[(home_data['home_team'] == home)]["home_score"],
                                 home_data[(home_data['away_team'] == home)]["away_score"]]).mean()

    away_data = dataset[
        ((dataset['home_team'] == away) | (dataset['away_team'] == away)) &
        (dataset['date'] < max_date) &
        (dataset['date'] > min_date)]
    away_goal_mean = pd.concat([away_data[(away_data['home_team'] == away)]["home_score"],
                                 away_data[(away_data['away_team'] == away)]["away_score"]]).mean()

    if np.isnan(home_goal_mean):
        home_goal_mean = 0
    if np.isnan(away_goal_mean):
        away_goal_mean = 0
    return home_goal_mean, away_goal_mean

def get_previous_goals(row):
    home = row["home_team"]
    away = row["away_team"]
    date = row["date"]
    data = dataset[
        ((dataset['home_team'] == home) | (dataset['away_team'] == home)) &
        ((dataset['home_team'] == away) | (dataset['away_team'] == away)) &
        (dataset['date'] < date)]

    home_team_goals = pd.concat([data[(data['home_team'] == home)]["home_score"],
                                 data[(data['away_team'] == home)]["away_score"]])
    away_team_goals = pd.concat([data[(data['home_team'] == away)]["home_score"],
                                 data[(data['away_team'] == away)]["away_score"]])

    home_goals = home_team_goals.sum()
    away_goals = away_team_goals.sum()

    home_avg = home_team_goals.mean()
    away_avg = away_team_goals.mean()
    if np.isnan(home_avg):
        home_avg = 0
    if np.isnan(away_avg):
        away_avg = 0

    home_goal_mean, away_goal_mean = get_median_goals(row)
    return pd.Series({
        'goal_diff_with_away': home_goals - away_goals,
        'home_goals_with_away': home_avg,
        'away_goals_with_home': away_avg,
        'home_goal_mean': home_goal_mean,
        'away_goal_mean': away_goal_mean,
        'home_team': home,
        'away_team': away,
        'date': date
    })

dataset = pd.read_csv('data/original/results.csv')
dataset['date'] =  pd.to_datetime(dataset['date'], format='%Y-%m-%d')
goal_data = dataset.apply(get_previous_goals, axis=1)
import ipdb; ipdb.set_trace()
goal_data.to_csv("data/generated/goal_history_data.csv")
