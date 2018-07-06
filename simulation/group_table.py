import functools
import random
import numpy as np
import pandas as pd

class GroupTable():
    def __init__(self, match_df):
        self.table = self.build_group_table(match_df)

    def build_group_table(self, match_df):
        data = []
        for key, value in match_df.groupby('group')['home_team'].unique().to_dict().items():
            for team in value:
                data.append({"Team": team, "Group": key, "points": 0, 'goal_diff': 0, 'goals_scored': 0})

        return pd.DataFrame(data)

    def print_group_standings(self):
        self.sort()
        columns = ['Position', 'Group A', 'Points A', 'Group B', 'Points B', 'Group C', 'Points C',
                'Group D', 'Points D', 'Group E', 'Points E', 'Group F', 'Points F',
                'Group G', 'Points G', 'Group H', 'Points H']

        data = {"Position": [1,2,3,4]}
        df = pd.DataFrame(data, columns = columns)

        for idx, group in enumerate(["A", "B", "C", "D", "E", "F", "G", "H"]):
            group_df = self.table[self.table["Group"] == group]
            group_df = group_df.reset_index()
            group_df = group_df.drop(['index', 'Group'], axis=1)
            df.iloc[:, 1 + (idx * 2)] = group_df["Team"]
            df.iloc[:, 2 + (idx * 2)] = group_df["points"]

        print("\n\n", df)

    def sort(self):
        sorted_table = pd.DataFrame()
        for group in np.unique(self.table["Group"]):
            group_df = self.table[self.table["Group"] == group]
            teams = [group_df.iloc[0], group_df.iloc[1], group_df.iloc[2], group_df.iloc[3]]
            shorted_standing = sorted(teams, key=functools.cmp_to_key(self.get_better_team))
            tmp = pd.concat([row.to_frame().T for row in shorted_standing])
            sorted_table = pd.concat([sorted_table, tmp])
        self.table = sorted_table

    def update_table(self, home_team, away_team, match_outcome):
        if match_outcome == 1:
            self.table.loc[self.table["Team"] == home_team, "points"] += 3
        elif match_outcome == 0:
            self.table.loc[self.table["Team"] == home_team, "points"] += 1
            self.table.loc[self.table["Team"] == away_team, "points"] += 1
        elif match_outcome == -1:
            self.table.loc[self.table["Team"] == away_team, "points"] += 3

        self.store_mutual_match(home_team, away_team, match_outcome)
        self.sort()

    def get_team(self, group, position):
        return self.table[self.table["Group"] == group].iloc[position]["Team"]

    def store_mutual_match(self, home_team, away_team, match_outcome):
        self.table[f"{home_team}-{away_team}"] = match_outcome
        self.table[f"{away_team}-{home_team}"] = -match_outcome if match_outcome != 0 else match_outcome

    def get_better_team(self, first_team, second_team):
        if first_team["points"] > second_team["points"]:
            return -1
        elif first_team["points"] < second_team["points"]:
            return 1

        if first_team["goal_diff"] > second_team["goal_diff"]:
            return -1
        elif first_team["goal_diff"] < second_team["goal_diff"]:
            return 1

        if first_team["goals_scored"] > second_team["goals_scored"]:
            return -1
        elif first_team["goals_scored"] < second_team["goals_scored"]:
            return 1

        f_name = first_team["Team"]
        s_name = second_team["Team"]

        if first_team.get(f"{f_name}-{s_name}", 0) > 0:
            return -1
        elif first_team.get(f"{f_name}-{s_name}", 0) < 0:
            return 1
        else:
            return - 1 if random.random() > 0.5 else -1