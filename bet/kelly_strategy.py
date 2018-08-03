import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimize

from bet.strategy import Strategy

def kelly_function(params, odds, probabilities):
    a, b, c = params
    o1, o2, o3 = odds
    p1, p2, p3 = probabilities
    return -(p1 * np.log(1 + o1*a - b - c) + p2 * np.log(1 + o2*b - a - c) + p3*np.log(1 + o3*c - a - b))

class KellyStrategy(Strategy):
    def __init__(self, outcomes, initial_capital=64):
        super().__init__(initial_capital=initial_capital)
        self.outcomes = outcomes
        self.max_iterations = 20

        self.odds_and_fractions = []

    def get_optimal_fractions(self, odds, probabilities):
        args = (odds, probabilities)
        bounds = ((0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
        for i in range(self.max_iterations):
            initial_guess = np.random.uniform(low=0.005, high=0.1, size=3)
            result = optimize.minimize(kelly_function, initial_guess, bounds=bounds, args=args)
            if result.success:
                break
            if i + 1 == self.max_iterations:
                return [0.0, 0.0, 0.0]

        fs = result.x
        for i, f in enumerate(fs):
            if f < 0.0001:
                fs[i] = 0
        return fs

    def run(self, odds, probabilities, coef=0.3):
        for _, (match_odds, match_probabilities, outcome) in enumerate(zip(odds, probabilities, self.outcomes)):
            net_match_odds = match_odds - 1
            bet_fractions = self.get_optimal_fractions(net_match_odds, match_probabilities)

            cost = 0
            returns = 0
            odds_and_fractions = zip(match_odds, bet_fractions)
            for k, (odd, fraction) in enumerate(odds_and_fractions):
                bet_size = self.balance * fraction * coef
                if bet_size < 0.1:
                    bet_size = 0
                cost += bet_size
                if outcome == 1 - k:
                    returns += bet_size * odd

            self.update_balance(returns - cost)
            self.odds_and_fractions.append(odds_and_fractions)
            self.store_cost(cost)
