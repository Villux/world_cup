import argparse
import functools
import random
import time
import socket
import numpy as np
import pandas as pd

from features.data_provider import get_train_test_wc_dataset, get_feature_columns, get_whole_dataset
from simulation.predictor import OutcomePredictor
from simulation.simulation import run_simulation, run_actual_tournament_simulation
from db.simulation_table import store_simulation_results
from models.outcome_model import get_model

parser = argparse.ArgumentParser()
parser.add_argument('--actual', action="store_true")
args = parser.parse_args()

X, y = get_whole_dataset("home_win")

for i in range(0, 100):
    model = get_model(X=X, y=y)
    predictor = OutcomePredictor(model)

    if args.actual:
        prefix = "matchlevel"
        print(f"Running match-level tournament simulation: {i}")

        match_template = pd.read_csv('data/original/wc_2018_games_real.csv')
        run_actual_tournament_simulation(match_template, predictor)
    else:
        prefix = "full"
        print(f"Running full tournament simulation: {i}")

        match_template = pd.read_csv('data/original/wc_2018_games.csv')
        run_simulation(match_template, predictor)

store_simulation_results(f"data/simulations/{prefix}_outcome_{socket.gethostname()}_{round(time.time())}_simulation.csv")
