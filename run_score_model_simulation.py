import functools
import random
import time
import socket
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from features.data_provider import get_train_test_wc_dataset, get_feature_columns, get_whole_dataset
from simulation.predictor import ScorePredictor
from simulation.simulation import run_simulation, get_match_win_probability
from db.simulation_table import store_simulation_results


home = get_whole_dataset("home_score")
away = get_whole_dataset("away_score")

X = pd.concat([home[0], away[0]])
y = pd.concat([home[1], away[1]])

params = {
    'oob_score' : True,
    'bootstrap': True,
    'n_jobs':-1,
    'n_estimators': 1000,
    "max_depth": None,
    "min_samples_leaf": 5,
    "max_features": "sqrt"
}

clf = RandomForestRegressor(**params)
clf.fit(X, y)

match_template = pd.read_csv('data/original/wc_2018_games.csv')
predictor = ScorePredictor(clf)

for i in range(0, 1000):
    print(f"Running simulation: {i}")
    run_simulation(match_template, predictor)

teams = pd.unique(match_template[['home_team', 'away_team']].values.ravel('K'))[0:32]
print(get_match_win_probability(teams, 63))

store_simulation_results(f"data/simulations/{socket.gethostname()}_{round(time.time())}_simulation.csv")
