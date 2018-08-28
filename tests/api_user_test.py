from app.api import Role, User
import json


def test_create_user(app, client):
    _create_dummy_user(app, client)
    token = _get_token(app, client)
    data = {'username': 'qwerty',
            'displayName': 'QWERTy',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'supporterin',
            'status': 'bereit'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201


def test_create_user_error_status(app, client):
    _create_dummy_user(app, client)
    token = _get_token(app, client)
    data = {'username': 'qwerty',
            'displayName': 'QWERTy',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'supporterin',
            'status': 'ich bin nicht da!'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 404


def test_create_user_error_role(app, client):
    _create_dummy_user(app, client)
    token = _get_token(app, client)
    data = {'username': 'qwerty',
            'displayName': 'QWERTy',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'sadfouia',
            'status': 'afk'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 404


def test_create_two_equal_users(app, client):
    _create_dummy_user(app, client)
    token = _get_token(app, client)
    data = {'username': 'maximilian',
            'displayName': 'QWERTy',
            'email': 'maximilian@mustermann.de',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'supporterin',
            'status': 'bereit'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 422


def test_create_user_error(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/users', headers={'Access-Token': token})
    assert resp.status_code == 400


def test_create_user_error_wrong_data(app, client):
    token = _get_token(app, client)
    data = {'name': 'something'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400


def test_get_all_user(app, client):
    _create_dummy_user(app=app, client=client)
    resp = client.get('/api/users', headers={'Access-Token': _get_token(app, client)})
    data = json.loads(resp.data.decode()).get('data')
    assert resp.status_code == 200
    assert len(data) == 2


def test_get_user(app, client):
    user_id = _create_dummy_user(app=app, client=client)
    resp = client.get(f'/api/users/{user_id}', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200


def test_get_user_error(app, client):
    _create_dummy_user(app=app, client=client)
    resp = client.get(f'/api/users/daniel', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('errors')[0] == 'user does not exist'


def test_self_update(app, client):
    token = _get_token(app, client)
    json_data = {'displayName': 'Dante Bauer'}
    resp = client.put(f'/api/users/me', headers={'Access-Token': token}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('displayName') == 'Dante Bauer'


def test_self_update_not_allowed_change_role(app, client):
    token = _get_user_token(app, client)
    user = client.get('/api/auth', headers={'Access-Token': token})
    user_data = json.loads(user.data.decode()).get('data')
    user_id = user_data.get('publicId')
    json_data = {'role': 'admin'}
    resp = client.put(f'/api/users/{user_id}', headers={'Access-Token': token}, json=json_data)
    assert resp.status_code == 403


def test_admin_update(app, client):
    user_id = _create_dummy_user(app=app, client=client)
    json_data = {'role': 'admin'}
    resp = client.put(f'/api/users/{user_id}', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('role').get('description') == 'Administrator'


def test_admin_update_invalid_user(app, client):
    _create_dummy_user(app=app, client=client)
    json_data = {'roel': 'admin'}
    resp = client.put(f'/api/users/doof', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 404


def test_delete_user(app, client):
    user_id = _create_dummy_user(app=app, client=client)
    token = _get_token(app, client)
    resp = client.delete(f'/api/users/{user_id}', headers={'Access-Token': token})
    assert resp.status_code == 204


def _get_token(app, client):
    role = Role(name='admin', description='Administrator')
    user = User(
        username='test',
        email='testine@test.de',
        password='test',
        role=role
    )
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    data = json.loads(resp.data.decode())
    return data.get('token')


def _get_user_token(app, client):
    role = Role(name='user', description='Benutzer')
    user = User(
        username='test22',
        email='testine@test.de',
        password='test22',
        role=role
    )
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
    resp = client.post('/api/auth', json={'username': 'test22', 'password': 'test22'})
    data = json.loads(resp.data.decode())
    return data.get('token')


def _create_dummy_user(app, client):
    role = Role(name='supporterin', description='Supporterin')
    user = User(
        username='maximilian',
        email='maximilian@mustermann.de',
        password='maximilian',
        role=role
    )
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        public_id = user.public_id
        db.session.commit()
    return public_id
