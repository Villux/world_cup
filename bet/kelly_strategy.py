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

def kelly_function_deriv(params, odds, probabilities):
    a, b, c = params
    o1, o2, o3 = odds
    p1, p2, p3 = probabilities
    dfda = -(p1 * o1)/(o1*a-b-c+1) + p2/(o2*b-a-c+1) + p3/(o3*c-b-a+1)
    dfdb = p1/(o1*a-b-c+1) - (p2 * o2)/(o2*b-a-c+1) + p3/(o3*c-b-a+1)
    dfdc = p1/(o1*a-b-c+1) + p2/(o2*b-a-c+1) - (p3*o3)/(o3*c-b-a+1)
    return np.array([dfda, dfdb, dfdc])

def constraint(x):
    return 1.00000001 - (x[0]+x[1]+x[2])

class KellyStrategy(Strategy):
    def __init__(self, outcomes, initial_capital=64):
        super().__init__(initial_capital=initial_capital)
        self.outcomes = outcomes
        self.max_iterations = 20

        self.opf = []

    def get_optimal_fractions(self, odds, probabilities):
        args = (odds, probabilities)
        bounds = ((0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
        cons = {'type': 'ineq', 'fun': constraint}
        for i in range(self.max_iterations):
            initial_guess = [0.05, 0.05, 0.05]
            result = optimize.minimize(
                kelly_function,
                initial_guess,
                bounds=bounds,
                constraints=cons,
                args=args,
                jac=kelly_function_deriv
            )

            if result.success:
                break
            if i + 1 == self.max_iterations:
                return [0.0, 0.0, 0.0]

        fs = result.x
        for i, f in enumerate(fs):
            if f < 0.0001:
                fs[i] = 0
        return fs

    def get_odds_probabilities_and_fractions(self):
        return self.opf

    def run(self, odds, probabilities, coef=0.3):
        for _, (match_odds, match_probabilities, outcome) in enumerate(zip(odds, probabilities, self.outcomes)):
            net_match_odds = match_odds - 1
            bet_fractions = self.get_optimal_fractions(net_match_odds, match_probabilities)

            self.opf.append(list(zip(match_odds, match_probabilities, bet_fractions)))

            cost = 0
            returns = 0
            for k, (odd, fraction) in enumerate(zip(match_odds, bet_fractions)):
                bet_size = self.balance * fraction * coef
                if bet_size < 0.1:
                    bet_size = 0
                cost += bet_size
                if outcome == 1 - k:
                    returns += bet_size * odd
            self.update_balance(returns - cost)
            self.store_cost(cost)
