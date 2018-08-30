from app.api import Role, User
import json
from hashlib import sha512


# register user
def test_register_user(app, client):
    _generate_default(app, client)
    data = {'username': 'querty',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg'}
    resp = client.post('/api/users', json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('username') == data.get('username')
    assert json.loads(resp.data.decode()).get('data').get('email') == data.get('email')
    assert json.loads(resp.data.decode()).get('data').get('role').get('name') == "user"
    with app.app_context():
        user = User.query.filter_by(username=data.get('username')).first()
        assert user.password == sha512(data.get('password').encode('utf8')).hexdigest()


def test_register_user_without_data(app, client):
    resp = client.post('/api/users')
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == "Payload is invalid"


# Admin: create user
def test_create_user(app, client):
    token = _get_token(app, client)
    data = {'username': 'qwerty',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'admin'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('username') == data.get('username')
    assert json.loads(resp.data.decode()).get('data').get('email') == data.get('email')
    assert json.loads(resp.data.decode()).get('data').get('role').get('name') == data.get('role')
    with app.app_context():
        user = User.query.filter_by(username=data.get('username')).first()
        assert user.password == sha512(data.get('password').encode('utf8')).hexdigest()


def test_create_user_error_role(app, client):
    token = _get_token(app, client)
    data = {'username': 'qwerty',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'invalid_role'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Role does not exist!'


def test_create_two_equal_usernames(app, client):
    _generate_default(app, client)
    token = _get_token(app, client)
    data = {'username': 'test',
            'email': 'test@test.de',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'user'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 422
    assert json.loads(resp.data.decode()).get('message') == 'Username or email already in use!'


def test_create_user_without_data(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/users', headers={'Access-Token': token})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == "Payload is invalid"


def test_create_user_invalid_data(app, client):
    token = _get_token(app, client)
    data = {'name': 'something'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == "Payload is invalid"


def test_create_user_as_user(app, client):
    token = _get_user_token(app, client)
    data = {'username': 'qwerty',
            'email': 'qu@er.ty',
            'password': 'i7Co8yvFWDGZfNMUQtcg',
            'role': 'user'}
    resp = client.post('/api/users', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 403
    assert json.loads(resp.data.decode()).get('message') == 'Forbidden'


# Admin: get user by publicId
def test_get_user(app, client):
    user_id = _create_dummy_user(app=app, client=client)
    resp = client.get(f'/api/users/{user_id}', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('publicId') == user_id


def test_get_invalid_user(app, client):
    resp = client.get(f'/api/users/fake_user_id', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'User does not exist!'


# Admin: get all users
def test_get_all_user(app, client):
    _create_dummy_user(app=app, client=client)
    resp = client.get('/api/users', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    with app.app_context():
        assert len(json.loads(resp.data.decode()).get('data')) == len(User.query.all())


# update user (identified by /me)
def test_self_update(app, client):
    token = _get_token(app, client)
    json_data = {'email': 'my-new@email.de'}
    resp = client.put(f'/api/users/me', headers={'Access-Token': token}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('email') == json_data.get('email')


def test_self_update_not_allowed_change_role(app, client):
    json_data = {'role': 'admin'}
    resp = client.put(f'/api/users/me', headers={'Access-Token': _get_user_token(app, client)}, json=json_data)
    assert resp.status_code == 403
    assert json.loads(resp.data.decode()).get('message') == 'You are not allowed to change your role!'


# Admin: update user (identified by publicId)
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
    json.loads(resp.data.decode()).get('message') == 'User does not exist'


# delete user (identified by /me)
def test_self_delete(app, client):
    resp = client.delete(f'/api/users/me', headers={'Access-Token': _get_user_token(app, client)})
    assert resp.status_code == 204


# Admin: delete user (identified by publicId)
def test_delete_user(app, client):
    user_id = _create_dummy_user(app=app, client=client)
    resp = client.delete(f'/api/users/{user_id}', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 204


def _generate_default(app, client):
    db = client.db
    with app.app_context():
        if len(Role.query.all()) < 2:
            if not Role.query.filter_by(name="admin").first():
                admin = Role(
                    name="admin",
                    description="Administrator"
                )
                db.session.add(admin)
            if not Role.query.filter_by(name="user").first():
                user = Role(
                    name="user",
                    description="User"
                )
                db.session.add(user)
            db.session.commit()


def _get_token(app, client):
    with app.app_context():
        role = Role.query.filter_by(name="admin").first()
        if not role:
            role = Role(name='admin', description='Administrator')
        user = User(
            username='test',
            email='testine@test.de',
            password='test',
            role=role
        )
        db = client.db
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    data = json.loads(resp.data.decode())
    return data.get('token')


def _get_user_token(app, client):
    with app.app_context():
        role = Role.query.filter_by(name="user").first()
        if not role:
            role = Role(name='user', description='User')
        user = User(
            username='test22',
            email='testine@test.de',
            password='test22',
            role=role
        )
        db = client.db
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

