from flask.views import MethodView
from flask import request

from app.db import db
from ..authentication import require_token
from ..schemas import ResultSchema, ResultErrorSchema
from ..challenge import Challenge
from ..solve import Solve
from .models import Rating
from .schemas import DaoRateSchema


class RatingResource(MethodView):
    """
    Rate Challenge
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/rate/<id:Int> -H "Content-Type: application/json" \
    -d '{"thumbUp": false}'
    """
    @require_token
    def put(self, _id, user, **_):
        data = request.get_json() or {}
        schema = DaoRateSchema()
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

        # check if the user has solved the challenge
        if not Solve.query.filter_by(user=user, challenge=challenge).first():
            return ResultErrorSchema(
                message='Challenge not solved!',
                errors=['challenge not solved'],
                status_code=422
            ).jsonify()

        # check if the challenge has already be rated by the user
        already_rated = Rating.query.filter_by(user=user).all()
        if already_rated:
            for chall in already_rated:
                if chall.challenge == challenge:
                    return ResultErrorSchema(
                        message='Challenge already rated!',
                        errors=['challenge already rated'],
                        status_code=422
                    ).jsonify()

        rating = Rating(
            user=user,
            challenge=challenge,
            thumb_up=data.get('thumbUp')
        )
        db.session.add(rating)
        db.session.commit()
        return ResultSchema(
            status_code=201
        ).jsonify()
