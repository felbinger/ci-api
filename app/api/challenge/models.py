from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime
from app.db import db


class Challenge(db.Model):
    __table_args__ = ({'mysql_character_set': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_520_ci'})
    id = Column('id', Integer, primary_key=True)
    flag = Column('flag', String(80), unique=True, nullable=False)
    points = Column('points', Integer, nullable=False)
    name = Column('name', String(80), nullable=False)
    description = Column('description', String(512), nullable=False)
    yt_challenge_id = Column('ytChallengeId', String(20), nullable=True)
    yt_solution_id = Column('ytSolutionId', String(20), nullable=True)

    publication = Column('publication', DateTime, nullable=False)
    created = Column('created', DateTime, nullable=False)

    category_id = Column('category', Integer, ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('challenges', lazy=True))

    def __init__(self, *args, **kwargs):
        kwargs['publication'] = datetime.utcnow()  # todo remove
        # todo create a field (mini calender) in the frontend and check the validation (iso 8601)
        super().__init__(*args, **kwargs, created=datetime.utcnow())

    def min_jsonify(self):
        # Used for solved challenges
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.jsonify(),
            'points': self.points
        }

    def jsonify(self):
        from ..solve import Solve
        from ..url import Url
        from ..rating import Rating
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.jsonify(),
            'points': self.points,
            'ytChallengeId': self.yt_challenge_id,
            'ytSolutionId': self.yt_solution_id,
            'urls': [url.jsonify() for url in Url.query.filter_by(challenge=self).all()],
            'solveCount': len(Solve.query.filter_by(challenge=self).all()),
            'ratings': {
                'thumbUp': len(Rating.query.filter_by(challenge=self, thumb_up=True).all()),
                'thumbDown': len(Rating.query.filter_by(challenge=self, thumb_up=False).all())
            }
        }
