from flask.views import MethodView
from flask import request

from ..schemas import ResultSchema, ResultErrorSchema
from .models import Challenge
from app.db import db
from ..authentication import require_token, require_admin
from .schemas import DaoCreateChallengeSchema, DaoUpdateChallengeSchema


class ChallengeResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/challenge
    curl -H "Access-Token: $token" -X GET localhost:5000/api/challenge/test
    """
    @require_token
    def get(self, name, **_):
        if name is None:
            return ResultSchema(
                data=[d.jsonify() for d in Challenge.query.all()]
            ).jsonify()
        else:
            data = Challenge.query.filter_by(name=name).first()
            if not data:
                return ResultErrorSchema(
                    message='Challenge does not exist!',
                    errors=['challenge does not exist']
                ).jsonify()
            return ResultSchema(
                data=data.jsonify() or None
            ).jsonify()

    """
    curl -H "Access-Token: $token" -X POST localhost:5000/api/challenge -H "Content-Type: application/json" \
    -d '{"name": "Test", "description": "TestChallenge", "flag": "TMT{t3$T}", category: "HC"}'
    """
    @require_token
    @require_admin
    def post(self, **_):
        data = request.get_json() or {}
        schema = DaoCreateChallengeSchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        for challenge in Challenge.query.all():
            if data.get('name') == challenge.name:
                return ResultErrorSchema(
                    message='Name already in use!',
                    errors=['name already in use'],
                    status_code=400
                ).jsonify()
        challenge = Challenge(
            name=data.get('name'),
            description=data.get('description'),
            flag=data.get('flag'),
            category=data.get('category')
        )
        db.session.add(challenge)
        db.session.commit()
        return ResultSchema(
            data=challenge.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/challenge/test -H "Content-Type: application/json" \
    -d '{"description": "Test2"}'
    """
    @require_token
    @require_admin
    def put(self, name, **_):
        data = request.get_json() or {}
        schema = DaoUpdateChallengeSchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        role = Challenge.query.filter_by(name=name).first()
        if not role:
            return ResultErrorSchema(
                message='Challenge does not exist!',
                errors=['Challenge does not exist'],
                status_code=404
            ).jsonify()
        for key, val in data.items():
            setattr(role, key, val)
        db.session.commit()
        return ResultSchema(
            data=role.jsonify()
        ).jsonify()
