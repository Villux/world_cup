import os
import argparse
import time
import socket
import pandas as pd

from features.data_provider import get_whole_dataset, set_feature_columns, other_features
from simulation.predictor import OutcomePredictor,ScorePredictor
from simulation.simulation import run_actual_tournament_simulation
from db.simulation_table import store_simulation_results
from models import outcome_model, score_model

parser = argparse.ArgumentParser()
parser.add_argument('--outcome', action="store_true")
parser.add_argument('--limited-features', action="store_true")
parser.add_argument('--match-template', type=str, default='data/original/wc_2018_games_real.csv')
parser.add_argument('-i', type=int, default=100)
args = parser.parse_args()

simulation_name = os.path.splitext(os.path.basename(args.match_template))[0]
simulation_id = f"{socket.gethostname()}_{round(time.time())}"
simulation_model = "outcome" if args.outcome else "score"

if args.limited_features:
    set_feature_columns(other_features)
    simulation_name = simulation_name + "_limfeatures"

if args.outcome:
    X, y = get_whole_dataset("home_win")
else:
    home = get_whole_dataset("home_score")
    away = get_whole_dataset("away_score")
    X = pd.concat([home[0], away[0]])
    y = pd.concat([home[1], away[1]])

print("Feature set shape:", X.shape)

for i in range(args.i):
    if args.outcome:
        model = outcome_model.get_model(X=X, y=y)
        predictor = OutcomePredictor(model)
    else:
        model = score_model.get_model(X=X, y=y)
        predictor = ScorePredictor(model)

    print(f"Running match-level tournament simulation: {i}")

    match_template = pd.read_csv(args.match_template)
    run_actual_tournament_simulation(match_template, predictor)

filename = f"data/simulations/{simulation_name}_{simulation_model}_{simulation_id}.csv"
store_simulation_results(filename)
