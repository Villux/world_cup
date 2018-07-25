import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse


def get_meta(bs):
    meta = bs.findAll("div", {"class": 'meta'})[0]
    text = re.sub(r'.*Age ', '', meta.get_text())
    text_list = text.split()
    return {
        'age': int(text_list[0]),
        'height': int(text_list[-2].strip('cm')),
        'weight': int(text_list[-1].strip('kg'))
    }

def get_high_level_info(bs):
    element = bs.findAll("div", {"class": 'stats'})[0]
    divs = element.findChildren(["div"])
    return {
        'overall_rating': int(divs[0].span.get_text()),
        'potential': int(divs[1].span.get_text()),
        'market_value': divs[2].span.get_text(),
        'wage': divs[3].span.get_text()
    }


def get_team_level_info(bs):
    element = bs.findAll("div", {"class": 'card pt-10 pb-10 pl-10 pr-10 mb-20'})[0]
    lis = element.div.div.ul.findChildren(["li"])
    for li in lis:
        li.label.extract()

    attributes = {
        'preferred_foot': lis[0].get_text().strip(),
        'international_reputation': int(lis[1].get_text().strip()),
        'weak_foot': lis[2].get_text().strip()
    }
    return attributes

def get_all_attributes(bs):
    attributes = {}

    attrs = bs.findChildren('li')
    for attr in attrs:
        spans = attr.findChildren('span')
        if len(spans) > 0:
            value = int(spans[0].get_text())
            for span in spans:
                span.extract()
            key = attr.get_text().strip().replace(" ", "_")
            attributes[key] = value

    return attributes


def get_column_level_data(bs):
    columns = bs.findAll("div", {"class": 'column col-4 mb-20'})
    attributes = {}
    for col in columns:
        col_attributes = get_all_attributes(col)
        attributes = {**attributes, **col_attributes}
    return attributes

def get_player_data(player_data):
    page = requests.get(f'https://sofifa.com{player_data["link"]}')
    bs = BeautifulSoup(page.text, 'html.parser')

    final = player_data
    final = {**final, **get_meta(bs)}
    final = {**final, **get_high_level_info(bs)}
    final = {**final, **get_team_level_info(bs)}
    final = {**final, **get_column_level_data(bs)}

    return final
