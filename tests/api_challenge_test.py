from app.api import Challenge, Role, User, Url, Category
import json
from uuid import uuid4


# get challenges
def test_get_all_challenges(app, client):
    _create_dummy_challenge(app, client)
    resp = client.get('/api/challenges', headers={'Access-Token': _get_token(app, client)})
    assert len(json.loads(resp.data.decode()).get('data')) == 1


def test_get_challenges(app, client):
    _id = _create_dummy_challenge(app, client).get('id')
    resp = client.get(f'/api/challenges/{_id}', headers={'Access-Token': _get_token(app, client)})
    assert json.loads(resp.data.decode()).get('data').get('category').get('description') == 'Hacking'


def test_get_invalid_challenges(app, client):
    resp = client.get(f'/api/challenges/500', headers={'Access-Token': _get_token(app, client)})
    assert json.loads(resp.data.decode()).get('message') == 'Challenge does not exist!'


# create challenge
def test_create_challenge(app, client):
    token = _get_token(app, client)
    _create_dummy_category(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'hacking'}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    resp_data = json.loads(resp.data.decode()).get('data')
    assert resp_data.get('name') == data.get('name')
    assert resp_data.get('description') == data.get('description')
    assert resp_data.get('category').get('name') == data.get('category')
    with app.app_context():
        assert len(Challenge.query.all()) == 1


def test_create_challenge_without_data(app, client):
    resp = client.post('/api/challenges', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


# update challenge (description, video ids)
def test_update_challenge(app, client):
    token = _get_token(app, client)
    # create dummy challenge
    _create_dummy_category(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'hacking'}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    challenge_id = json.loads(resp.data.decode()).get('data').get('id')

    # update challenge
    data = {'description': 'new challenge description',
            'ytChallengeId': 'anything',
            'ytSolutionId': 'something'}
    resp = client.put(f'/api/challenges/{challenge_id}', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('description') == data.get('description')
    assert json.loads(resp.data.decode()).get('data').get('ytChallengeId') == data.get('ytChallengeId')
    assert json.loads(resp.data.decode()).get('data').get('ytSolutionId') == data.get('ytSolutionId')


def test_update_challenge_without_data(app, client):
    token = _get_token(app, client)

    _create_dummy_category(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'hacking'}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    challenge_id = json.loads(resp.data.decode()).get('data').get('id')

    resp = client.put(f'/api/challenges/{challenge_id}', headers={'Access-Token': token})
    assert resp.status_code == 200


def test_update_challenge_invalid_data(app, client):
    token = _get_token(app, client)
    # create dummy challenge
    _create_dummy_category(app, client)
    data = {'name': 'challenge name',
            'description': 'challenge description',
            'flag': 'TMT{TestFlag}',
            'category': 'hacking'}
    resp = client.post('/api/challenges', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    challenge_id = json.loads(resp.data.decode()).get('data').get('id')

    # update challenge
    data = {'invalid_key': 'new challenge description',
            'ytChallengeId': 'too long data - maximum is 10'}
    resp = client.put(f'/api/challenges/{challenge_id}', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'
    assert 'ytChallengeId' in json.loads(resp.data.decode()).get('errors')
    assert any('Length' in s for s in json.loads(resp.data.decode()).get('errors').get('ytChallengeId'))


def test_update_challenge_invalid_challenge(app, client):
    resp = client.put('/api/challenges/101010', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Challenge does not exist!'


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
        return {'id': chall.id, 'flag': 'TMT{' + _id + '}'}
