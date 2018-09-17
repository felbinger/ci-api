from app.api import User, Role, Challenge, Solve, Category, Message
from uuid import UUID


def test_create_models(client):
    assert client.db is not None


def test_create_challenge(app, client):
    cat = Category(
        name='test',
        description='Test'
    )
    db = client.db
    challenge = Challenge(name="TEST", description="TEST", flag="TEST", category=cat, points=30)
    with app.app_context():
        db.session.add(challenge)
        db.session.add(cat)
        db.session.commit()
        assert len(Challenge.query.all()) == 1


def test_solve_challenge(app, client):
    db = client.db

    role = Role(name='admin', description='Administrator')
    user = User(
        username='test',
        email='testine@test.de',
        password='testineTestHatEinPw',
        role=role
    )
    cat = Category(
        name='test',
        description='Test'
    )
    challenge = Challenge(name="TEST", description="TEST", flag="TEST", category=cat)
    solve = Solve(challenge=challenge, user=user)
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.add(challenge)
        db.session.add(cat)
        db.session.add(solve)
        db.session.commit()
        assert len(Solve.query.all()) == 1


def test_create_category(app, client):
    cat = Category(
        name='test',
        description='Test'
    )
    db = client.db
    with app.app_context():
        db.session.add(cat)
        db.session.commit()


def test_create_role(app, client):
    db = client.db
    role = Role(name='admin', description='Administrator')
    with app.app_context():
        db.session.add(role)
        db.session.commit()
        assert len(Role.query.all()) == 1


def test_create_user(app, client):
    db = client.db
    role = Role(name='admin', description='Administrator')
    user = User(
        username='test',
        email='testine@test.de',
        password='testineTestHatEinPw',
        role=role
    )
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
        first = User.query.first()

    assert isinstance(first, User)
    assert len(UUID(first.public_id).hex) == 32
    assert first.verify_password('testineTestHatEinPw')


def test_create_message(app, client):
    db = client.db
    role = Role(name='admin', description='Administrator')
    user = User(
        username='test',
        email='testine@test.de',
        password='testineTestHatEinPw',
        role=role
    )
    msg = Message(
        subject="test",
        message="test",
        user=user
    )
    with app.app_context():
        db.session.add(role)
        db.session.add(user)
        db.session.add(msg)
        db.session.commit()
