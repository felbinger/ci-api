from app.api import Role, User, require_admin
import json
import jwt
from dateutil import parser
from flask import Flask


def test_auth(app, client):
    _create_dummy_user(app, client)
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    data = resp.data.decode()
    assert resp.status_code == 200
    assert isinstance(data, str)
    assert 'token' in json.loads(data)


def test_auth_error_without_data(client):
    resp = client.post('/api/auth')
    assert resp.status_code == 400


def test_auth_error_wrong_data(client):
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    assert resp.status_code == 401


def test_get_user_data(app, client):
    _create_dummy_user(app, client)
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    data = json.loads(resp.data.decode())
    token = data.get('token')
    data_resp = client.get('/api/auth', headers={'Access-Token': token})
    user_data = json.loads(data_resp.data.decode())
    assert data_resp.status_code == 200
    created = user_data.get('data').get('created')
    assert 'username' in user_data.get('data')
    assert parser.parse(created)


def test_get_user_data_without_token(client):
    resp = client.get('/api/auth')
    assert resp.status_code == 401


def test_get_user_data_wrong_token(client):
    fake_token = jwt.encode({'publicKey': '1'}, key='sekrit')
    resp = client.get('/api/auth', headers={'Access-Token': fake_token})
    assert resp.status_code == 401


def test_get_user_data_invalid_token(app, client):
    fake_token = jwt.encode({'publicKey': '1'}, key=app.config['SECRET_KEY'])
    resp = client.get('/api/auth', headers={'Access-Token': fake_token})
    assert resp.status_code == 401


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


def test_require_admin_error():
    app = Flask(__name__)

    @app.route('/')
    @require_admin
    def index(): pass
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 500


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
