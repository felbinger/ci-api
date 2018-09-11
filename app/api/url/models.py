from sqlalchemy import Column, String, Integer, ForeignKey

from app.db import db


class Url(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    url = Column('url', String(80), unique=True, nullable=False)
    description = Column('description', String(80), nullable=False)

    challenge_id = Column('challenge', Integer, ForeignKey('challenge.id'), nullable=False)
    challenge = db.relationship('Challenge', backref=db.backref('url', lazy=True))

    def jsonify(self):
        return {
            'id': self.id,
            'url': self.url,
            'description': self.description
        }
