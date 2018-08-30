from app.api import Role, User
import json


# admin: create role
def test_create_role(app, client):
    token = _get_token(app, client)
    data = {'name': 'test_role', 'description': 'test_role_description'}
    resp = client.post('/api/roles', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('name') == data.get('name')
    assert json.loads(resp.data.decode()).get('data').get('description') == data.get('description')


def test_create_role_without_data(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/roles', headers={'Access-Token': token})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_create_role_invalid_data(app, client):
    token = _get_token(app, client)
    data = {'name': 'something'}
    resp = client.post('/api/roles', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


# get all roles
def test_get_all_roles(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    _create_dummy_role(app=app, client=client, name='user')
    token = _get_token(app, client)
    resp = client.get('/api/roles', headers={'Access-Token': token})
    assert resp.status_code == 200
    with app.app_context():
        assert len(json.loads(resp.data.decode()).get('data')) == len(Role.query.all())


# get role by name
def test_get_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.get(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('description') == 'test'


def test_get_role_invalid_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.get(f'/api/roles/invalid_role', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Role does not exist!'


# admin update role
def test_update_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    json_data = {'description': 'new description'}
    resp = client.put(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('description') == 'new description'


def test_update_role_invalid_role(app, client):
    json_data = {'description': 'neue Beschreibung'}
    resp = client.put(f'/api/roles/afk', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Role does not exist!'


def test_update_role_invalid_data(app, client):
    _create_dummy_role(app=app, client=client, name='abc')
    json_data = {'a': '1'}
    resp = client.put(f'/api/roles/abc', headers={'Access-Token': _get_token(app, client)}, json=json_data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_delete_role(app, client):
    _create_dummy_role(app=app, client=client, name='support')
    resp = client.delete(f'/api/roles/support', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 204


def _generate_default(app, client):
    db = client.db
    with app.app_context():
        if len(Role.query.all()) < 2:
            if not Role.query.filter_by(name="admin").first():
                admin = Role(
                    name="admin",
                    description="Administrator"
                )
                db.session.add(admin)
            if not Role.query.filter_by(name="user").first():
                user = Role(
                    name="user",
                    description="User"
                )
                db.session.add(user)
            db.session.commit()


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


def _create_dummy_role(app, client, name):
    role = Role(name=name, description='test')
    db = client.db
    with app.app_context():
        db.session.add(role)
        db.session.commit()
    return role
