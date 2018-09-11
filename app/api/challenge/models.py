from sqlalchemy import Column, String, Integer, ForeignKey

from app.db import db


class Challenge(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    flag = Column('flag', String(80), unique=True, nullable=False)
    name = Column('name', String(80), nullable=False)
    description = Column('description', String(512), nullable=False)
    yt_challenge_id = Column('ytChallengeId', String(20), nullable=True)
    yt_solution_id = Column('ytSolutionId', String(20), nullable=True)

    category_id = Column('category', Integer, ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('challenges', lazy=True))

    def min_jsonify(self):
        # Used for solved challenges
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.jsonify()
        }

    def jsonify(self):
        from ..solve import Solve
        from ..url import Url
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.jsonify(),
            'ytChallengeId': self.yt_challenge_id,
            'ytSolutionId': self.yt_solution_id,
            'urls': [url.jsonify() for url in Url.query.filter_by(challenge=self).all()],
            'solveCount': len(Solve.query.filter_by(challenge=self).all())
        }
