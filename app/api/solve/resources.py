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
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/solve/<name:String> -H "Content-Type: application/json" \
    -d '{"flag": "TMT{TEST}"}'
    """
    @require_token
    def put(self, name, user, **_):
        data = request.get_json() or {}
        schema = DaoSolveChallengeSchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()

        challenge = Challenge.query.filter_by(name=name).first()
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