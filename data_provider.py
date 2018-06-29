import numpy as np
import pandas as pd

def append_rank_data(df, ranking):
    dataset = pd.merge(df, ranking,  how='left', left_on=['date','home_team'], right_on = ['date','team'])
    dataset = dataset.drop(['team'], axis=1)
    dataset.rename(columns = {"elo": "home_elo"}, inplace=True)

    dataset = pd.merge(dataset, ranking,  how='left', left_on=['date','away_team'], right_on = ['date','team'])
    dataset = dataset.drop(['team'], axis=1)
    dataset.rename(columns = {"elo": "away_elo"}, inplace=True)
    return dataset

def append_player_data(df, player_stats):
    dataset_w = df.shape[1]
    dataset = pd.merge(df, player_stats,  how='left', left_on=['year','home_team'], right_on = ['year','nationality'])
    new_names = [(i, 'home_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['home_nationality'], axis=1)

    dataset_w = dataset.shape[1]
    dataset = pd.merge(dataset, player_stats,  how='left', left_on=['year','away_team'], right_on = ['year','nationality'])
    new_names = [(i, 'away_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['away_nationality'], axis=1)
    return dataset

def append_goal_history(df, goal_history):
    dataset = pd.merge(df, goal_history,  how='left', left_on=['date','home_team'], right_on = ['date','home_team'])
    dataset.rename(columns = {"home_team_x": "home_team", "away_team_x": "away_team"}, inplace=True)
    dataset = dataset.drop(['away_team_y'], axis=1)
    return dataset

def merge_all_data(match_results, elo_ranking, player_stats, goal_history):
    dataset = append_rank_data(match_results, elo_ranking)
    dataset = append_player_data(dataset, player_stats)
    dataset = append_goal_history(dataset, goal_history)
    return dataset

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

def get_data(filename, write_to_csv=False, save_filename="data/generated/master_data.csv"):
    match_results = pd.read_csv(filename)
    match_results['date'] =  pd.to_datetime(match_results['date'], format='%Y-%m-%d')
    match_results["year"] = match_results["date"].dt.year

    elo_ranking, player_stats, goal_history = load_feature_data()

    master_data = merge_all_data(match_results, elo_ranking, player_stats, goal_history)
    if write_to_csv:
        master_data.to_csv(save_filename, index=False)
    return master_data
