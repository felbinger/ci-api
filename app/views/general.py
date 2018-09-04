import requests
from flask import Blueprint, redirect, render_template, request, flash, url_for, session
from .utils import require_login, require_logout

general = Blueprint(__name__, 'general')


@general.route('/', methods=['GET'])
@require_login
def index():
    header = {'Access-Token': session.get('Access-Token')}

    categories = requests.get(
        f'{request.scheme}://{request.host}{url_for("category_api")}',
        headers=header
    ).json().get('data')

    challenges = requests.get(
        f'{request.scheme}://{request.host}{url_for("challenge_api")}',
        headers=header
    ).json().get('data')

    solves = list()
    solved = requests.get(
        f'{request.scheme}://{request.host}{url_for("solve_api")}',
        headers=header
    ).json().get('data') or []
    if solved:
        for solve in solved:
            # append the challenge id the the solves list
            solves.append(solve.get('challenge').get('id'))

    data = list()
    for category in categories:
        solved_count = 0
        challenge_count = 0
        if category.get('name') != 'Special':
            for challenge in solved:
                if category["name"] == challenge['challenge']["category"]["name"]:
                    solved_count += 1

            for challenge in challenges:
                if category["name"] == challenge["category"]["name"]:
                    challenge_count += 1
            if category.get('name') == 'HC':
                url = url_for('app.views.challenges.hacking')
            elif category.get('name') == 'CC':
                url = url_for('app.views.challenges.hacking')
            data.append({
                'description': category.get('description'),
                'unsolved': challenge_count - solved_count,
                'url': url
            })

    return render_template('index.html', data=data), 200


@general.route('/rules', methods=['GET'])
@require_login
def rules():
    return render_template('rules.html'), 200


@general.route('/login', methods=['GET', 'POST'])
@require_logout
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            token = requests.post(
                f'{request.scheme}://{request.host}{url_for("auth_api")}',
                json={
                    'username': username,
                    'password': password
                }
            ).json().get('token')
            if token:
                print(f'User {username} logged in with token: {token}')
                session['Access-Token'] = token
                return redirect(url_for('app.views.general.index'))
            else:
                flash('Credentials incorrect')
        else:
            flash('Missing credentials')
    return render_template('login.html')


@general.route('/logout', methods=['GET'])
@require_login
def logout():
    resp = requests.delete(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers={'Access-Token': session.get('Access-Token')},
    )
    if resp.status_code != 204:
        print(f"Unable to delete token ({session.get('Access-Token')}) from database!")
    session['Access-Token'] = None
    return redirect(url_for('app.views.general.login'), code=302)


@general.route('/account', methods=['GET', 'POST'])
@require_login
def account():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')
            if action == 'changePassword':
                if request.form.get('password1') == request.form.get('password2'):
                    if len(request.form.get('password1')) >= 8:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("user_api")}/me',
                            headers=header,
                            json={
                                'password': request.form.get('password1')
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update password: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Password has been updated!', 'success')
                    else:
                        flash('Password is too short. Please use a password which is >= 8 characters!')
                else:
                    flash('The entered Password\'s are not the same!', 'danger')

            elif action == 'update':

                resp = requests.put(
                    f'{request.scheme}://{request.host}{url_for("user_api")}/me',
                    headers=header,
                    json={
                        'username': request.form.get('username'),
                        'email': request.form.get('email')
                    }
                )
                if resp.status_code != 200:
                    flash(f'Unable to update your account: {resp.json().get("message")}', 'danger')
                else:
                    flash('Your account has been updated!', 'success')
    data = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    data['solved_challenges'] = list()

    solved = requests.get(
        f'{request.scheme}://{request.host}{url_for("solve_api")}',
        headers=header
    ).json().get('data')
    for solve in solved:
        category = solve.get('challenge').get('category').get('name')
        if category == 'HC':
            category = 'Hacking Challenge'
        elif category == 'CC':
            category = 'Coding Challenge'
        else:
            category = 'Special Challenge'

        data['solved_challenges'].append({
            'type': category,
            'name': solve.get('challenge').get('name'),
            'time': solve.get('timestamp')
        })

    return render_template('account.html', data=data)
