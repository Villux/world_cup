import functools
import random
import numpy as np
import pandas as pd
from dateutil.parser import parse

from features.generate_goal_features import calculate_goal_features_for_match
from features.data_provider import append_player_data, get_feature_vector
from db.match_table import insert, delete_simulations
from features.elo import update_elo_after_match, get_current_elo, attach_elo_to_match
from db.elo_table import delete_elos_after_date
from match import Match
from group_table import GroupTable
from predictor import Predictor

def post_simulation():
    simulation_start_date = "2018-06-13"
    delete_elos_after_date(simulation_start_date)
    delete_simulations()

class WorldCupSimulator():
    def __init__(self, match_templates, table, predictor, verbose=True):
        self.match_templates = match_templates
        self.group_table = table
        self.predictor = predictor
        self.verbose = verbose

    def print(self, text, end='\n'):
        if self.verbose:
            print(text, end=end)

    def predict_match(self, match):
        x = self.get_match_feature_vector(match)
        match.set_feature_vector(x)

        outcome_probabilities = self.predictor.predict_outcome_probabilities(x)
        match.set_outcome_probabilties(outcome_probabilities)

        home_score, away_score = self.predictor.predict_score(x, match.get_outcome())
        match.set_score(home_score, away_score)
        return match

    def post_match_results(self, match):
        db_obj = match.to_dict()
        db_obj["year"] = parse(db_obj["date"]).year
        db_obj["simulation"] = True
        match_id = insert(**db_obj)
        home_elo, away_elo = attach_elo_to_match(match_id, match.home_team, match.away_team)
        update_elo_after_match(match.date, home_elo, away_elo, match.home_team,
                               match.away_team, match.home_score, match.away_score, match.tournament)

    def get_match_feature_vector(self, match):
        data_merge_obj = {"home_team": match.home_team, "away_team": match.away_team, "date": match.date}
        data_merge_obj["year"] = parse(match.date).year

        # ELO
        home_elo = get_current_elo(match.home_team)
        away_elo = get_current_elo(match.away_team)
        data_merge_obj["home_elo"] = home_elo
        data_merge_obj["away_elo"] = away_elo

        # Goals
        goal_data = calculate_goal_features_for_match(match.date, match.home_team, match.away_team)
        for key, value in goal_data.items():
            data_merge_obj[key] = value

        # Player data
        data_merge_obj = pd.DataFrame([data_merge_obj])
        data_merge_obj = append_player_data(data_merge_obj)
        return get_feature_vector(data_merge_obj)

    def print_match_result(self, match):
        self.print(f"{match.home_team} - {match.away_team}: ", end='')
        self.print(f"{match.get_outcome()}        -- probabilities [Lose, Draw, Win] -- {match.outcome_probabilities}")

    def simulate_match(self, match):
        match = self.predict_match(match)
        self.post_match_results(match)
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

            match = Match(match_template)
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
            match = Match(match_template)
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
            match = Match(match_template)
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
            match = Match(match_template)
            match = self.simulate_match(match)

    def simulate_finals(self):
        self.print("\n\n\n___Final___\n")
        for _, match_template in self.match_templates.iloc[63:].iterrows():
            match = Match(match_template)
            match = self.simulate_match(match)

    def simulate_tournament(self):
        self.simulate_group_stage()
        self.group_table.print_group_standings()
        self.simulate_round_of_16()
        self.simulate_quarter_finals()
        self.simulate_semi_finals()
        self.simulate_third_place_play_off()
        self.simulate_finals()

def run_simulation(outcome_model, home_score_model, away_score_model):
    wc_2018_matches_templates = pd.read_csv('data/original/wc_2018_games.csv')
    group_table = GroupTable(wc_2018_matches_templates)
    predictor = Predictor(outcome_model, home_score_model, away_score_model)
    wc_2018 = WorldCupSimulator(wc_2018_matches_templates, group_table, predictor)

    wc_2018.simulate_tournament()
    post_simulation()

class DummyPredictor():
    def __init__(self, classes):
        self.classes = classes

    def predict(self, *arg):
        return [random.choice(self.classes)]

    def predict_proba(self, *arg):
        return [np.random.rand(len(self.classes))]


if __name__ == "__main__":
    sign_model = DummyPredictor([-1, 0, 1])
    home_score_model = DummyPredictor([0, 1, 2])
    away_score_model = DummyPredictor([0, 1, 2])

    run_simulation(sign_model, home_score_model, away_score_model)