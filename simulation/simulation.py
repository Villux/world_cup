import pandas as pd

from features.elo import update_elo_after_match, attach_elo_to_match
from db.match_table import delete_simulations
from db.elo_table import delete_elos_after_date
from db.simulation_table import insert, get_win_probability
from simulation.match import Match, insert_match
from simulation.group_table import GroupTable

def clean_after_simulation():
    simulation_start_date = "2018-06-13"
    delete_elos_after_date(simulation_start_date)
    delete_simulations()

def insert_match_simulation(match):
    match_dict = match.to_dict()
    match_dict["match_id"] = match.id
    match_dict["outcome"] = match.get_outcome()
    match_dict.pop('tournament', None)
    insert(**match_dict)

def post_match_results(match):
    match_id = insert_match(match)
    home_elo, away_elo = attach_elo_to_match(match_id, match.home_team, match.away_team)
    update_elo_after_match(match.date, home_elo, away_elo, match.home_team,
                           match.away_team, match.home_score, match.away_score, match.tournament)

    insert_match_simulation(match)

class WorldCupSimulator():
    def __init__(self, match_templates, table, predictor, verbose=True):
        self.match_templates = match_templates
        self.group_table = table
        self.predictor = predictor
        self.verbose = verbose

    def print(self, text, end='\n'):
        if self.verbose:
            print(text, end=end)

    def print_match_result(self, match):
        self.print(f"{match.home_team} - {match.away_team}: ", end='')
        self.print(f"{match.get_outcome()}        -- probabilities [Lose, Draw, Win] -- {match.outcome_probabilities}")

    def simulate_match(self, match):
        match = self.predictor.predict(match)
        post_match_results(match)
        self.print_match_result(match)
        return match

    def simulate_group_stage(self):
        self.print("\n\n\n___Group Stage___\n")
        for _, match_template in self.match_templates.iloc[0:48].iterrows():
            match = Match(match_template)
            match = self.simulate_match(match)
            self.group_table.update_table(match.home_team, match.away_team, match.get_outcome())

    def simulate_round_of_16(self):
        i = 0
        self.print("\n\n\n___Round of 16___\n")
        for index, match_template in self.match_templates.iloc[48:56].iterrows():
            home_group, home_position = list(match_template["home_team"])
            match_template["home_team"] = self.group_table.get_team(home_group, int(home_position) - 1)
            away_group, away_position = list(match_template["away_team"])
            match_template["away_team"] = self.group_table.get_team(away_group, int(away_position) - 1)

            match = Match(match_template, win_or_lose=True)
            match = self.simulate_match(match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match.get_outcome() == 1:
                self.match_templates.loc[56 + i, team_col] = match.home_team
            else:
                self.match_templates.loc[56 + i, team_col] = match.away_team
            if index%2 != 0:
                i += 1

    def simulate_quarter_finals(self):
        i = 0
        self.print("\n\n\n___Quarter-Finals___\n")
        for index, match_template in self.match_templates.iloc[56:60].iterrows():
            match = Match(match_template, win_or_lose=True)
            match = self.simulate_match(match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match.get_outcome() == 1:
                self.match_templates.loc[60 + i, team_col] = match.home_team
            else:
                self.match_templates.loc[60 + i, team_col] = match.away_team
            if index%2 != 0:
                i += 1

    def simulate_semi_finals(self):
        self.print("\n\n\n___Semi-Finals___\n")
        for index, match_template in self.match_templates.iloc[60:62].iterrows():
            match = Match(match_template, win_or_lose=True)
            match = self.simulate_match(match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match.get_outcome() == 1:
                self.match_templates.loc[63, team_col] = match.home_team
                self.match_templates.loc[62, team_col] = match.away_team
            else:
                self.match_templates.loc[63, team_col] = match.away_team
                self.match_templates.loc[62, team_col] = match.home_team

    def simulate_third_place_play_off(self):
        self.print("\n\n\n___Third place play-off___\n")
        for _, match_template in self.match_templates.iloc[62:63].iterrows():
            match = Match(match_template, win_or_lose=True)
            match = self.simulate_match(match)

    def simulate_finals(self):
        self.print("\n\n\n___Final___\n")
        for _, match_template in self.match_templates.iloc[63:].iterrows():
            match = Match(match_template, win_or_lose=True)
            match = self.simulate_match(match)

    def simulate_tournament(self):
        self.simulate_group_stage()
        if self.verbose:
            self.group_table.print_group_standings()
        self.simulate_round_of_16()
        self.simulate_quarter_finals()
        self.simulate_semi_finals()
        self.simulate_third_place_play_off()
        self.simulate_finals()

def run_simulation(match_template, predictor, verbose=False):
    group_table = GroupTable(match_template)
    tournament = WorldCupSimulator(match_template, group_table, predictor, verbose=verbose)

    tournament.simulate_tournament()
    clean_after_simulation()


def get_match_win_probability(teams, match_id):
    prob_dict = {}
    for team in teams:
        prob = get_win_probability(team, match_id)
        prob_dict[team] = prob

    return prob_dict
