import functools
import random
import time
import socket
import numpy as np
import pandas as pd

from features.data_provider import get_train_test_wc_dataset, get_feature_columns, get_whole_dataset
from simulation.predictor import OutcomePredictor
from simulation.simulation import run_simulation
from db.simulation_table import store_simulation_results
from models.outcome_model import get_model

X, y = get_whole_dataset("home_win")
match_template = pd.read_csv('data/original/wc_2018_games.csv')

for i in range(0, 100):
    print(f"Running simulation: {i}")

    model = get_model(X=X, y=y)
    predictor = OutcomePredictor(model)

    run_simulation(match_template, predictor, verbose=False)

store_simulation_results(f"data/simulations/outcome_{socket.gethostname()}_{round(time.time())}_simulation.csv")
