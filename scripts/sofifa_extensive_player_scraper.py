import argparse
from datetime import datetime
from urllib import parse
from multiprocessing import Pool, cpu_count
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

from player_data_parser import get_player_data

def get_url(query_string, offset):
    return f'https://sofifa.com/players?{query_string}&offset={offset}'

fname = "scraped_datapoints.txt"
try:
    with open(fname) as file:
        read_queries = [line.rstrip('\n') for line in file]
except:
    read_queries = []

url = f'https://sofifa.com/players?'
page = requests.get(url)
bs = BeautifulSoup(page.text, 'html.parser')
datapoint_rows = bs.findAll('div', {'class': 'filter-body'})[0]

dates = {}
for drow in datapoint_rows.findAll('div', {'class': 'column col-4'})[4:]:
    month = drow.div.div.div.get_text()
    for child in drow.findAll('div', {'class': 'card-body'})[0].findChildren(["a"]):
        query_string = parse.urlparse(child["href"]).query
        day = child.get_text()
        date = datetime.strptime(f"{month} {day}", '%b %Y %d')
        date_string = date.strftime("%Y-%m-%d")
        dates[date_string] = query_string

bs.decompose()

for data_date, query_string in dates.items():
    if query_string in read_queries:
        continue

    with open(fname, "a") as myfile:
        myfile.write(f"{query_string}\n")

    players = []

    offset = 0
    url = get_url(query_string, offset)
    page = requests.get(url)

    first_player_id = None
    print(f"Starting to scrape data for {query_string}")

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
                'link': a_cols[1]["href"] + f'?{query_string}'
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

        bs.decompose()

        if not_all_done:
            offset += 80
            print(f"Next Offset: {offset}")
            url = get_url(query_string, offset)
            page = requests.get(url)


    player_df = pd.DataFrame(players)
    player_df.to_csv(f"data/generated/player_data/SOFIFA_ext_{data_date}.csv")
    break
