import requests
from flask import Blueprint, redirect, render_template, request, flash, url_for, session

from .utils import require_login, require_admin

admin = Blueprint(__name__, 'admin')


@admin.route('/', methods=['GET'])
@require_login
@require_admin
def index():
    return redirect(url_for('app.views.admin.dashboard'), code=302)


@admin.route('/challenges', methods=['GET', 'POST'])
@require_login
@require_admin
def challenges():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')

            if action == 'createCategory':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name or not description:
                    flash('Unable to create Category: Name and description cannot be emtpy!', 'danger')
                else:
                    resp = requests.post(
                        f'{request.scheme}://{request.host}{url_for("category_api")}',
                        headers=header,
                        json={
                            'name': name,
                            'description': description
                        }
                    )
                    if resp.status_code != 201:
                        flash(f'Unable to create category: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Category has been created successfully!', 'success')

            elif action == 'updateCategory':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name:
                    flash('Unable to update Category: Name cannot be emtpy!', 'danger')
                else:
                    if not description:
                        flash('Unable to update Category: Description cannot be emtpy!', 'danger')
                    else:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("category_api")}/{name}',
                            headers=header,
                            json={
                                'description': description
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update category: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Category has been created successfully!', 'success')

            elif action == 'deleteCategory':
                name = request.form.get('name')
                if name:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("category_api")}/{name}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete category: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Category has been deleted!', 'success')
                else:
                    flash('You need to provide an name to delete a category!', 'danger')

            elif action == 'createChallenge':
                name = request.form.get('name')
                description = request.form.get('description')
                flag = request.form.get('flag')
                category_name = request.form.get('category')
                yt_challenge_id = request.form.get('ytChallengeId')
                yt_solution_id = request.form.get('ytSolutionId')
                urls = request.form.getlist('urls[]')
                url_descriptions = request.form.getlist("urlDescriptions[]")
                if not name:
                    flash('Unable to create challenge: Name cannot be emtpy!', 'danger')
                else:
                    if not flag:
                        flash('Unable to create challenge: Flag cannot be emtpy!', 'danger')
                    else:
                        if not category_name:
                            flash('Unable to create challenge: Category cannot be emtpy!', 'danger')
                        else:
                            resp = requests.post(
                                f'{request.scheme}://{request.host}{url_for("challenge_api")}',
                                headers=header,
                                json={
                                    'name': name,
                                    'description': description,
                                    'flag': flag,
                                    'category': category_name,
                                    'ytChallengeId': yt_challenge_id,
                                    'ytSolutionId': yt_solution_id
                                }
                            )
                            if resp.status_code != 201:
                                flash(f'Unable to create challenge: {resp.json().get("message")}', 'danger')
                            else:
                                challenge_id = resp.json().get('data').get('id')
                                if urls and url_descriptions:
                                    for url, description in zip(urls, url_descriptions):
                                        if url and description:
                                            resp = requests.post(
                                                f'{request.scheme}://{request.host}{url_for("url_api")}',
                                                headers=header,
                                                json={
                                                    'url': url,
                                                    'description': description,
                                                    'challenge': challenge_id
                                                }
                                            )
                                            if resp.status_code != 201:
                                                msg = resp.json().get("message")
                                                flash(f'Unable to create url {url}: {msg}', 'danger')

                                else:
                                    flash('Challenge has been created successfully!', 'success')

            elif action == 'updateChallenge':
                _id = request.form.get('id')
                description = request.form.get('description')
                yt_challenge_id = request.form.get('ytChallengeId')
                yt_solution_id = request.form.get('ytSolutionId')
                url_ids = request.form.getlist('urlIds[]')
                urls = request.form.getlist('urls[]')
                url_descriptions = request.form.getlist("urlDescriptions[]")
                if not _id:
                    flash('Unable to update challenge: ID cannot be emtpy!', 'danger')
                else:
                    resp = requests.put(
                        f'{request.scheme}://{request.host}{url_for("challenge_api")}/{_id}',
                        headers=header,
                        json={
                            'description': description,
                            'ytChallengeId': yt_challenge_id,
                            'ytSolutionId': yt_solution_id
                        }
                    )
                    if resp.status_code != 200:
                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Challenge has been created successfully!', 'success')
                        all_urls = resp.json().get('data').get('urls')
                        if url_ids and urls and url_descriptions:
                            for _id, url, description in zip(url_ids, urls, url_descriptions):
                                # if url and description contain something useful update the url
                                if url and description:
                                    resp = requests.put(
                                        f'{request.scheme}://{request.host}{url_for("url_api")}/{_id}',
                                        headers=header,
                                        json={
                                            'url': url,
                                            'description': description
                                        }
                                    )
                                    if resp.status_code != 200:
                                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')
                                else:
                                    # if url and description fields are emtpy
                                    resp = requests.delete(
                                        f'{request.scheme}://{request.host}{url_for("url_api")}/{_id}',
                                        headers=header
                                    )
                                    if resp.status_code != 204:
                                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')

                            # iterate over all urls for the challenge
                            for obj in all_urls:
                                # if the id from the currently saved url object is not in the request delete it
                                if str(obj.get('id')) not in url_ids:
                                    resp = requests.delete(
                                       f'{request.scheme}://{request.host}{url_for("url_api")}/{obj.get("id")}',
                                       headers=header
                                    )
                                    if resp.status_code != 204:
                                        msg = resp.json().get("message")
                                        flash(f'Unable to update challenge (url): {msg}', 'danger')
                        else:
                            # if urls and url_descriptions are completely emtpy delete all urls
                            for obj in all_urls:
                                resp = requests.delete(
                                    f'{request.scheme}://{request.host}{url_for("url_api")}/{obj.get("id")}',
                                    headers=header
                                )
                                if resp.status_code != 204:
                                    msg = resp.json().get("message")
                                    flash(f'Unable to update challenge (url): {msg}', 'danger')

    data = dict()

    data['challenges'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("challenge_api")}',
        headers=header
    ).json().get('data')

    data['categories'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("category_api")}',
        headers=header
    ).json().get('data')

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    return render_template('challenge-dashboard.html', user=user, data=data)


@admin.route('/messages', methods=['GET', 'POST'])
@require_login
@require_admin
def messages():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')

            if action == 'deleteMessage':
                _id = request.form.get('id')
                if _id:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("message_api")}/{_id}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete message: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Message has been deleted!', 'success')
                else:
                    flash('You need to provide an id to delete a message!', 'danger')

    data = dict()
    data['messages'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("message_api")}',
        headers=header
    ).json().get('data')

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    return render_template('message-dashboard.html', user=user, data=data)


@admin.route('/accounts', methods=['GET', 'POST'])
@require_login
@require_admin
def accounts():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')

            if action == 'createAccount':

                username = request.form.get('username')
                password = request.form.get('password')
                email = request.form.get('email')
                role = request.form.get('role')

                if not username:
                    flash('Unable to create account: Username cannot be emtpy!', 'danger')
                else:
                    if not password:
                        flash('Unable to create account: Password cannot be emtpy!', 'danger')
                    else:
                        if len(password) < 8:
                            flash('Password is too short!', 'danger')
                        else:
                            if not email:
                                flash('Unable to create account: E-Mail cannot be emtpy!', 'danger')
                            else:
                                if not role:
                                    flash('Unable to create account: Role cannot be emtpy!', 'danger')
                                else:
                                    resp = requests.post(
                                        f'{request.scheme}://{request.host}{url_for("user_api")}',
                                        headers=header,
                                        json={
                                            'username': username,
                                            'password': password,
                                            'email': email,
                                            'role': role
                                        }
                                    )
                                    if resp.status_code != 201:
                                        msg = resp.json().get("message")
                                        flash(f'Unable to create account: {msg}', 'danger')
                                    else:
                                        flash('Account has been created successfully!', 'success')

            elif action == 'updateAccount':
                public_id = request.form.get('id')
                if public_id:
                    resp = requests.put(
                        f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
                        json={
                            'username': request.form.get('username'),
                            'email': request.form.get('email'),
                            'role': request.form.get('role')
                        },
                        headers=header
                    )
                    if resp.status_code != 200:
                        flash(f'Unable to update account: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Account has been update!', 'success')
                else:
                    flash('You need to provide an uuid to update an account!', 'danger')

            elif action == 'deleteAccount':
                public_id = request.form.get('id')
                if public_id:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete account: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Account has been deleted!', 'success')
                else:
                    flash('You need to provide an uuid to delete an account!', 'danger')

            elif action == 'updatePassword':
                public_id = request.form.get('id')
                if public_id:
                    if request.form.get('password1') == request.form.get('password2'):
                        if request.form.get('password2') != "":
                            resp = requests.put(
                                f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
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
                            flash('You are not allowed to set an emtpy password!', 'danger')
                    else:
                        flash('The entered Password\'s are not the same!', 'danger')
                else:
                    flash('You need to provide an uuid to change the password of an account!', 'danger')

            elif action == 'createRole':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name or not description:
                    flash('Unable to create Role: Name and description cannot be emtpy!', 'danger')
                else:
                    resp = requests.post(
                        f'{request.scheme}://{request.host}{url_for("role_api")}',
                        headers=header,
                        json={
                            'name': name,
                            'description': description
                        }
                    )
                    if resp.status_code != 201:
                        flash(f'Unable to create role: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Role has been created successfully!', 'success')

            elif action == 'updateRole':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name:
                    flash('Unable to update Role: Name cannot be emtpy!', 'danger')
                else:
                    if not description:
                        flash('Unable to update Role: Description cannot be emtpy!', 'danger')
                    else:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("role_api")}/{name}',
                            headers=header,
                            json={
                                'description': description
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update role: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Role has been created successfully!', 'success')

            elif action == 'deleteRole':
                name = request.form.get('name')
                if name:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("role_api")}/{name}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete role: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Role has been deleted!', 'success')
                else:
                    flash('You need to provide an name to delete a role!', 'danger')

    data = dict()
    data['accounts'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("user_api")}',
        headers=header
    ).json().get('data')

    data['roles'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("role_api")}',
        headers=header
    ).json().get('data')

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    return render_template('account-dashboard.html', user=user, data=data)


# TODO remove after testing the splitted dashboard's
@admin.route('/dashboard', methods=['GET', 'POST'])
@require_login
@require_admin
def dashboard():
    header = {'Access-Token': session.get('Access-Token')}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')

            if action == 'createAccount':

                username = request.form.get('username')
                password = request.form.get('password')
                email = request.form.get('email')
                role = request.form.get('role')

                if not username:
                    flash('Unable to create account: Username cannot be emtpy!', 'danger')
                else:
                    if not password:
                        flash('Unable to create account: Password cannot be emtpy!', 'danger')
                    else:
                        if len(password) < 8:
                            flash('Password is too short!', 'danger')
                        else:
                            if not email:
                                flash('Unable to create account: E-Mail cannot be emtpy!', 'danger')
                            else:
                                if not role:
                                    flash('Unable to create account: Role cannot be emtpy!', 'danger')
                                else:
                                    resp = requests.post(
                                        f'{request.scheme}://{request.host}{url_for("user_api")}',
                                        headers=header,
                                        json={
                                            'username': username,
                                            'password': password,
                                            'email': email,
                                            'role': role
                                        }
                                    )
                                    if resp.status_code != 201:
                                        msg = resp.json().get("message")
                                        flash(f'Unable to create account: {msg}', 'danger')
                                    else:
                                        flash('Account has been created successfully!', 'success')

            elif action == 'updateAccount':
                public_id = request.form.get('id')
                if public_id:
                    resp = requests.put(
                        f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
                        json={
                            'username': request.form.get('username'),
                            'email': request.form.get('email'),
                            'role': request.form.get('role')
                        },
                        headers=header
                    )
                    if resp.status_code != 200:
                        flash(f'Unable to update account: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Account has been update!', 'success')
                else:
                    flash('You need to provide an uuid to update an account!', 'danger')

            elif action == 'deleteAccount':
                public_id = request.form.get('id')
                if public_id:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete account: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Account has been deleted!', 'success')
                else:
                    flash('You need to provide an uuid to delete an account!', 'danger')

            elif action == 'updatePassword':
                public_id = request.form.get('id')
                if public_id:
                    if request.form.get('password1') == request.form.get('password2'):
                        if request.form.get('password2') != "":
                            resp = requests.put(
                                f'{request.scheme}://{request.host}{url_for("user_api")}/{public_id}',
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
                            flash('You are not allowed to set an emtpy password!', 'danger')
                    else:
                        flash('The entered Password\'s are not the same!', 'danger')
                else:
                    flash('You need to provide an uuid to change the password of an account!', 'danger')

            elif action == 'createRole':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name or not description:
                    flash('Unable to create Role: Name and description cannot be emtpy!', 'danger')
                else:
                    resp = requests.post(
                        f'{request.scheme}://{request.host}{url_for("role_api")}',
                        headers=header,
                        json={
                            'name': name,
                            'description': description
                        }
                    )
                    if resp.status_code != 201:
                        flash(f'Unable to create role: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Role has been created successfully!', 'success')

            elif action == 'updateRole':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name:
                    flash('Unable to update Role: Name cannot be emtpy!', 'danger')
                else:
                    if not description:
                        flash('Unable to update Role: Description cannot be emtpy!', 'danger')
                    else:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("role_api")}/{name}',
                            headers=header,
                            json={
                                'description': description
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update role: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Role has been created successfully!', 'success')

            elif action == 'deleteRole':
                name = request.form.get('name')
                if name:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("role_api")}/{name}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete role: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Role has been deleted!', 'success')
                else:
                    flash('You need to provide an name to delete a role!', 'danger')

            elif action == 'createCategory':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name or not description:
                    flash('Unable to create Category: Name and description cannot be emtpy!', 'danger')
                else:
                    resp = requests.post(
                        f'{request.scheme}://{request.host}{url_for("category_api")}',
                        headers=header,
                        json={
                            'name': name,
                            'description': description
                        }
                    )
                    if resp.status_code != 201:
                        flash(f'Unable to create category: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Category has been created successfully!', 'success')

            elif action == 'updateCategory':
                name = request.form.get('name')
                description = request.form.get('description')
                if not name:
                    flash('Unable to update Category: Name cannot be emtpy!', 'danger')
                else:
                    if not description:
                        flash('Unable to update Category: Description cannot be emtpy!', 'danger')
                    else:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("category_api")}/{name}',
                            headers=header,
                            json={
                                'description': description
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update category: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Category has been created successfully!', 'success')

            elif action == 'deleteCategory':
                name = request.form.get('name')
                if name:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("category_api")}/{name}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete category: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Category has been deleted!', 'success')
                else:
                    flash('You need to provide an name to delete a category!', 'danger')

            elif action == 'createChallenge':
                name = request.form.get('name')
                description = request.form.get('description')
                flag = request.form.get('flag')
                category_name = request.form.get('category')
                yt_challenge_id = request.form.get('ytChallengeId')
                yt_solution_id = request.form.get('ytSolutionId')
                urls = request.form.getlist('urls[]')
                url_descriptions = request.form.getlist("urlDescriptions[]")
                if not name:
                    flash('Unable to create challenge: Name cannot be emtpy!', 'danger')
                else:
                    if not flag:
                        flash('Unable to create challenge: Flag cannot be emtpy!', 'danger')
                    else:
                        if not category_name:
                            flash('Unable to create challenge: Category cannot be emtpy!', 'danger')
                        else:
                            resp = requests.post(
                                f'{request.scheme}://{request.host}{url_for("challenge_api")}',
                                headers=header,
                                json={
                                    'name': name,
                                    'description': description,
                                    'flag': flag,
                                    'category': category_name,
                                    'ytChallengeId': yt_challenge_id,
                                    'ytSolutionId': yt_solution_id
                                }
                            )
                            if resp.status_code != 201:
                                flash(f'Unable to create challenge: {resp.json().get("message")}', 'danger')
                            else:
                                challenge_id = resp.json().get('data').get('id')
                                if urls and url_descriptions:
                                    for url, description in zip(urls, url_descriptions):
                                        if url and description:
                                            resp = requests.post(
                                                f'{request.scheme}://{request.host}{url_for("url_api")}',
                                                headers=header,
                                                json={
                                                    'url': url,
                                                    'description': description,
                                                    'challenge': challenge_id
                                                }
                                            )
                                            if resp.status_code != 201:
                                                msg = resp.json().get("message")
                                                flash(f'Unable to create url {url}: {msg}', 'danger')

                                else:
                                    flash('Challenge has been created successfully!', 'success')

            elif action == 'updateChallenge':
                _id = request.form.get('id')
                description = request.form.get('description')
                yt_challenge_id = request.form.get('ytChallengeId')
                yt_solution_id = request.form.get('ytSolutionId')
                url_ids = request.form.getlist('urlIds[]')
                urls = request.form.getlist('urls[]')
                url_descriptions = request.form.getlist("urlDescriptions[]")
                if not _id:
                    flash('Unable to update challenge: ID cannot be emtpy!', 'danger')
                else:
                    resp = requests.put(
                        f'{request.scheme}://{request.host}{url_for("challenge_api")}/{_id}',
                        headers=header,
                        json={
                            'description': description,
                            'ytChallengeId': yt_challenge_id,
                            'ytSolutionId': yt_solution_id
                        }
                    )
                    if resp.status_code != 200:
                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Challenge has been created successfully!', 'success')
                        all_urls = resp.json().get('data').get('urls')
                        if url_ids and urls and url_descriptions:
                            for _id, url, description in zip(url_ids, urls, url_descriptions):
                                # if url and description contain something useful update the url
                                if url and description:
                                    resp = requests.put(
                                        f'{request.scheme}://{request.host}{url_for("url_api")}/{_id}',
                                        headers=header,
                                        json={
                                            'url': url,
                                            'description': description
                                        }
                                    )
                                    if resp.status_code != 200:
                                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')
                                else:
                                    # if url and description fields are emtpy
                                    resp = requests.delete(
                                        f'{request.scheme}://{request.host}{url_for("url_api")}/{_id}',
                                        headers=header
                                    )
                                    if resp.status_code != 204:
                                        flash(f'Unable to update challenge: {resp.json().get("message")}', 'danger')

                            # iterate over all urls for the challenge
                            for obj in all_urls:
                                # if the id from the currently saved url object is not in the request delete it
                                if str(obj.get('id')) not in url_ids:
                                    resp = requests.delete(
                                       f'{request.scheme}://{request.host}{url_for("url_api")}/{obj.get("id")}',
                                       headers=header
                                    )
                                    if resp.status_code != 204:
                                        msg = resp.json().get("message")
                                        flash(f'Unable to update challenge (url): {msg}', 'danger')
                        else:
                            # if urls and url_descriptions are completely emtpy delete all urls
                            for obj in all_urls:
                                resp = requests.delete(
                                    f'{request.scheme}://{request.host}{url_for("url_api")}/{obj.get("id")}',
                                    headers=header
                                )
                                if resp.status_code != 204:
                                    msg = resp.json().get("message")
                                    flash(f'Unable to update challenge (url): {msg}', 'danger')

            elif action == 'deleteMessage':
                _id = request.form.get('id')
                if _id:
                    resp = requests.delete(
                        f'{request.scheme}://{request.host}{url_for("message_api")}/{_id}',
                        headers=header
                    )
                    if resp.status_code != 204:
                        flash(f'Unable to delete message: {resp.json().get("message")}', 'danger')
                    else:
                        flash('Message has been deleted!', 'success')
                else:
                    flash('You need to provide an id to delete a message!', 'danger')

    data = dict()
    data['accounts'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("user_api")}',
        headers=header
    ).json().get('data')

    data['challenges'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("challenge_api")}',
        headers=header
    ).json().get('data')

    data['categories'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("category_api")}',
        headers=header
    ).json().get('data')

    data['roles'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("role_api")}',
        headers=header
    ).json().get('data')

    data['messages'] = requests.get(
        f'{request.scheme}://{request.host}{url_for("message_api")}',
        headers=header
    ).json().get('data')

    user = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header
    ).json().get('data')
    return render_template('dashboard.html', user=user, data=data)
