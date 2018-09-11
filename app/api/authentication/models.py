from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey, Integer
from uuid import uuid4
from datetime import datetime, timedelta
from flask import current_app

from app.db import db


class Token(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    token = Column('token', String(80), unique=True, nullable=False)

    user_id = Column('user', Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('users', lazy=True))

    created = Column('created', DateTime, nullable=False)
    expires = Column('expires', DateTime)
    broken = Column('broken', Boolean, nullable=False)

    def __init__(self, *args, **kwargs):
        expires = datetime.now() + timedelta(hours=current_app.config['TOKEN_VALIDITY'])
        super().__init__(*args, **kwargs, token=str(uuid4()), created=datetime.utcnow(), expires=expires, broken=False)

    def jsonify(self):
        return {
            'token': self.token,
            'user': self.user.jsonify(),
            'valid': self.broken == 0 and self.expires > datetime.utcnow()
        }

    def is_valid(self):
        return self.broken == 0 and self.expires > datetime.utcnow()
