from bet.strategy import Strategy

class UnitStrategy(Strategy):
    def __init__(self, predicted_outcomes, outcomes, initial_capital=64, bet_size=1):
        assert len(predicted_outcomes) == len(outcomes)
        super().__init__(initial_capital=initial_capital)

        self.predicted_outcomes = predicted_outcomes
        self.outcomes = outcomes
        self.bet_size = bet_size

    @staticmethod
    def get_odd(match_odds, outcome):
        odd_index = -outcome + 1
        return match_odds[odd_index]

    def run(self, odds):
        assert len(odds) == len(self.predicted_outcomes)

        for _, (match_odds, y_hat, y) in enumerate(zip(odds, self.predicted_outcomes, self.outcomes)):
            if y_hat == y:
                odd = self.get_odd(match_odds, y)
                profit = odd * self.bet_size - self.bet_size
                self.update_balance(profit)
            else:
                self.update_balance(-self.bet_size)
