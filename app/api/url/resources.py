from flask.views import MethodView
from flask import request

from app.db import db
from ..challenge import Challenge
from ..authentication import require_token, require_admin
from ..schemas import ResultSchema, ResultErrorSchema
from .models import Url
from .schemas import DaoCreateCategorySchema, DaoUpdateCategorySchema


class UrlResource(MethodView):
    """
    curl -H "Access-Token: $token" -X POST localhost:5000/api/urls -H "Content-Type: application/json" \
    -d '{"name": "test", "description": "Test"}'
    """
    @require_token
    @require_admin
    def post(self, **_):
        data = request.get_json() or {}
        schema = DaoCreateCategorySchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        for url in Url.query.all():
            if data.get('url') == url.url:
                return ResultErrorSchema(
                    message='Url already created!',
                    errors=['url already created'],
                    status_code=400
                ).jsonify()
        challenge = Challenge.query.filter_by(id=data.get('challenge')).first()
        if not challenge:
            return ResultErrorSchema(
                message="Challenge does not exist!",
                errors=["challenge does not exist"],
                status_code=404
            ).jsonify()
        url = Url(
            url=data.get('url'),
            description=data.get('description'),
            challenge=challenge
        )
        db.session.add(url)
        db.session.commit()
        return ResultSchema(
            data=url.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/urls/test -H "Content-Type: application/json" \
    -d '{"description": "Test2"}'
    """
    @require_token
    @require_admin
    def put(self, _id, **_):
        data = request.get_json() or {}
        schema = DaoUpdateCategorySchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        url = Url.query.filter_by(id=_id).first()
        if not url:
            return ResultErrorSchema(
                message='Url does not exist!',
                errors=['Url does not exist'],
                status_code=404
            ).jsonify()
        for key, val in data.items():
            setattr(url, key, val)
        db.session.commit()
        return ResultSchema(
            data=url.jsonify()
        ).jsonify()

    """
    curl -v -H "Access-Token: $token" -X DELETE localhost:5000/api/urls/test
    """
    @require_token
    @require_admin
    def delete(self, _id, **_):
        url = Url.query.filter_by(id=_id).first()
        if not url:
            return ResultErrorSchema(
                message='Url does not exist!',
                errors=['url does not exist'],
                status_code=404
            ).jsonify()
        db.session.delete(url)
        db.session.commit()
        return '', 204
