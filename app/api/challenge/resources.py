# import dateutil.parser
from flask.views import MethodView
from flask import request
from datetime import datetime

from app.db import db
from ..schemas import ResultSchema, ResultErrorSchema
from ..categories import Category
from ..authentication import require_token, require_admin
from ..solve import Solve
from .models import Challenge
from .schemas import DaoCreateChallengeSchema, DaoUpdateChallengeSchema


class ChallengeResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/challenges
    curl -H "Access-Token: $token" -X GET localhost:5000/api/challenges/1
    """
    @require_token
    def get(self, _id, **_):
        if _id is None:
            # get all challenges (except not published and special challenges)
            return ResultSchema(
                data=[d.jsonify() for d in Challenge.query.filter(
                    Challenge.category != Category.query.filter_by(name='special').first(),
                    Challenge.publication < datetime.now()
                ).all()]
            ).jsonify()
        else:
            # get the challenge object by the submitted name in the resource (url)
            challenge = Challenge.query.filter_by(id=_id).first()
            if challenge.category == Category.query.filter_by(name='special').first():
                return ResultErrorSchema(
                    message='Special challenge is not deliverable',
                    errors=['special challenge is not deliverable']
                ).jsonify()
            if challenge.publication:
                if challenge.publication > datetime.now():
                    return ResultErrorSchema(
                        message='Challenge is not published yet!',
                        errors=['challenge is not published yet!']
                    )
            if not challenge:
                return ResultErrorSchema(
                    message='Challenge does not exist!',
                    errors=['challenge does not exist']
                ).jsonify()
            data = challenge.jsonify()
            challenge_solves = Solve.query.filter_by(challenge=challenge).first()
            if challenge_solves:
                data['solved'] = True
            return ResultSchema(
                data=data
            ).jsonify()

    """
    Create a new challenge
    curl -H "Access-Token: $token" -X POST localhost:5000/api/challenge -H "Content-Type: application/json" \
    -d '{"name": "Test", "description": "TestChallenge", "flag": "TMT{t3$T}", "category": "hc"}'
    """
    @require_token
    @require_admin
    def post(self, **_):
        data = request.get_json() or {}
        schema = DaoCreateChallengeSchema()
        # use the schema to validate the submitted data
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        # check if the flag for the challenge in already in use
        for challenge in Challenge.query.all():
            if data.get('flag') == challenge.flag:
                return ResultErrorSchema(
                    message='Flag already in use!',
                    errors=['flag already in use'],
                    status_code=400
                ).jsonify()
        data['category'] = Category.query.filter_by(name=data.get('category')).first()

        # if a publication date is in the data check if its parseable
        # todo create a field (mini calender) in the frontend and check the validation (iso 8601)
        if data.get('publication'):
            # todo create field and do this in schema
            try:
                data['publication'] = dateutil.parser.parse(data['publication'])
            except ValueError as e:
                return ResultErrorSchema(
                    message='Invalid date for publication!',
                    errors=['invalid date for publication'],
                    status_code=400
                ).jsonify()

        # create the challenge
        challenge = Challenge(
            name=data.get('name'),
            description=data.get('description'),
            flag=data.get('flag'),
            points=data.get('points'),
            category=data.get('category'),
            yt_challenge_id=data.get('ytChallengeId') or None,
            yt_solution_id=data.get('ytSolutionId') or None,
            publication=data.get('publication') or datetime.now()
        )

        # add the challenge object to the database
        db.session.add(challenge)
        # commit db changes (challenge)
        db.session.commit()
        return ResultSchema(
            data=challenge.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/challenge/test -H "Content-Type: application/json" \
    -d '{"description": "a"}'
    """
    @require_token
    @require_admin
    def put(self, _id, **_):
        data = request.get_json() or {}
        schema = DaoUpdateChallengeSchema()
        # use the schema to validate the submitted data
        data, error = schema.load(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        # get the challenge object by the submitted name
        challenge = Challenge.query.filter_by(id=_id).first()
        if not challenge:
            return ResultErrorSchema(
                message='Challenge does not exist!',
                errors=['Challenge does not exist'],
                status_code=404
            ).jsonify()
        for key, val in data.items():
            # set the submitted values for the submitted key's
            setattr(challenge, key, val)
        # save the changes
        db.session.commit()
        return ResultSchema(
            data=challenge.jsonify()
        ).jsonify()
