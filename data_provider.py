import numpy as np
import pandas as pd

from db_interface import get_connection

def append_player_data(df):
    query = ''' SELECT * from player_attribute;'''
    with get_connection() as conn:
        df_player_attribute = pd.read_sql(query, conn)
    df_player_attribute = df_player_attribute.drop(['id'], axis=1)

    dataset_w = df.shape[1]
    dataset = pd.merge(df, df_player_attribute,  how='left', left_on=['year','home_team'], right_on = ['year','nationality'])
    new_names = [(i, 'home_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['home_nationality'], axis=1)

    dataset_w = dataset.shape[1]
    dataset = pd.merge(dataset, df_player_attribute,  how='left', left_on=['year','away_team'], right_on = ['year','nationality'])
    new_names = [(i, 'away_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['away_nationality'], axis=1)
    return dataset

def merge_all_data():
    query = ''' SELECT
                    m.*,
                    home_e.elo as "home_elo",
                    away_e.elo as "away_elo",
                    goal.goal_diff_with_away as "goal_diff_with_away",
                    goal.home_goals_with_away as "home_goals_with_away",
                    goal.away_goals_with_home as "away_goals_with_home",
                    goal.home_goal_mean as "home_goal_mean",
                    goal.away_goal_mean as "away_goal_mean"
                FROM match AS m
                LEFT JOIN elo_rating AS home_e
                    ON home_e.match_id=m.id AND home_e.team=m.home_team
                LEFT JOIN elo_rating AS away_e
                    ON away_e.match_id=m.id AND away_e.team=m.away_team
                LEFT JOIN goal_feature AS goal
                    ON goal.match_id=m.id
                ORDER BY date;'''
    with get_connection() as conn:
        df_match = pd.read_sql(query, conn)

    return append_player_data(df_match)

def load_feature_data():
    elo_ranking = pd.read_csv('data/generated/elo_ranking.csv', )
    elo_ranking['date'] =  pd.to_datetime(elo_ranking['date'], format='%Y-%m-%d')
    elo_ranking = elo_ranking.drop(['Unnamed: 0'], axis=1)

    player_stats = pd.read_csv('data/generated/team_level_player_data.csv')
    player_stats = player_stats.drop(['Unnamed: 0'], axis=1)

    goal_history = pd.read_csv('data/generated/goal_history_data.csv')
    goal_history['date'] =  pd.to_datetime(goal_history['date'], format='%Y-%m-%d')
    goal_history = goal_history.drop(['Unnamed: 0'], axis=1)

    return elo_ranking, player_stats, goal_history

def get_data(write_to_csv=False, save_filename="data/generated/master_data.csv"):
    master_data = merge_all_data()
    if write_to_csv:
        master_data.to_csv(save_filename, index=False)
    return master_data

def get_latest_elo(team):
    elo_ranking = pd.read_csv('data/generated/elo_ranking.csv', )
    elo_ranking['date'] =  pd.to_datetime(elo_ranking['date'], format='%Y-%m-%d')
    elo_ranking = elo_ranking.drop(['Unnamed: 0'], axis=1)

    elo_ranking = elo_ranking.sort_values(by='date')
    return elo_ranking[elo_ranking["team"] == team]["elo"].tail(1).item()

if __name__ == "__main__":
    merge_all_data()
