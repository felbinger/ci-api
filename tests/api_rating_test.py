from app.api import Solve, User, Challenge, Role, Category, Rating
import json
from uuid import uuid4


# rate challenge
def test_rate_challenge(app, client):
    token = _get_token(app, client)
    c = _create_solved_dummy_challenge(app, client)
    data = {'thumbUp': True}
    resp = client.put(f'/api/rate/{c.get("id")}', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    with app.app_context():
        assert len(Rating.query.all()) == 1


def test_solve_challenge_multiple_times(app, client):
    token = _get_token(app, client)
    c = _create_solved_dummy_challenge(app, client)
    data = {'thumbUp': True}
    resp = client.put(f'/api/rate/{c.get("id")}', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    with app.app_context():
        assert len(Rating.query.all()) == 1
        resp = client.put(f'/api/rate/{c.get("id")}', headers={'Access-Token': token}, json=data)
        assert resp.status_code == 422
        assert json.loads(resp.data.decode()).get('message') == 'Challenge already rated!'
        assert len(Rating.query.all()) == 1


def test_rate_unsolved_challenge(app, client):
    c = _create_dummy_challenge(app, client)
    data = {'thumbUp': True}
    token = _get_token(app, client)
    resp = client.put(f'/api/rate/{c.get("id")}', headers={'Access-Token': token}, json=data)
    print(resp.data)
    assert resp.status_code == 422
    assert json.loads(resp.data.decode()).get('message') == 'Challenge not solved!'
    with app.app_context():
        assert len(Rating.query.all()) == 0


def test_solve_invalid_challenge(app, client):
    data = {'thumbUp': False}
    resp = client.put(f'/api/rate/500', headers={'Access-Token': _get_token(app, client)}, json=data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Challenge does not exist!'


def test_solve_challenge_without_data(app, client):
    resp = client.put('/api/rate/500', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def _create_solved_dummy_challenge(app, client):
    db = client.db
    with app.app_context():
        _id = str(uuid4())
        role = Role.query.filter_by(name="admin").first()
        if not role:
            role = Role(name='admin', description='Administrator')
        user = User.query.filter_by(username="test").first()
        if not user:
            user = User(
                username='test',
                email='testine@test.de',
                password='test',
                role=role
            )
        cat = Category.query.filter_by(name='hacking').first()
        if not cat:
            cat = Category(
                name='hacking',
                description='Hacking'
            )
            db.session.add(cat)
            db.session.commit()
        chall = Challenge(
            name=_id,
            description='Description2',
            flag='TMT{' + _id + '}',
            category=cat,
            points=0
        )
        solve = Solve(
            user=user,
            challenge=chall
        )
        db.session.add(role)
        db.session.add(user)
        db.session.add(chall)
        db.session.add(solve)
        db.session.commit()
        return {'id': chall.id, 'flag': 'TMT{' + _id + '}'}


def _create_dummy_challenge(app, client):
    db = client.db
    with app.app_context():
        _id = str(uuid4())
        cat = Category.query.filter_by(name='hacking').first()
        if not cat:
            cat = Category(
                name='hacking',
                description='Hacking'
            )
            db.session.add(cat)
            db.session.commit()
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
        user = User.query.filter_by(username="test").first()
        if not user:
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
