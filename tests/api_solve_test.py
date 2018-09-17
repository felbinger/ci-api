from app.api import Solve, User, Challenge, Role, Category
import json
from uuid import uuid4


# get all solved challenges
def test_get_solved_challenges(app, client):
    token = _get_token(app, client)
    # create challenges
    c1 = _create_dummy_challenge(app, client)
    c2 = _create_dummy_challenge(app, client)

    # solve challenges
    resp = client.put(f'/api/solve/{c1.get("id")}', headers={'Access-Token': token}, json={'flag': c1.get('flag')})
    resp = client.put(f'/api/solve/{c2.get("id")}', headers={'Access-Token': token}, json={'flag': c2.get('flag')})
    assert resp.status_code == 201

    # get solved challenges
    resp = client.get('/api/solve', headers={'Access-Token': token})
    assert resp.status_code == 200
    assert len(json.loads(resp.data.decode()).get('data')) == 2


# solve special challenge
def test_solve_special_challenge(app, client):
    flag = _create_special_challenge(app, client)
    resp = client.post('/api/solve', headers={'Access-Token': _get_token(app, client)}, json={'flag': flag})
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('challenge').get('category').get('description') == 'Special'
    db = client.db
    with app.app_context():
        assert len(Solve.query.all()) == 1


def test_solve_special_challenge_multiple_times(app, client):
    flag = _create_special_challenge(app, client)
    token = _get_token(app, client)
    resp = client.post('/api/solve', headers={'Access-Token': token}, json={'flag': flag})
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('challenge').get('category').get('description') == 'Special'
    db = client.db
    with app.app_context():
        assert len(Solve.query.all()) == 1
        resp = client.post('/api/solve', headers={'Access-Token': token}, json={'flag': flag})
        assert resp.status_code == 422
        assert json.loads(resp.data.decode()).get('message') == 'Challenge already solved!'
        assert len(Solve.query.all()) == 1


def test_solve_special_challenge_without_data(app, client):
    resp = client.post('/api/solve', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_solve_special_challenge_invalid_flag(app, client):
    data = {'flag': 'invalid'}
    resp = client.post('/api/solve', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Invalid flag!'


# solve challenge - also special challenges - but id is not really submitable
def test_solve_challenge(app, client):
    c = _create_dummy_challenge(app, client)
    data = {'flag': c.get('flag')}
    resp = client.put(f'/api/solve/{c.get("id")}', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('challenge').get('category').get('description') == 'Hacking'
    with app.app_context():
        assert len(Solve.query.all()) == 1


def test_solve_challenge_multiple_times(app, client):
    token = _get_token(app, client)
    c = _create_dummy_challenge(app, client)
    data = {'flag': c.get('flag')}
    resp = client.put(f'/api/solve/{c.get("id")}', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('challenge').get('category').get('description') == 'Hacking'
    with app.app_context():
        assert len(Solve.query.all()) == 1
        resp = client.put(f'/api/solve/{c.get("id")}', headers={'Access-Token': token}, json=data)
        assert resp.status_code == 422
        assert json.loads(resp.data.decode()).get('message') == 'Challenge already solved!'
        assert len(Solve.query.all()) == 1


def test_solve_invalid_challenge(app, client):
    data = {'flag': 'not_relevant'}
    resp = client.put(f'/api/solve/500', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Challenge does not exist!'


def test_solve_challenge_without_data(app, client):
    resp = client.put('/api/solve/500', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_solve_challenge_invalid_flag(app, client):
    c = _create_dummy_challenge(app, client)
    data = {'flag': 'invalid'}
    resp = client.put(f'/api/solve/{c.get("id")}', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Invalid flag!'


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


def _create_special_category(app, client):
    db = client.db
    with app.app_context():
        cat = Category.query.filter_by(name='Special').first()
        if not cat:
            cat = Category(
                name='Special',
                description='Special'
            )
            db.session.add(cat)
            db.session.commit()
        return cat


def _create_special_challenge(app, client):
    db = client.db
    with app.app_context():
        _id = str(uuid4())
        cat = _create_special_category(app, client)
        chall = Challenge(
            name=_id,
            description='Description',
            flag='TMT{' + _id + '}',
            category=cat,
            points=0
        )
        db.session.add(chall)
        db.session.commit()
        return 'TMT{' + _id + '}'


def _create_dummy_challenge(app, client):
    db = client.db
    with app.app_context():
        _id = str(uuid4())
        cat = _create_dummy_category(app, client)
        chall = Challenge(
            name=_id,
            description='Description',
            flag='TMT{' + _id + '}',
            category=cat,
            points=0
        )
        db.session.add(chall)
        db.session.commit()
        return {'id': chall.id, 'flag': 'TMT{' + _id + '}'}


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
