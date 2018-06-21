import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--year', type=str, default='17', help="Which year's FIFA")
args = parser.parse_args()

players = []

offset = 0
page = requests.get(f'https://sofifa.com/players?v={args.year}&offset={offset}')

first_player_id = None
print(f"Starting to scrape data for year {args.year}")

not_all_done = True
while not_all_done:
    bs = BeautifulSoup(page.text, 'html.parser')

    player_table  = bs.findAll('table', {'class': 'table table-hover persist-area'})[0]

    rows = player_table.findChildren(['tr'])
    for row in rows[2:]:
        try:
            id_col = row.findChildren(["td"])[0]
            player_col = row.findChildren(["td"])[1]
            a_cols = player_col.div.findChildren("a")
            nationality_col = a_cols[0]
            name_col = a_cols[1]
            play_pos = a_cols[2]
        except Exception as e:
            print("Failed to get data")
            print(e)
        else:
            player_id = int(id_col.img["id"])
            player_nationality = player_col.div.a["title"]
            player_name = name_col["title"]
            player_play_pos = play_pos.get_text()

            if first_player_id is None:
                first_player_id = player_id
            else:
                if first_player_id == player_id:
                    not_all_done = False
                    break
                else:
                    players.append([player_id, player_name, player_nationality, player_play_pos])

    if not_all_done:
        offset += 80
        print(f"Next Offset: {offset}")
        page = requests.get(f'https://sofifa.com/players?v={args.year}&offset={offset}')

df_cols = ["player_fifa_api_id", "name", "nationality", "position"]

player_df = pd.DataFrame(players,  columns=df_cols)
player_df.to_csv(f"SOFIFA{args.year}.csv")
