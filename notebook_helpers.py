from multiprocessing import Pool, cpu_count
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss, precision_score, f1_score, recall_score
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from simulation.analyse import get_win_probabilities, get_simulations
from simulation.predictor import MaxProbabilityScorePredictor, MaxProbabilityOutcomePredictor, OneVsRestPredictor, ScorePredictor
from simulation.simulation import run_actual_tournament_simulation
from models import score_model, outcome_model, one_vs_all_model, gboost_model, lr_model
from db.simulation_table import get_simulation_results, delete_all
from bet.unit_strategy import UnitStrategy
from bet.kelly_strategy import KellyStrategy

DEFAULT_N_ESTIMATORS = 2000

def run_score_model_for_features(data_loader, tt_file, match_bet_file, params):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    Xhome, yhome, Xaway, yaway = data_loader.get_all_data(["home_score", "away_score"])
    X = pd.concat([Xhome, Xaway])
    y = pd.concat([yhome, yaway])
    model = score_model.get_model(X=X, y=y, params=params)
    predictor = MaxProbabilityScorePredictor(model, data_loader)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values), model

def run_outcome_model_for_features(data_loader, tt_file, match_bet_file, params):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    X, y = data_loader.get_all_data("home_win")
    model = outcome_model.get_model(X=X, y=y, params=params)
    predictor = MaxProbabilityOutcomePredictor(model, data_loader)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values), model

def run_gboost_model_for_features(data_loader, tt_file, match_bet_file, params):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    X, y = data_loader.get_all_data("home_win")
    model = gboost_model.get_model(X=X, y=y, params=params)
    predictor = MaxProbabilityOutcomePredictor(model, data_loader)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values), model

def run_lr_model_for_features(data_loader, tt_file, match_bet_file, params):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    X, y = data_loader.get_all_data("home_win")
    model = lr_model.get_model(X=X, y=y, params=params)
    predictor = MaxProbabilityOutcomePredictor(model, data_loader)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values), model

def run_one_vs_rest_for_features(data_loader, tt_file, match_bet_file, params):
    tournament_template = pd.read_csv(tt_file)
    match_bets = pd.read_csv(match_bet_file)

    X, y = data_loader.get_all_data("home_win")

    home_model = one_vs_all_model.get_home(X=X, y=fix_label(y, 1), params=params[0], calibration="sigmoid")
    draw_model = one_vs_all_model.get_draw(X=X, y=fix_label(y, 0), params=params[1], calibration="sigmoid")
    away_model = one_vs_all_model.get_away(X=X, y=fix_label(y, -1), params=params[2], calibration="sigmoid")

    predictor = OneVsRestPredictor(home_model, draw_model, away_model, data_loader)

    return get_tournament_simulation_results(tournament_template, predictor, match_bets[["1", "X", "2"]].values), (home_model, draw_model, away_model)

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

def iterate_simulations(data_loader, tournament_template_file, bet_file, simulation_f, params, iter_n=10):
    simulations = np.empty(iter_n, dtype=object)
    unit_strategies = np.empty(iter_n, dtype=object)
    kelly_strategies = np.empty(iter_n, dtype=object)


    for i in range(iter_n):
        (simulation, unit, kelly), _ = simulation_f(data_loader, tournament_template_file, bet_file, params)
        simulations[i] = simulation
        unit_strategies[i] = unit
        kelly_strategies[i] = kelly

    return simulations, unit_strategies, kelly_strategies

def get_feature_by_importance(model, feature_columns):
    return sorted(zip(feature_columns, model.feature_importances_), key = lambda t: t[1], reverse=True)

def get_accuracy(y_true, y_pred):
    return accuracy_score(y_true, y_pred)

def get_log_loss(y_true, y_pred_proba):
    labels = np.unique(y_true)
    return log_loss(y_true, y_pred_proba, labels=labels)

def simulation_iteration_report(simulations, unit_strategies, kelly_strategies):
    accuracies = [get_accuracy(simulation["true_outcome"], simulation["outcome"]) for simulation in simulations]
    log_losses = [get_log_loss(simulation["true_outcome"], simulation[['away_win_prob', 'draw_prob', 'home_win_prob']]) for simulation in simulations]
    precisions = [precision_score(simulation["true_outcome"], simulation["outcome"], average=None) for simulation in simulations]
    recall_scores = [recall_score(simulation["true_outcome"], simulation["outcome"], average=None) for simulation in simulations]
    f1_scores = [f1_score(simulation["true_outcome"], simulation["outcome"], average=None) for simulation in simulations]

    unit_profits = [unit.get_total_profit() for unit in unit_strategies]
    kelly_profits = [kelly.get_total_profit() for kelly in kelly_strategies]

    accuracy_mu, accuracy_std = np.mean(accuracies), np.std(accuracies)
    logloss_mu, logloss_std = np.mean(log_losses), np.std(log_losses)
    precision_mu, precision_std = np.mean(precisions, axis=0), np.std(precisions, axis=0)
    recall_mu, recall_std = np.mean(recall_scores, axis=0), np.std(recall_scores, axis=0)
    f1_mu, f1_std = np.mean(f1_scores, axis=0), np.std(f1_scores, axis=0)
    unit_mu, unit_std = np.mean(unit_profits), np.std(unit_profits)
    kelly_mu, kelly_std = np.mean(kelly_profits), np.std(kelly_profits)

    report = {
        "acc_mu":accuracy_mu,
        "acc_std":accuracy_std,
        "logloss_mu": logloss_mu,
        "logloss_std": logloss_std,
        "precision_mu":precision_mu,
        "precision_std": precision_std,
        "recall_mu": recall_mu,
        "recall_std":recall_std,
        "f1_mu": f1_mu,
        "f1_std": f1_std,
        "unit_mu": unit_mu,
        "unit_std": unit_std,
        "kelly_mu": kelly_mu,
        "kelly_std": kelly_std
    }
    return report

def plot_bank_and_bets(strategy):
    initial_capital = strategy.initial_capital
    net_returns = np.array(strategy.get_returns())
    returns = net_returns + 1
    returns[0] *= initial_capital
    costs = np.array(strategy.costs) * -1

    balance_progression = np.cumprod(returns)
    bar_labels = [1 if value > 0 else 0 for value in net_returns]

    net_flows = balance_progression - np.insert(balance_progression, 0, initial_capital)[:-1]
    winnnings = np.array([value if value > 0 else 0 for value in net_flows])

    figsize = (12, 6)
    colors = {0: 'r', 1: 'g'}
    fig, ax = plt.subplots(figsize=figsize)
    index = np.arange(len(costs))
    ax.bar(index, winnnings, color='g')
    ax.bar(index, costs, color='r')

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

    print("Accuracy:", get_accuracy(tournament_simulation["true_outcome"], tournament_simulation["outcome"]))
    return tournament_simulation

def fix_label(data, label):
    y = data.copy()
    if label == 1:
        y.loc[y != 1] = 0
    elif label == 0:
        y.loc[y != 0] = -100
        y.loc[y == 0] = 1
        y.loc[y == -100] = 0
    elif label == -1:
        y.loc[y != -1] = 0
        y.loc[y == -1] = 1
    return y

def plot_reliability_diagram(probas, y):
    data_matrix = np.hstack((probas, y.reshape(y.shape[0], 1)))

    true_positive_rates = []
    x = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    for ub in x:
        true_positives = 0
        all_outcomes = 0
        lb = (ub-0.1)
        for idx, (q, p, outcome) in enumerate(data_matrix):
            if p > lb and p <= ub:
                true_positives += outcome
                all_outcomes += 1
        if all_outcomes == 0:
            true_positive_rates.append(0.0)
        else:
            true_positive_rates.append(true_positives / all_outcomes)

    print("Brier Score", brier_score_loss(y, data_matrix[:, 0]))
    print("Log loss", get_log_loss(y, data_matrix[:, 0]))

    diagonal_line = np.linspace(0, 1, 100)
    plt.plot(diagonal_line,diagonal_line)
    plt.scatter(x, true_positive_rates)

def plot_simulation(data):
    tournament_simulation = data["simulation"]
    print("Accuracy:", get_accuracy(tournament_simulation["true_outcome"], tournament_simulation["outcome"]))
    plot_bank_and_bets(data["unit"])
    plot_bank_and_bets(data["kelly"])

def get_model_metrics(args):
    params = args[0]
    Xtrain, ytrain = args[1], args[2]
    Xtest, ytest = args[3], args[4]
    model = RandomForestClassifier(**params)
    model.fit(Xtrain, ytrain)
    y_true, y_pred = ytest, model.predict(Xtest)
    y_pred_prob = model.predict_proba(Xtest)

    labels = np.unique(y_true)
    return accuracy_score(y_true, y_pred), get_log_loss(y_true, y_pred_prob)

def get_cv_grid_search_arguments(org_params, X):
    kf_splits = 5
    kf = KFold(n_splits=kf_splits)
    arguments = []
    for depth in [3, 5, 8, 12, None]:
        for min_samples in [1, 3, 5, 10, 15]:
            for max_features in ["sqrt", "log2"]:
                params = org_params.copy()
                params["max_depth"] = depth
                params["min_samples_leaf"] = min_samples
                params["max_features"] = max_features

                arg_array = []
                for train_index, test_index in kf.split(X):
                    arg_array.append((params, train_index, test_index))
                arguments.append(arg_array)

    return arguments

def run_grid_search_for_outcome(arguments, X, y):
    metrics = []
    pool = Pool(cpu_count())
    for cv_args in arguments:
        args = []
        cv_params = {}
        for (params, train_index, test_index) in cv_args:
            args.append((params, X.iloc[train_index], y.iloc[train_index], X.iloc[test_index], y.iloc[test_index]))
            cv_params = params
        results = pool.map(get_model_metrics, args)
        metrics.append({
            "max_depth": cv_params["max_depth"],
            "min_samples_leaf": cv_params["min_samples_leaf"],
            "max_features": cv_params["max_features"],
            "test_acc": np.mean([result[0] for result in results]),
            "test_logloss": np.mean([result[1] for result in results])
        })
    return pd.DataFrame(metrics)

def get_score_model_metrics(args):
    params = args[0]
    Xhome_train, yhome_train = args[1], args[2]
    Xhome_test = args[3]
    Xaway_train, yaway_train = args[4], args[5]
    Xaway_test = args[6]
    outcome_test = args[7]

    Xtrain = pd.concat([Xhome_train, Xaway_train])
    ytrain = pd.concat([yhome_train, yaway_train])
    model = RandomForestRegressor(**params)
    model.fit(Xtrain, ytrain)

    predicted_outcomes = []
    predicted_outcome_probabilities = []
    for i in range(Xhome_test.shape[0]):
        home_fv = [Xhome_test.iloc[i].as_matrix()]
        away_fv = [Xaway_test.iloc[i].as_matrix()]
        home_mu = model.predict(home_fv)
        away_mu = model.predict(away_fv)

        goal_matrix = ScorePredictor.get_goal_matrix(home_mu, away_mu)
        away_win, draw, home_win = ScorePredictor.get_outcome_probabilities(goal_matrix)

        if home_win > away_win and home_win > draw:
            outcome = 1
        elif away_win > home_win and away_win > draw:
            outcome = -1
        elif draw > home_win and draw > away_win:
            outcome = 0
        else:
            outcome = 1
        predicted_outcomes.append(outcome)
        predicted_outcome_probabilities.append([away_win, draw, home_win])

    accuracy = accuracy_score(outcome_test.values, predicted_outcomes)
    log_loss_score = get_log_loss(outcome_test.values, np.array(predicted_outcome_probabilities))

    return accuracy, log_loss_score

def run_grid_search_for_score(arguments, Xhome, yhome, Xaway, yaway, outcomes):
    metrics = []
    pool = Pool(cpu_count())
    for cv_args in arguments:
        args = []
        cv_params = {}
        for (params, train_index, test_index) in cv_args:
            Xhome_train = Xhome.iloc[train_index]
            yhome_train = yhome.iloc[train_index]
            Xhome_test = Xhome.iloc[test_index]

            Xaway_train = Xaway.iloc[train_index]
            yaway_train = yaway.iloc[train_index]
            Xaway_test = Xaway.iloc[test_index]

            outcomes_test = outcomes.iloc[test_index]

            args.append((params, Xhome_train, yhome_train, Xhome_test,
                   Xaway_train, yaway_train, Xaway_test, outcomes_test))
            cv_params = params
        results = pool.map(get_score_model_metrics, args)
        metrics.append({
            "max_depth": cv_params["max_depth"],
            "min_samples_leaf": cv_params["min_samples_leaf"],
            "max_features": cv_params["max_features"],
            "test_acc": np.mean([result[0] for result in results]),
            "test_logloss": np.mean([result[1] for result in results])
        })
    return pd.DataFrame(metrics)

