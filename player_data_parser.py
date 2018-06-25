import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse


def get_meta(bs):
    meta = bs.findAll("div", {"class": 'meta'})[0]
    text = meta.span.get_text()
    text_list = text.split()[-6:] # Take only age, height and weight

    return {
        'age': int(text_list[0]),
        'height': int(text_list[-2].strip('cm')),
        'weight': int(text_list[-1].strip('kg'))
    }

def get_high_level_info(bs):
    element = bs.findAll("div", {"class": 'stats'})[0]
    tds = element.findChildren(["td"])

    return {
        'overall_rating': int(tds[0].span.get_text()),
        'potential': int(tds[1].span.get_text()),
        'market_value': tds[2].span.get_text(),
        'wage': tds[3].span.get_text()
    }


def get_team_level_info(bs):
    element = bs.findAll("div", {"class": 'teams'})[0]
    tds = element.findChildren(["td"])
    lis = tds[0].findChildren('li')
    for li in lis:
        li.label.extract()

    attributes = {
        'preferred_foot': lis[0].get_text().strip(),
        'international_reputation': int(lis[1].get_text().strip()),
        'weak_foot': lis[2].get_text().strip(),
        'national_team_rating': None,
        'national_team_position': None
    }

    if len(tds) > 3:
        lis = tds[3].findChildren('li')
        if len(lis) > 2:
            attributes["national_team_rating"] = int(lis[1].span.get_text())
            attributes["national_team_position"] = lis[2].span.get_text()

    return attributes

def get_all_attributes(bs):
    attributes = {}

    attrs = bs.findChildren('li')
    for attr in attrs:
        if attr.span:
            value = int(attr.span.extract().get_text())
            key = attr.get_text().strip().replace(" ", "_")
            attributes[key] = value

    return attributes


def get_column_level_data(bs):
    article = bs.findAll("article", {"class": 'column'})[0]
    rows = article.findAll("div", {"class": 'columns'})

    attributes = {}
    for row in rows:
        cols = row.findAll("div", {"class": 'column'})
        for col in cols:
            col_attributes = get_all_attributes(col)
            attributes = {**attributes, **col_attributes}

    return attributes


def get_player_data(player_data):
    page = requests.get(f'https://sofifa.com/{player_data["link"]}')
    bs = BeautifulSoup(page.text, 'html.parser')

    final = player_data
    final = {**final, **get_meta(bs)}
    final = {**final, **get_high_level_info(bs)}
    final = {**final, **get_team_level_info(bs)}
    final = {**final, **get_column_level_data(bs)}

    return final
