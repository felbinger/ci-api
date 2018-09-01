from app.api import Challenge, Role, User, Url
import json


# create challenge
def test_create_challenge_without_urls(app, client):
    token = _get_token(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'HC',
            'urls': []}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    resp_data = json.loads(resp.data.decode()).get('data')
    assert resp_data.get('name') == data.get('name')
    assert resp_data.get('description') == data.get('description')
    assert resp_data.get('category') == data.get('category')
    with app.app_context():
        assert len(Url.query.all()) == 0


def test_create_challenge_with_one_url(app, client):
    token = _get_token(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'HC',
            'urls': [{'description': "Challenge URL", 'url': "http://cc.the-morpheus.de/challenge/4"}]}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    resp_data = json.loads(resp.data.decode()).get('data')
    assert resp.status_code == 201
    assert resp_data.get('name') == data.get('name')
    assert resp_data.get('description') == data.get('description')
    assert resp_data.get('category') == data.get('category')
    assert resp_data.get('urls')[0].get('url') == data.get('urls')[0].get('url')
    assert resp_data.get('urls')[0].get('description') == data.get('urls')[0].get('description')
    with app.app_context():
        assert len(Url.query.all()) == 1


def test_create_challenge_with_urls(app, client):
    token = _get_token(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'HC',
            'urls': [{'description': "Challenge URL", 'url': "http://cc.the-morpheus.de/challenge/4"},
                     {'description': "Challenge URL", 'url': "http://cc.the-morpheus.de/challenge/5"}]}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    resp_data = json.loads(resp.data.decode()).get('data')
    assert resp_data.get('name') == data.get('name')
    assert resp_data.get('description') == data.get('description')
    assert resp_data.get('category') == data.get('category')
    assert resp_data.get('urls')[0].get('url') == data.get('urls')[0].get('url')
    assert resp_data.get('urls')[0].get('description') == data.get('urls')[0].get('description')
    assert resp_data.get('urls')[1].get('url') == data.get('urls')[1].get('url')
    assert resp_data.get('urls')[1].get('description') == data.get('urls')[1].get('description')
    with app.app_context():
        assert len(Url.query.all()) == 2


def test_create_challenge_without_data(app, client):
    resp = client.post('/api/challenges', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_create_challenge_invalid_urls(app, client):
    token = _get_token(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'HC',
            'urls': [{'something': "Missing both"},
                     {'url': "missing description"}]}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'URL Payload is invalid'


# update challenge (description and url's)
# TODO - after rechecking api


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