from app.db import db
from sqlalchemy import Column, String, Integer


class Role(db.Model):
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(80), unique=True, nullable=False)
    description = Column('description', String(80), nullable=False)

    def jsonify(self):
        return {
            'name': self.name,
            'description': self.description
        }