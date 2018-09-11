from flask.views import MethodView
from flask import request

from app.db import db
from ..schemas import ResultSchema, ResultErrorSchema
from ..challenge import Challenge
from ..authentication import require_token, require_admin
from .models import Category
from .schemas import DaoCreateCategorySchema, DaoUpdateCategorySchema


class CategoryResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/categories
    """
    @require_token
    def get(self, name, **_):
        if name is None:
            # get all categories
            return ResultSchema(
                data=[d.jsonify() for d in Category.query.all()]
            ).jsonify()
        else:
            # get a category by the name in the resource (url)
            data = Category.query.filter_by(name=name).first()
            if not data:
                return ResultErrorSchema(
                    message='Category does not exist!',
                    errors=['category does not exist'],
                    status_code=404
                ).jsonify()
            return ResultSchema(
                data=data.jsonify() or None
            ).jsonify()

    """
    curl -H "Access-Token: $token" -X POST localhost:5000/api/categories -H "Content-Type: application/json" \
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
        for category in Category.query.all():
            if data.get('name') == category.name:
                return ResultErrorSchema(
                    message='Name already in use!',
                    errors=['name already in use'],
                    status_code=400
                ).jsonify()
        category = Category(
            name=data.get('name'),
            description=data.get('description')
        )
        db.session.add(category)
        db.session.commit()
        return ResultSchema(
            data=category.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -H "Access-Token: $token" -X PUT localhost:5000/api/categories/test -H "Content-Type: application/json" \
    -d '{"description": "Test2"}'
    """
    @require_token
    @require_admin
    def put(self, name, **_):
        data = request.get_json() or {}
        schema = DaoUpdateCategorySchema()
        error = schema.validate(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        category = Category.query.filter_by(name=name).first()
        if not category:
            return ResultErrorSchema(
                message='Category does not exist!',
                errors=['category does not exist'],
                status_code=404
            ).jsonify()
        category.description = data.get('description')
        db.session.commit()
        return ResultSchema(
            data=category.jsonify()
        ).jsonify()

    """
    curl -v -H "Access-Token: $token" -X DELETE localhost:5000/api/categories/test
    """
    @require_token
    @require_admin
    def delete(self, name, **_):
        category = Category.query.filter_by(name=name).first()
        if not category:
            return ResultErrorSchema(
                message='Category does not exist!',
                errors=['category does not exist'],
                status_code=404
            ).jsonify()
        for challenge in Challenge.query.all():
            if challenge.category == category:
                return ResultErrorSchema(
                    message='Category is in use!',
                    errors=['category is in use'],
                    status_code=422
                ).jsonify()
        db.session.delete(category)
        db.session.commit()
        return '', 204
