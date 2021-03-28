import locale

import flask
from flask import make_response, jsonify, request
from werkzeug.exceptions import abort

import kgs_api

app = flask.Flask(__name__)
app.secret_key = b'I4=\xde\x00;\x06\xea3\xe4\xa2\xe0\x14\x8b\xabH'


@app.route('/api', methods=['GET'])
def index():
    return jsonify({})


@app.route('/api/game', methods=['GET'])
def get_game():
    player = request.args.get('player', default=None, type=str)
    game_id = request.args.get('game_id', default=-1, type=int)
    if player is None or game_id not in [0, 1]:
        abort(404)

    game = kgs_api.get_game(player, game_id)

    return jsonify(game)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app.run('localhost', 8080, debug=True)
