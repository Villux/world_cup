import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimize

from simulation.analyse import get_win_probabilities, get_simulations

def kelly_function(params, odds, probabilities):
    a, b, c = params
    o1, o2, o3 = odds
    p1, p2, p3 = probabilities
    return -(p1 * np.log(1 + o1*a - b - c) + p2 * np.log(1 + o2*b - a - c) + p3*np.log(1 + o3*c - a - b))

def get_optimal_kelly(odds, probabilities):
    args = (odds, probabilities)
    bounds = ((0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
    max_iter = 20
    for i in range(max_iter):
        initial_guess = np.random.uniform(low=0.005, high=0.1, size=3)
        result = optimize.minimize(kelly_function, initial_guess, bounds=bounds, args=args)
        if result.success:
            break
        if i + 1 == max_iter:
            return [0.0, 0.0, 0.0]

    fs = result.x
    for i, f in enumerate(fs):
        if f < 0.0001:
            fs[i] = 0
    return fs

def plot_bank_and_bets(banks, bets):
    colors = {0: 'r', 1: 'g'}
    fig, ax = plt.subplots(figsize=(12, 12))
    index = np.arange(len(bets))
    ax.bar(index, bets)
    ax.plot(banks)
    ax.set_xticks(np.arange(0, 64))
    plt.xticks(rotation='vertical')

def run_unit_strategy(y_pred, y_true, odds, initial_capital=64, bet_size=1, plot=False):
    bets = []
    banks = []
    results = []

    bank = initial_capital

    for i in range(len(y_true)):
        if bank <= bet_size:
            print("Bank empty")
            break

        banks.append(bank)
        bets.append(bet_size)

        bank -= bet_size
        predicted_outcome = y_pred[i]
        if y_true[i] == predicted_outcome:
            if predicted_outcome == 1:
                odd = odds[i, 0]
            elif predicted_outcome == 0:
                odd = odds[i, 1]
            else:
                odd = odds[i, 2]
            bank += odd * bet_size
            results.append(1)
        else:
            results.append(0)

    if plot:
        print(f"Profit: {np.around((bank/initial_capital - 1)*100, 4)}%")
        print("Balance: ", bank)
        plot_bank_and_bets(banks, bets)
    return bank

def get_positive_kelly_fraction(b, p):
    q = 1-p
    f = max((b*p - q)/b, 0)
    return f

def run_kelly_strategy(y_true, odds, probabilities, initial_capital=64, plot=False, coef=0.3):
    bank = initial_capital

    bets = []
    banks = []
    for i, _ in enumerate(y_true):
        match_odds = odds[i, :]
        net_odds = match_odds - 1
        conservative_prob = probabilities[i, :] * coef
        fractions = get_optimal_kelly(net_odds, conservative_prob)

        winnings = 0
        total_bets = 0
        for k, (odd, f) in enumerate(zip(match_odds, fractions)):
            bet_size = bank * f * coef
            if bet_size < 0.1:
                bet_size = 0
            total_bets += bet_size

            outcome = 1 - k
            if y_true[i] == outcome:
                winnings = bet_size * odd
        bank -= total_bets
        bets.append(total_bets)

        bank += winnings
        banks.append(bank)

    if plot:
        print(f"Profit: {np.around((bank/initial_capital - 1)*100, 4)}%")
        print("Balance: ", bank)
        plot_bank_and_bets(banks, bets)
    return bank

def kelly_bet_most_probable(y_pred, y_true, odds, probabilities, initial_capital=64, plot=False):
    bank = initial_capital

    bets = []
    banks = []
    results = []
    for i in range(len(y_true)):
        predicted_outcome = y_pred[i]
        if predicted_outcome == 1:
            odd = odds[i, 0]
            p = probabilities[i, 0]
        elif predicted_outcome == 0:
            odd = odds[i, 1]
            p = probabilities[i, 1]
        else:
            odd = odds[i, 2]
            p = probabilities[i, 2]

        b = odd-1
        f = get_positive_kelly_fraction(b, p)
        bet_size = bank * f

        bets.append(bet_size)
        bank -= bet_size

        if y_true[i] == predicted_outcome:
            win = odd * bet_size
            bank += win
            results.append(1)
        else:
            results.append(0)
        banks.append(bank)

    if plot:
        print(f"Profit: {np.around((bank/initial_capital - 1)*100, 4)}%")
        print("Balance: ", bank)
        plot_bank_and_bets(banks, bets)
    return bank

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