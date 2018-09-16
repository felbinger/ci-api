from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from uuid import uuid4
from hashlib import sha512
from datetime import datetime

from app.db import db


class Message(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    subject = Column('subject', String(80), unique=True, nullable=False)
    message = Column('message', String(1000), nullable=False)

    created = Column('created', DateTime)

    user_id = Column('user', Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('message', lazy=True))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, created=datetime.utcnow())

    def jsonify(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'message': self.message,
            'created': self.created.strftime("%d.%m.%Y %H:%M:%S"),
            'user': self.user.jsonify()
        }
