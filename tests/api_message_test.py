from app.api import Role, User, Message
import json


# admin: create message
def test_create_message(app, client):
    token = _get_token(app, client)
    data = {'subject': 'TestSubject', 'message': 'TestMessage'}
    resp = client.post('/api/messages', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 201
    assert json.loads(resp.data.decode()).get('data').get('message') == data.get('message')
    assert json.loads(resp.data.decode()).get('data').get('subject') == data.get('subject')
    assert json.loads(resp.data.decode()).get('data').get('user').get('username') == 'test'


def test_create_message_without_data(app, client):
    token = _get_token(app, client)
    resp = client.post('/api/messages', headers={'Access-Token': token})
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


def test_create_message_invalid_data(app, client):
    token = _get_token(app, client)
    data = {'name': 'something'}
    resp = client.post('/api/messages', headers={'Access-Token': token}, json=data)
    assert resp.status_code == 400
    assert json.loads(resp.data.decode()).get('message') == 'Payload is invalid'


# get all messages
def test_get_all_messages(app, client):
    _create_dummy_message(app=app, client=client, subject='support')
    _create_dummy_message(app=app, client=client, subject='user')
    token = _get_token(app, client)
    resp = client.get('/api/messages', headers={'Access-Token': token})
    assert resp.status_code == 200
    with app.app_context():
        assert len(json.loads(resp.data.decode()).get('data')) == len(Message.query.all())


# get message by id
def test_get_message(app, client):
    _create_dummy_message(app=app, client=client, subject='test')
    resp = client.get(f'/api/messages/1', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 200
    assert json.loads(resp.data.decode()).get('data').get('subject') == 'test'
    assert json.loads(resp.data.decode()).get('data').get('message') == 'MyMessage'


def test_get_message_invalid_message(app, client):
    _create_dummy_message(app=app, client=client, subject='support')
    resp = client.get(f'/api/messages/9', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 404
    assert json.loads(resp.data.decode()).get('message') == 'Message does not exist!'


def test_delete_message(app, client):
    _create_dummy_message(app=app, client=client, subject='support')
    resp = client.delete(f'/api/messages/1', headers={'Access-Token': _get_token(app, client)})
    assert resp.status_code == 204


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


def _create_dummy_message(app, client, subject):
    db = client.db
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
        message = Message(subject=subject, message='MyMessage', user=user)
        db.session.add(message)
        db.session.commit()
        return message
