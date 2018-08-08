import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimize

from simulation.analyse import get_win_probabilities, get_simulations
from simulation.predictor import MaxProbabilityScorePredictor, MaxProbabilityOutcomePredictor
from simulation.simulation import run_actual_tournament_simulation
from features.data_provider import get_whole_dataset, set_feature_columns
from models import score_model, outcome_model
from db.simulation_table import get_simulation_results, delete_all
from bet.unit_strategy import UnitStrategy
from bet.kelly_strategy import KellyStrategy

def run_score_model_for_features(features, filter_start, tt_file, match_bet_file, n_estimators=2000):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    set_feature_columns(features)
    home = get_whole_dataset("home_score", filter_start=filter_start)
    away = get_whole_dataset("away_score", filter_start=filter_start)
    X = pd.concat([home[0], away[0]])
    y = pd.concat([home[1], away[1]])
    model = score_model.get_model(X=X, y=y, n_estimators=n_estimators)
    predictor = MaxProbabilityScorePredictor(model)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values)

def run_outcome_model_for_features(features, filter_start, tt_file, match_bet_file, n_estimators=2000):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    set_feature_columns(features)
    X, y = get_whole_dataset("home_win", filter_start=filter_start)
    model = outcome_model.get_model(X=X, y=y, n_estimators=n_estimators)
    predictor = MaxProbabilityOutcomePredictor(model)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values)

def get_tournament_simulation_results(tournament_template, predictor, odds):
    run_actual_tournament_simulation(tournament_template, predictor)
    tournament_simulation = get_simulation_results()
    tournament_simulation["true_outcome"] = np.sign(tournament_simulation["home_score"] - tournament_simulation["away_score"])
    delete_all()

    y_pred = tournament_simulation["outcome"].values
    y_true = tournament_simulation["true_outcome"].values
    unit_strategy = UnitStrategy(y_pred, y_true)
    unit_strategy.run(odds)

    kelly_strategy = KellyStrategy(y_true)
    probabilities = tournament_simulation[["home_win_prob", "draw_prob", "away_win_prob"]].values
    kelly_strategy.run(odds, probabilities)

    return tournament_simulation, unit_strategy, kelly_strategy

def get_feature_by_importance(model, feature_columns):
    return sorted(zip(feature_columns, model.feature_importances_), key = lambda t: t[1], reverse=True)

def write_report(accuracy, unit, kelly, header, filename):
    print("AVG Accuracy: ", np.mean(accuracy), np.std(accuracy))
    print("AVG Unit profit: ", np.mean(unit), np.std(unit))
    print("AVG Kelly profit: ", np.mean(kelly), np.std(kelly))

    with open(filename, "a") as myfile:
        myfile.write(header + "\n")
        myfile.write(f"Accuracy: {np.mean(accuracy)} {np.std(accuracy)} \n")
        myfile.write(f"Unit profit: {np.mean(unit)} {np.std(unit)} \n")
        myfile.write(f"Kelly profit: {np.mean(kelly)} {np.std(kelly)} \n")
        myfile.write(f"\n\n\n")

def plot_bank_and_bets(strategy):
    initial_capital = strategy.initial_capital
    net_returns = np.array(strategy.get_returns())
    returns = net_returns + 1
    returns[0] *= initial_capital
    costs = strategy.costs

    balance_progression = np.cumprod(returns)
    bar_labels = [1 if value > 0 else 0 for value in net_returns]

    net_flows = balance_progression - np.insert(balance_progression, 0, initial_capital)[:-1]
    winnnings = np.array([value if value > 0 else 0 for value in net_flows])

    figsize = (12, 6)
    colors = {0: 'r', 1: 'g'}
    fig, ax = plt.subplots(figsize=figsize)
    index = np.arange(len(costs))
    ax.bar(index, costs, color='r')
    ax.bar(index, winnnings, color='g', bottom=costs)
    ax.set_xticks(np.arange(0, len(net_returns)))
    plt.xticks(rotation='vertical')

    plt.subplots(figsize=figsize)
    plt.xticks(np.arange(0, len(net_returns)))
    plt.xticks(rotation='vertical')
    plt.plot(balance_progression)

def get_tournament_results(simulations_files, tournament_template_file, filename=None):
    tournament_template = pd.read_csv(tournament_template_file)
    teams = pd.unique(tournament_template[['home_team', 'away_team']].values.ravel('K'))[0:32]
    match_ids = tournament_template["id"]

    simulations = get_simulations(simulations_files)
    print("Total number of simulations", simulations.shape)

    match_wise_probabilities = get_win_probabilities(simulations, teams, match_ids)

    match_simulations = []

    tournament_template.set_index('id')
    for i in range(tournament_template.shape[0]):
        match_id = tournament_template.loc[i, "id"]
        away_team = tournament_template.loc[i, "away_team"]
        home_team = tournament_template.loc[i, "home_team"]

        home_win_prob = match_wise_probabilities.loc[
            (match_wise_probabilities["match_id"] == match_id) &
            (match_wise_probabilities["team"] == home_team), "win_prob"].item()

        away_win_prob = match_wise_probabilities.loc[
            (match_wise_probabilities["match_id"] == match_id) &
            (match_wise_probabilities["team"] == away_team), "win_prob"].item()

        draw_prob = 1 - home_win_prob - away_win_prob

        if (home_win_prob > away_win_prob) and (home_win_prob > draw_prob):
            outcome = 1
        elif (away_win_prob > home_win_prob) and (away_win_prob > draw_prob):
            outcome = -1
        else:
            outcome = 0

        match_simulation = {
            "home_team": home_team,
            "away_team": away_team,
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "outcome": outcome,
            "true_outcome": np.sign(tournament_template.loc[i, "home_score"] - tournament_template.loc[i, "away_score"])
        }
        match_simulations.append(match_simulation)

    tournament_simulation = pd.DataFrame(match_simulations)
    if filename:
        tournament_simulation.to_csv(filename)

    print("Accuracy:", sum(tournament_simulation["outcome"] == tournament_simulation["true_outcome"]) / tournament_template.shape[0])
    return tournament_simulation