import numpy as np

class BankEmptyException(Exception):
    pass

class Strategy():
    def __init__(self, initial_capital=64):
        self.initial_capital = initial_capital
        self.balance = initial_capital
        self.single_bet_returns = []
        self.costs = []

    def update_balance(self, net_flow):
        self.single_bet_returns.append(net_flow/self.balance)
        new_balance = self.balance + net_flow
        if new_balance < 0:
            raise BankEmptyException("No balance to execute bet")
        self.balance = new_balance

    def store_cost(self, cost):
        self.costs.append(cost)

    def get_balance(self):
        return self.balance

    def get_returns(self):
        return self.single_bet_returns

    def get_total_profit(self):
        return self.balance/self.initial_capital

    def get_costs(self):
        return self.costs
