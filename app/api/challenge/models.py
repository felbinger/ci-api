
from app.db import db
from sqlalchemy import Column, String, Integer, ForeignKey


class Challenge(db.Model):
    id = Column('id', Integer, primary_key=True)
    flag = Column('flag', String(80), unique=True, nullable=False)
    name = Column('name', String(80), unique=True, nullable=False)
    description = Column('description', String(512), nullable=False)
    yt_challenge_id = Column('ytChallengeId', String(10))
    yt_solution_id = Column('ytSolutionId', String(10))
    category = Column('category', String(80), nullable=False)

    def jsonify(self):
        return {
            'name': self.name,
            'description': self.description,
            'ytChallengeId': self.yt_challenge_id,
            'ytSolutionId': self.yt_solution_id,
            'category': self.category,
            'urls': [url.jsonify() for url in Url.query.filter_by(challenge=self).all()]
        }


class Url(db.Model):
    id = Column('id', Integer, primary_key=True)

    challenge_id = Column('challenge', Integer, ForeignKey('challenge.id'), nullable=False)
    challenge = db.relationship('Challenge', backref=db.backref('Url', lazy=True))

    description = Column('description', String(100))
    url = Column('url', String(100), unique=True)

    def jsonify(self):
        return {
            'description': self.description,
            'url': self.url
        }
