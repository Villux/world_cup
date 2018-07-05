import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse
from multiprocessing import Pool, cpu_count


from player_data_parser import get_player_data

parser = argparse.ArgumentParser()
parser.add_argument('--year', type=str, default='17', help="Which year's FIFA")
args = parser.parse_args()

players = []

offset = 0
url = f'https://sofifa.com/players?v={args.year}&offset={offset}'
page = requests.get(url)

first_player_id = None
print(f"Starting to scrape data for year {args.year}")

pool = Pool(cpu_count())

not_all_done = True
while not_all_done:
    if 'offset' not in page.url:
        not_all_done = False
        break
    bs = BeautifulSoup(page.text, 'html.parser')

    player_table  = bs.findAll('table', {'class': 'table table-hover persist-area'})[0]

    rows = player_table.findChildren(['tr'])
    list_of_players = []
    for row in rows[2:]:
        id_col = row.findChildren(["td"])[0]
        player_id = int(id_col.img["id"])

        player_col = row.findChildren(["td"])[1]
        a_cols = player_col.div.findChildren("a")

        player_data = {
            'fifa_id': player_id,
            'nationality': player_col.div.a["title"],
            'name': a_cols[1]["title"],
            'play_pos': ','.join([a.get_text() for a in a_cols[2:]]),
            'link': a_cols[1]["href"] + f'?v={args.year}'
        }

        if first_player_id is None:
                first_player_id = player_id
        else:
            if first_player_id == player_id:
                not_all_done = False
                break
            else:
                list_of_players.append(player_data)

    data = pool.map(get_player_data, list_of_players)
    players.extend(data)

    if not_all_done:
        offset += 80
        print(f"Next Offset: {offset}")
        page = requests.get(f'https://sofifa.com/players?v={args.year}&offset={offset}')

player_df = pd.DataFrame(players)
player_df.to_csv(f"SOFIFA_ext_{args.year}.csv")
