from app.api import Challenge, Url, Category, User, Role
import json
from uuid import uuid4


# admin: create url
def test_create_url(app, client):
    token = _get_token(app, client)
    challenge_id = _create_dummy_challenge(app, client)
    data = {
        'url': 'https://google.com',
        'description': 'Google Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('url') == data.get('url')
    assert json.loads(resp.data.decode()).get('data').get('description') == data.get('description')
    with app.app_context():
        assert json.loads(resp.data.decode()).get('data').get('description') == data.get('description')
        url_id = json.loads(resp.data.decode()).get('data').get('id')
        assert Url.query.filter_by(id=url_id).first().url == data.get('url')


def test_create_url_invalid_url(app, client):
    token = _get_token(app, client)
    challenge_id = _create_dummy_challenge(app, client)
    data = {
        'url': 'now_valid',
        'description': 'Invalid URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_create_url_without_data(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/urls', headers={'Access-Token': token})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_create_url_invalid_data(app, client):
    token = _get_token(app, client)
    data = {'url': 'something'}
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


# get all urls
def test_get_all_urls(app, client):
    token = _get_token(app, client)

    # create challenge
    challenge_id = _create_dummy_challenge(app, client)

    # Create url
    data = {
        'url': 'https://google.com',
        'description': 'Google Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201

    # Create url
    data = {
        'url': 'https://facebook.com',
        'description': 'Facebook Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201

    with app.app_context():
        # check if urls are in the database
        challenge = Challenge.query.filter_by(id=challenge_id).first()
        urls = Url.query.filter_by(challenge=challenge).all()
        assert len(urls) == 2

    # check if the urls are in the output of the challenge jsonify
    resp = client.get(f'/api/challenges/{challenge_id}', headers={'Access-Token': token})
    assert resp.status_code == 200
    assert len(json.loads(resp.data.decode()).get('data').get('urls')) == 2


# admin update url
def test_update_url(app, client):
    token = _get_token(app, client)

    # create challenge
    challenge_id = _create_dummy_challenge(app, client)

    # Create url
    data = {
        'url': 'https://facebook.com',
        'description': 'Facebook Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    url_id = json.loads(resp.data.decode()).get('data').get('id')

    # update description and url
    json_data = {'description': 'Website', 'url': 'https://the-morpheus.de'}
    resp = client.put(f'/api/urls/{url_id}', headers={'Access-Token': token}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('description') == 'Website'
    assert json.loads(resp.data.decode()).get('data').get('url') == 'https://the-morpheus.de'


def test_update_url_invalid_url(app, client):
    token = _get_token(app, client)
    json_data = {'description': 'neue Beschreibung'}
    resp = client.put(f'/api/urls/12', headers={'Access-Token': token}, json=json_data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Url does not exist!'


def test_update_url_invalid_data(app, client):
    token = _get_token(app, client)

    # create challenge
    challenge_id = _create_dummy_challenge(app, client)

    # Create url
    data = {
        'url': 'https://facebook.com',
        'description': 'Facebook Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    url_id = json.loads(resp.data.decode()).get('data').get('id')

    # edit url with invalid payload - should not affect anything
    resp = client.put(f'/api/urls/{url_id}', headers={'Access-Token': token}, json={'invalid': '1'})
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('url') == data.get('url')
    assert json.loads(resp.data.decode()).get('data').get('description') == data.get('description')


def test_delete_url(app, client):
    token = _get_token(app, client)

    # create challenge
    challenge_id = _create_dummy_challenge(app, client)

    # Create url
    data = {
        'url': 'https://facebook.com',
        'description': 'Facebook Test URL',
        'challenge': challenge_id
    }
    resp = client.post('/api/urls', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    url_id = json.loads(resp.data.decode()).get('data').get('id')

    resp = client.delete(f'/api/urls/{url_id}', headers={'Access-Token': token})
    assert resp.status_code == 204


def _create_dummy_category(app, client):
    db = client.db
    with app.app_context():
        cat = Category.query.filter_by(name='hacking').first()
        if not cat:
            cat = Category(
                name='hacking',
                description='Hacking'
            )
            db.session.add(cat)
            db.session.commit()
        return cat


def _create_dummy_challenge(app, client):
    _id = str(uuid4())
    cat = _create_dummy_category(app, client)
    chall = Challenge(
        name=_id,
        description='Description',
        flag='TMT{' + _id + '}',
        category=cat
    )
    db = client.db
    with app.app_context():
        db.session.add(chall)
        db.session.commit()
        return chall.id


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
