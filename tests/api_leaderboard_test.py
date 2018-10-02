from app.api import Role, User
import json


# get the leaderboard
def test_get_leaderboard(app, client):
    resp = client.get('/api/leaderboard', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    print(resp.data)
    # TODO test more cases (solve challenge with a few users (build leaderboard then check if correct))


# get my rank
def test_get_rank(app, client):
    resp = client.get(f'/api/leaderboard/me', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    assert isinstance(json.loads(resp.data.decode()).get('data'), int)
    print(resp.data)
    # TODO test more cases (solve challenge with a few users (build leaderboard then check if correct))


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
