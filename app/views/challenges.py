import requests
from flask import Blueprint, redirect, render_template, request, flash, url_for, session

from .utils import require_login

challenges = Blueprint(__name__, 'challenges')


@challenges.route('/', methods=['GET'])
@require_login
def index():
    return redirect(url_for('app.views.challenges.coding'), code=302)


@challenges.route('/coding', methods=['GET', 'POST'])
@require_login
def coding():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')
            if action == 'submitFlag':
                resp = requests.put(
                    f'{request.scheme}://{request.host}{url_for("solve_api")}/{request.form.get("id")}',
                    headers=header,
                    json={'flag': request.form.get('flag')}
                )
                if resp.status_code != 201:
                    flash(f'Unable to solve challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Good Job, you\'ve solved another challenge!', 'success')

            elif action == 'rateUp':
                # TODO change url_for('rating_api')
                resp = requests.put(
                    f'{request.scheme}://{request.host}/api/rate/{request.form.get("id")}',
                    headers=header,
                    json={'thumbUp': True}
                )
                if resp.status_code != 201:
                    flash(f'Unable to rate challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Thanks for rating!', 'success')

            elif action == 'rateDown':
                # TODO change url_for('rating_api')
                resp = requests.put(
                    f'{request.scheme}://{request.host}/api/rate/{request.form.get("id")}',
                    headers=header,
                    json={'thumbUp': False}
                )
                if resp.status_code != 201:
                    flash(f'Unable to rate challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Thanks for rating!', 'success')

    data = dict()
    data['challenges'] = list()
    challs = requests.get(
        f'{request.scheme}://{request.host}{url_for("challenge_api")}',
        headers=header
    ).json().get('data')

    # append the id's of the solved challenges to an list
    solved = requests.get(f'{request.scheme}://{request.host}{url_for("solve_api")}', headers=header).json().get('data')
    solves = [s.get('challenge').get('id') for s in solved.get('challenges')]
    if challs:
        for challenge in challs:
            if challenge.get('category').get('name') == 'CC':
                challenge['solved'] = True if challenge.get('id') in solves else False
                data['challenges'].append(challenge)

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return render_template('cc.html', user=user, data=data)


@challenges.route('/hacking', methods=['GET', 'POST'])
@require_login
def hacking():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')
            if action == 'submitFlag':
                resp = requests.put(
                    f'{request.scheme}://{request.host}{url_for("solve_api")}/{request.form.get("id")}',
                    headers=header,
                    json={'flag': request.form.get('flag')}
                )
                if resp.status_code != 201:
                    flash(f'Unable to solve challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Good Job, you\'ve solved another challenge!', 'success')

            elif action == 'rateUp':
                # TODO change url_for('rating_api')
                resp = requests.put(
                    f'{request.scheme}://{request.host}/api/rate/{request.form.get("id")}',
                    headers=header,
                    json={'thumbUp': True}
                )
                if resp.status_code != 201:
                    flash(f'Unable to rate challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Thanks for rating!', 'success')

            elif action == 'rateDown':
                # TODO change url_for('rating_api')
                resp = requests.put(
                    f'{request.scheme}://{request.host}/api/rate/{request.form.get("id")}',
                    headers=header,
                    json={'thumbUp': False}
                )
                if resp.status_code != 201:
                    flash(f'Unable to rate challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Thanks for rating!', 'success')

    data = dict()
    data['challenges'] = list()
    challs = requests.get(
        f'{request.scheme}://{request.host}{url_for("challenge_api")}',
        headers=header
    ).json().get('data')

    # append the id's of the solved challenges to an list
    solved = requests.get(f'{request.scheme}://{request.host}{url_for("solve_api")}', headers=header).json().get('data')
    solves = [s.get('challenge').get('id') for s in solved.get('challenges')]

    # append all hacking challenges to the data list
    if challs:
        for challenge in challs:
            if challenge.get('category').get('name') == 'HC':
                # check if the challenge id is in the solves list
                challenge['solved'] = True if challenge.get('id') in solves else False
                data['challenges'].append(challenge)

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return render_template('hc.html', user=user, data=data)


@challenges.route('/special', methods=['GET', 'POST'])
@require_login
def special():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')
            if action == 'submitFlag':
                resp = requests.post(
                    f'{request.scheme}://{request.host}{url_for("solve_api")}',
                    headers=header,
                    json={'flag': request.form.get('flag')}
                )
                if resp.status_code != 201:
                    flash(f'Unable to solve challenge: {resp.json().get("message")}', 'danger')
                else:
                    flash('Good Job', 'success')
    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return render_template('special.html', user=user)
