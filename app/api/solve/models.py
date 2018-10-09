from sqlalchemy import Column, DateTime, Integer, ForeignKey
from datetime import datetime

from app.db import db


class Solve(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)

    user_id = Column('user', Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('solves', lazy=True))

    challenge_id = Column('challenge', Integer, ForeignKey('challenge.id'), nullable=False)
    challenge = db.relationship('Challenge', backref=db.backref('solves', lazy=True))

    timestamp = Column('created', DateTime, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, timestamp=datetime.utcnow())

    def jsonify(self):
        return {
            'challenge': self.challenge.min_jsonify(),
            'timestamp': self.timestamp
        }
