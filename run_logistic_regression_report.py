import datetime
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from sklearn.metrics import accuracy_score, log_loss
from sklearn.linear_model import LogisticRegression

from features.data_provider import all_features, other_features, player_features, DataLoader
from notebook_helpers import iterate_simulations, run_lr_model_for_features, simulation_iteration_report
from models.helpers import get_default_parameters, get_best_params


def write_log(filename, text, print_text=False):
    with open(filename, "a") as f:
        f.write(text + "\n")

    if print_text:
        print(text)


tournament_parameters = [
    ('data/original/wc_2018_games_real.csv', 'data/original/wc_2018_bets.csv', "2018-06-14"),
    ('data/original/wc_2014_games_real.csv', 'data/original/wc_2014_bets.csv', "2014-06-12"),
    ('data/original/wc_2010_games_real.csv', 'data/original/wc_2010_bets.csv', "2010-06-11")
]
feature_sets = [
    ("all_features", all_features),
    ("general_features", other_features),
    ("player_features", player_features)
]

file_name = "outcome_report_full.txt"

reports = []
for (name, feature_set) in feature_sets:
    write_log(file_name, str(datetime.datetime.now()))
    write_log(file_name, f"Running test for feature set: {name}", print_text=True)

    data_loader = DataLoader(feature_set)
    X, y = data_loader.get_all_data("home_win")

    params = {'n_jobs': cpu_count(), "solver": "newton-cg"}

    for (tt_file, bet_file, filter_start) in tournament_parameters:
        data_loader.set_filter_start(filter_start)
        simulations, units, kellys = iterate_simulations(data_loader,
                                                         tt_file,
                                                         bet_file,
                                                         run_lr_model_for_features,
                                                         params)
        report = simulation_iteration_report(simulations, units, kellys)
        report["id"] = f"{name}_{filter_start}"

        write_log(file_name, str(report), print_text=True)
        reports.append(report)

pd.DataFrame(reports).to_csv("gboost_outcome_model_report.csv")
