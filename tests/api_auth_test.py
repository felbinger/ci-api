from app.api import Role, User, require_admin
import json
# import jwt
from dateutil import parser
from flask import Flask


def test_auth(app, client):
    _create_dummy_user(app, client)
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    assert resp.status_code == 200
    assert 'token' in json.loads(resp.data.decode())


def test_auth_invalid_credentials(app, client):
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    assert resp.status_code == 401
    assert json.loads(resp.data.decode('utf8')).get('message') == 'Wrong credentials'


def test_auth_without_data(app, client):
    resp = client.post('/api/auth')
    assert resp.status_code == 400


def test_logout(app, client):
    token = _get_user_token(app, client)
    resp = client.delete('/api/auth', headers={'Access-Token': token})
    assert resp.status_code == 204


def test_logout_without_token(app, client):
    resp = client.delete('/api/auth')
    assert resp.status_code == 401
    assert json.loads(resp.data.decode('utf8')).get('message') == 'Missing Access-Token'


def test_logout_invalid_token(app, client):
    resp = client.delete('/api/auth', headers={'Access-Token': 'I am a test token!'})
    assert resp.status_code == 401
    assert json.loads(resp.data.decode('utf8')).get('message') == 'Invalid Access-Token'


def test_get_user_data(app, client):
    token = _get_user_token(app, client)
    resp = client.get('/api/auth', headers={'Access-Token': token})
    assert resp.status_code == 200
    assert 'username' in json.loads(resp.data.decode()).get('data')
    assert parser.parse(json.loads(resp.data.decode()).get('data').get('created'))


def test_get_user_data_without_token(app, client):
    resp = client.get('/api/auth')
    assert resp.status_code == 401
    assert json.loads(resp.data.decode('utf8')).get('message') == 'Missing Access-Token'


def test_get_user_data_invalid_token(app, client):
    resp = client.get('/api/auth', headers={'Access-Token': 'I am a test token!'})
    assert resp.status_code == 401
    assert json.loads(resp.data.decode('utf8')).get('message') == 'Invalid Access-Token'


def test_require_admin_without_require_token():
    app = Flask(__name__)

    @app.route('/')
    @require_admin
    def index(): pass
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 500


def _create_dummy_user(app, client):
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


def _get_user_token(app, client):
    role = Role(name='user', description='user')
    user = User(
        username='test2',
        email='testine2@tes2t.de',
        password='test',
        role=role
    )
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
    resp = client.post('/api/auth', json={'username': 'test2', 'password': 'test'})
    data = json.loads(resp.data.decode())
    return data.get('token')
