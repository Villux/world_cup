import functools
import random
import time
import socket
import numpy as np
import pandas as pd

from features.data_provider import get_train_test_wc_dataset, get_feature_columns, get_whole_dataset
from simulation.predictor import ScorePredictor
from simulation.simulation import run_simulation, get_match_win_probability
from db.simulation_table import store_simulation_results
from models.score_model import get_model

home = get_whole_dataset("home_score")
away = get_whole_dataset("away_score")

X = pd.concat([home[0], away[0]])
y = pd.concat([home[1], away[1]])

model = get_model(X=X, y=y)

match_template = pd.read_csv('data/original/wc_2018_games.csv')
predictor = ScorePredictor(model)

for i in range(0, 1000):
    print(f"Running simulation: {i}")
    run_simulation(match_template, predictor)

teams = pd.unique(match_template[['home_team', 'away_team']].values.ravel('K'))[0:32]
print(get_match_win_probability(teams, 63))

store_simulation_results(f"data/simulations/{socket.gethostname()}_{round(time.time())}_simulation.csv")