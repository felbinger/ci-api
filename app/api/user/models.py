from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from uuid import uuid4
from hashlib import sha512
from datetime import datetime
from app.db import db


class User(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    public_id = Column('publicId', String(80), unique=True, nullable=False)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(100), unique=True, nullable=False)
    password = Column('passwd', String(255), nullable=False)
    created = Column('created', DateTime, nullable=False)
    last_login = Column('lastLogin', DateTime)

    role_id = Column('role', Integer, ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def __init__(self, *args, **kwargs):
        kwargs['password'] = sha512(kwargs['password'].encode()).hexdigest()
        super().__init__(*args, **kwargs, public_id=str(uuid4()), created=datetime.utcnow())

    def jsonify(self):
        from ..solve import Solve
        return {
            'publicId': self.public_id,
            'username': self.username,
            'email': self.email,
            'created': self.created.strftime("%d.%m.%Y %H:%M:%S"),
            'lastLogin': self.last_login.strftime("%d.%m.%Y %H:%M:%S") if self.last_login else None,
            'role': self.role.jsonify(),
            'solved': [solve.jsonify() for solve in Solve.query.filter_by(user=self).all()]
        }

    def verify_password(self, password):
        return self.password == sha512(password.encode()).hexdigest()
