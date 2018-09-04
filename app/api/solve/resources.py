from flask.views import MethodView
from flask import request

from ..schemas import ResultSchema, ResultErrorSchema
from .models import Solve
from app.db import db
from ..authentication import require_token
from .schemas import DaoSolveChallengeSchema
from ..challenge import Challenge


class SolveResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/solve
    """
    @require_token
    def get(self, user, **_):
        return ResultSchema(
            data=[d.jsonify() for d in Solve.query.filter_by(user=user).all()]
        ).jsonify()

    """
    Solve Method for special challenges
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/solve/<id:Int> -H "Content-Type: application/json" \
    -d '{"flag": "TMT{TEST}"}'
    """
    @require_token
    def post(self, user, **_):
        data = request.get_json() or {}
        schema = DaoSolveChallengeSchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        challenge = Challenge.query.filter_by(flag=data.get('flag')).first()
        if not challenge or challenge.category.name != 'Special':
            return ResultErrorSchema(
                message="Invalid flag!",
                errors=["invalid flag"],
                status_code="404"
            ).jsonify()

        user_solved = Solve.query.filter_by(user=user).all()
        if user_solved:
            for chall in user_solved:
                if chall.challenge == challenge:
                    return ResultErrorSchema(
                        message='Challenge already solved!',
                        errors=['challenge already solved'],
                        status_code=422
                    ).jsonify()
        solve = Solve(
            user=user,
            challenge=challenge
        )
        db.session.add(solve)
        db.session.commit()

        return ResultSchema(
            data=solve.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/solve/<id:Int> -H "Content-Type: application/json" \
    -d '{"flag": "TMT{TEST}"}'
    """
    @require_token
    def put(self, _id, user, **_):
        data = request.get_json() or {}
        schema = DaoSolveChallengeSchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()

        challenge = Challenge.query.filter_by(id=_id).first()
        if not challenge:
            return ResultErrorSchema(
                message='Challenge does not exist!',
                errors=['challenge does not exist'],
                status_code=404
            ).jsonify()

        if challenge.flag != data.get('flag'):
            return ResultErrorSchema(
                message="Invalid flag!",
                errors=["invalid flag"],
                status_code="404"
            ).jsonify()

        user_solved = Solve.query.filter_by(user=user).all()
        if user_solved:
            for chall in user_solved:
                if chall.challenge == challenge:
                    return ResultErrorSchema(
                        message='Challenge already solved!',
                        errors=['challenge already solved'],
                        status_code=422
                    ).jsonify()

        solve = Solve(
            user=user,
            challenge=challenge
        )
        db.session.add(solve)
        db.session.commit()
        return ResultSchema(
            data=solve.jsonify(),
            status_code=201
        ).jsonify()
