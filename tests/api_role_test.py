from app.api import Role, User
import json


def test_create_role(app, client):
    token = _get_token(app, client)
    data = {'name': 'testrolle', 'description': 'testrollenbeschreibung'}
    resp = client.post('/api/roles', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201


def test_create_role_error(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/roles', headers={'Access-Token': token})
    assert resp.status_code == 400


def test_create_role_error_wrong_data(app, client):
    token = _get_token(app, client)
    data = {'name': 'something'}
    resp = client.post('/api/roles', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400


def test_get_all_roles(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    _create_dummy_role(app=app, client=client, name='user')
    token = _get_token(app, client)
    resp = client.get('/api/roles', headers={'Access-Token': token})
    data = json.loads(resp.data.decode()).get('data')
    assert resp.status_code == 200
    assert len(data) == 3


def test_get_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.get(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200


def test_get_role_error(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.get(f'/api/roles/asfasrtasfc23t4', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('errors')[0] == 'role does not exist'


def test_update_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    json_data = {'description': 'neue Beschreibung'}
    resp = client.put(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('description') == 'neue Beschreibung'


def test_update_role_error(app, client):
    _create_dummy_role(app=app, client=client, name='abc')
    json_data = {'description': 'neue Beschreibung'}
    resp = client.put(f'/api/roles/afk', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 404


def test_update_role_error_invalid_data(app, client):
    _create_dummy_role(app=app, client=client, name='abc')
    json_data = {'a': '1'}
    resp = client.put(f'/api/roles/abc', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 400


def test_delete_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.delete(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 204


def _get_token(app, client):
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
    resp = client.post('/api/auth', json={'username': 'test', 'password': 'test'})
    data = json.loads(resp.data.decode())
    return data.get('token')


def _create_dummy_role(app, client, name):
    role = Role(name=name, description='test')
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.commit()
    return role
