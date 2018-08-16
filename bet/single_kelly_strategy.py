import numpy as np
from bet.strategy import Strategy

class KellyStrategySingle(Strategy):
    def __init__(self, outcomes, predicted_outcomes, initial_capital=64):
        super().__init__(initial_capital=initial_capital)
        self.outcomes = outcomes
        self.predicted_outcomes = predicted_outcomes

    @staticmethod
    def calculate_optimal_fraction(b, p):
        return (b * p - (1-p))/b

    def get_optimal_fractions(self, odds, probabilities):
        fractions = np.zeros(3)
        for idx, (b, p) in enumerate(zip(odds, probabilities)):
            fractions[idx] = self.calculate_optimal_fraction(b, p)

        return fractions

    def run(self, odds, probabilities, coef=0.3):
        for _, (match_odds, match_probabilities, outcome, outcome_pred) in enumerate(zip(odds, probabilities, self.outcomes, self.predicted_outcomes)):
            net_match_odds = match_odds - 1
            bet_fractions = self.get_optimal_fractions(net_match_odds, match_probabilities)

            if outcome_pred == 1:
                odd_idx = 0
                f = bet_fractions[odd_idx]
            elif outcome_pred == 0:
                odd_idx = 1
                f = bet_fractions[odd_idx]
            elif outcome_pred == -1:
                odd_idx = 2
                f = bet_fractions[odd_idx]

            bet_size = self.balance * f * coef

            if bet_size < 0.1:
                bet_size = 0

            returns = 0
            if outcome_pred == outcome:
                returns = f * match_odds[odd_idx]
            self.update_balance(returns - bet_size)
            self.store_cost(bet_size)