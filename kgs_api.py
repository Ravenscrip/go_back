import datetime
import json
import shutil
import urllib.request

import requests
import sgf

KGS_URL = 'https://www.gokgs.com/json/access'


def login(session):
    data = {
        "type": "LOGIN",
        "name": "XxJadxX",
        "password": "bwwr2n",
        "locale": "en_US"
    }
    session.request('POST', KGS_URL, json=data)


def get_game_list(player):
    with requests.Session() as session:
        login(session)
        req = session.request('POST', KGS_URL, json={'type': 'JOIN_ARCHIVE_REQUEST', 'name': player})
        req2 = session.request('GET', KGS_URL)

    messages = json.JSONDecoder().decode(req2.text)['messages']

    games_list = list(filter(lambda x: x['type'] == 'ARCHIVE_JOIN', messages))[0]['games']

    return games_list


def get_game(player, game_id):
    game_list = get_game_list(player)
    game = game_list[game_id]
    year, month, day = map(int, game['timestamp'].split('T')[0].split('-'))
    white = game['players']['white']['name']
    black = game['players']['black']['name']

    date = datetime.date(year, month, day)
    game['date'] = date.strftime('%d %B %Y')

    game['players']['black']['avatar'] = f"https://goserver.gokgs.com/avatars/{game['players']['black']['name']}.jpg"
    game['players']['white']['avatar'] = f"https://goserver.gokgs.com/avatars/{game['players']['white']['name']}.jpg"

    sgf_url = f'https://files.gokgs.com/games/{year}/{month}/{day}/{white}-{black}'

    if 'revision' in game:
        sgf_url += f"-{game['revision']}"

    sgf_url += '.sgf'

    with urllib.request.urlopen(sgf_url) as response, open('game.sgf', 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    with open('larc-HiraBot44.sgf') as f:
        collection = sgf.parse(f.read())

    # game['sgf'] = collection

    return game
