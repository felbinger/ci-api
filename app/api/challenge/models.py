
from app.db import db
from sqlalchemy import Column, String, Integer


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
            'category': self.category
        }