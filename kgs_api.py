import datetime
import json
import shutil
import urllib.request

import requests
import sgf
from bs4 import BeautifulSoup

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


def get_moves(game_record):
    moves = game_record.nodes[1:]
    moves_new = []
    for move in moves:
        d = {}
        if 'B' in move.properties:
            d['color'] = 'black'
            c = move.properties['B'][0]
            if c == '':
                d['coords'] = 'pass'
            else:
                d['coords'] = [ord(c[0]) - ord('a') + 1, ord(c[1]) - ord('a') + 1]
            d['time'] = ''
            if 'BL' in move.properties:
                time = round(float(move.properties['BL'][0]))
                d['time'] += f'{time // 60}:{time % 60}'
            if 'OB' in move.properties:
                time = int(move.properties['OB'][0])
                d['time'] += f'({time})'
        else:
            d['color'] = 'white'
            c = move.properties['W'][0]
            if c == '':
                d['coords'] = 'pass'
            else:
                d['coords'] = [ord(c[0]) - ord('a') + 1, ord(c[1]) - ord('a') + 1]
            d['time'] = ''
            if 'WL' in move.properties:
                time = round(float(move.properties['WL'][0]))
                d['time'] += f'{time // 60}:{time % 60}'
            if 'OW' in move.properties:
                time = int(move.properties['OW'][0])
                d['time'] += f' ({time})'
        moves_new.append(d)
    return moves_new


def get_game(player, game_id):
    game_list = get_game_list(player)
    game = game_list[-1 - game_id]
    year, month, day = map(int, game['timestamp'].split('T')[0].split('-'))
    white = game['players']['white']['name']
    black = game['players']['black']['name']

    date = datetime.date(year, month, day)
    game['date'] = date.strftime('%d %B %Y')

    game['players']['black']['avatar'] = f"https://goserver.gokgs.com/avatars/{game['players']['black']['name']}.jpg"
    game['players']['white']['avatar'] = f"https://goserver.gokgs.com/avatars/{game['players']['white']['name']}.jpg"

    sgf_url = f'https://files.gokgs.com/games/{year}/{month}/{day}/{white}-{black}'

    if 'revision' in game:
        sgf_url += f"-{str(int(game['revision']) + 1)}"

    sgf_url += '.sgf'

    with urllib.request.urlopen(sgf_url) as response, open('game.sgf', 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    with open('game.sgf') as f:
        collection = sgf.parse(f.read())

    game_record = collection[0]

    game['rules'] = game_record.nodes[0].properties['RU'][0]

    game['moves'] = get_moves(game_record)

    return game


def get_top_100_player():
    req = requests.get('https://gokgs.com/top100.jsp')
    soup = BeautifulSoup(req.text, 'lxml')
    tables = soup.find_all('table', attrs={'class': 'grid'})
    result = []
    for table in tables:
        for child in table.children:
            if child.text == 'PositionNameRank':
                continue
            c = list(child.children)
            player = {
                'position': c[0].text,
                'name': c[1].text,
                'rank': c[2].text,
                'urls': [f'/api/game?player={c[1].text}&game_id=0', f'/api/game?player={c[1].text}&game_id=1'],
            }
            result.append(player)
    return result
