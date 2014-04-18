"""Tic Tac Toe game.

Uses a global dict to store the state of all current games, and stores each
board as a 3x3 list of 'X' and 'O' values.
"""
import os

from flask import Flask, redirect, url_for, request, render_template, abort, \
    session


app = Flask(__name__)
app.secret_key = os.urandom(24)
games = {}


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game', methods=['POST'])
def game():
    name = request.form.get('name')
    game_name = request.form.get('game')
    session['name'] = name

    if game_name not in games:
        # Create a new game if none exists
        games[game_name] = {
            'X': name,
            'O': None,
            'board': [
                [None, None, None],
                [None, None, None],
                [None, None, None]
            ],
            'turn': name,
            'winner': None
        }
        return redirect(url_for('get_game', game_name=game_name))

    elif games[game_name]['O'] is None:
        # Create a player 2 if none exists
        games[game_name]['O'] = name
        return redirect(url_for('get_game', game_name=game_name))

    elif name in (games[game_name]['X'], games[game_name]['O']):
        return redirect(url_for('get_game', game_name=game_name))

    else:
        return '<h1>Game full!</h1>'


@app.route('/games/<game_name>', methods=['GET', 'POST'])
def get_game(game_name):
    if games.get(game_name) is None:
        return abort(404)

    if request.method == 'POST':
        name = session.get('name')
        if name is None:
            return redirect(url_for('home'))

        current_game = games[game_name]
        if current_game['winner'] is not None:
            return 'Game over, %s won' % current_game['winner']

        position = request.form.get('position')
        x, y = [int(point) for point in position.split(',')]
        if current_game['board'][x][y] is None:
            if current_game['turn'] == name:
                move = find_key_for_value(current_game, name)
                current_game['board'][x][y] = move

                if detect_win(current_game['board']):
                    current_game['winner'] = current_game['turn']
                    return 'You won!'

                if move == 'X':
                    current_game['turn'] = current_game['O']

                else:
                    current_game['turn'] = current_game['X']

            else:
                return 'It isn\'t your turn'

        else:
            return 'Invalid move'

    return render_template(
        'index.html', game_name=game_name, **games[game_name])


# Helper functions
def find_key_for_value(dictionary, value):
    for k, v in dictionary.iteritems():
        if v == value:
            return k


def detect_win(board):
    # Check rows and columns
    for i in xrange(0, 3):
        if (board[i][0] == board[i][1] == board[i][2] is not None
                or board[0][i] == board[1][i] == board[2][i] is not None):
            return True

    # Check diagonals
    if (board[0][0] == board[1][1] == board[2][2] is not None
            or board[0][2] == board[1][1] == board[2][0] is not None):
        return True

    return False

if __name__ == '__main__':
    DEBUG = 'HEROKU' not in os.environ
    app.run(debug=DEBUG, port=int(os.environ.get('PORT', 5000)))
