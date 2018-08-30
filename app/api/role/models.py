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

    def check(self):
        # Create default roles if the does not exist.
        if len(Role.query.all()) < 2:
            if not Role.query.filter_by(name="admin").first():
                admin = Role(
                    name="admin",
                    description="Administrator"
                )
                db.session.add(admin)
            if not Role.query.filter_by(name="user").first():
                user = Role(
                    name="user",
                    description="User"
                )
                db.session.add(user)
            db.session.commit()
