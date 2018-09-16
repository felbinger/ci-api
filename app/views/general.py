import requests
from flask import Blueprint, redirect, render_template, request, flash, url_for, session

from .utils import require_login, require_logout

general = Blueprint(__name__, 'general')


@general.route('/', methods=['GET'])
@require_login
def index():
    header = {'Access-Token': session.get('Access-Token')}
    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return render_template('index.html', user=user), 200


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


@general.route('/register', methods=['GET', 'POST'])
@require_logout
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if username and email and password:
            if len(password) < 8:
                flash('Password too short (>= 8 character)', 'danger')
            else:
                resp = requests.post(
                    f'{request.scheme}://{request.host}{url_for("user_api")}',
                    json={
                        'username': username,
                        'email': email,
                        'password': password
                    }
                )
                if resp.status_code == 201:
                    # Login
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
                    flash(f'Unknown error: {resp.json().get("message")}', 'danger')
        else:
            flash('Missing data', 'danger')

    if request.method == 'GET':
        if request.args.get('username') or request.args.get('email') or request.args.get('password'):
            flash('Missing data', 'danger')
            if request.args.get('username') and request.args.get('email') and request.args.get('password'):
                flash('Internal Error', 'danger')

    # The template contains one form which should have the attribute method="POST".
    # The user should recognize this error and correct it itself to create the account.
    return render_template('register.html'), 200


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
                        flash('Password is too short. Please use a password which is >= 8 characters!', 'danger')
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

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return render_template('account.html', user=user)


@general.route('/message', methods=['POST'])
@require_login
def message():
    header = {'Access-Token': session.get('Access-Token')}
    if request.form is not None:
        subject = request.form.get('subject')
        message = request.form.get('message')
        if subject and message:
            resp = requests.post(
                f'{request.scheme}://{request.host}{url_for("message_api")}',
                json={
                    'subject': subject,
                    'message': message
                },
                headers=header
            )
            if resp.status_code != 201:
                flash(f'Unknown error: {resp.json().get("message")}', 'danger')
            else:
                flash('Message has been created!', 'success')

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')

    return redirect(url_for('app.views.general.index'), code=302)
