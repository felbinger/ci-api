import requests
from flask import Blueprint, render_template, request, url_for, session

from .utils import require_login

leaderboard = Blueprint(__name__, 'leaderboard')


@leaderboard.route('/leaderboard', methods=['GET'])
@require_login
def index():
    header = {'Access-Token': session.get('Access-Token')}
    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    leaderboard = requests.get(
        f'{request.scheme}://{request.host}{url_for("leaderboard_api")}',
        headers=header
    ).json().get('data')
    rank = requests.get(
        f'{request.scheme}://{request.host}{url_for("leaderboard_api")}/me',
        headers=header
    ).json().get('data')

    return render_template('leaderboard.html', user=user, rank=rank, leaderboard=leaderboard)
