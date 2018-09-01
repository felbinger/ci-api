from app.api import Solve, User, Challenge, Role
import json
from uuid import uuid4


# get all solved challenges
def test_get_solved_challenges(app, client):
    token = _get_token(app, client)
    # create challenges
    names = list()
    names.append(_create_dummy_challenge(app, client))
    names.append(_create_dummy_challenge(app, client))

    # solve challenges
    for name in names:
        data = {'flag': 'TMT{' + name + '}'}
        resp = client.put(f'/api/solve/{name}', headers={'Access-Token': token}, json=data)
        assert resp.status_code == 201

    # get solved challenges
    resp = client.get('/api/solve', headers={'Access-Token': token})
    assert resp.status_code == 200
    assert len(json.loads(resp.data.decode()).get('data')) == len(names)


# solve challenge
def test_solve_challenge(app, client):
    name = _create_dummy_challenge(app, client)
    data = {'flag': 'TMT{' + name + '}'}
    resp = client.put(f'/api/solve/{name}', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('challenge').get('category') == 'Test'
    db = client.db
    with app.app_context():
        assert len(Solve.query.all()) == 1


def test_solve_invalid_challenge(app, client):
    data = {'flag': 'not_relevant'}
    resp = client.put(f'/api/solve/invalid', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Challenge does not exist!'


def test_solve_challenge_without_data(app, client):
    resp = client.put('/api/solve/challenge', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_solve_challenge_invalid_flag(app, client):
    name = _create_dummy_challenge(app, client)
    data = {'flag': 'invalid'}
    resp = client.put(f'/api/solve/{name}', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Invalid flag!'


def _create_dummy_challenge(app, client):
    _id = str(uuid4())
    chall = Challenge(
        name=_id,
        description='Description',
        flag='TMT{' + _id + '}',
        category='Test'
    )
    db = client.db
    with app.app_context():
        db.session.add(chall)
        db.session.commit()
        return chall.name


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
