from datetime import datetime
from app.db import db
from sqlalchemy import Column, DateTime, Integer, ForeignKey


class Solve(db.Model):
    id = Column('id', Integer, primary_key=True)

    user_id = Column('user', Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('Solve', lazy=True))

    challenge_id = Column('challenge', Integer, ForeignKey('challenge.id'), nullable=False)
    challenge = db.relationship('Challenge', backref=db.backref('Solve', lazy=True))

    timestamp = Column('created', DateTime, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, timestamp=datetime.utcnow())

    def jsonify(self):
        return {
            'challenge': self.challenge.jsonify(),
            'timestamp': self.timestamp
        }