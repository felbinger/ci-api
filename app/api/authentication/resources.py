from flask.views import MethodView
from flask import request
from datetime import datetime

from .utils import require_token
from .schemas import AuthSchema, AuthResultSchema
from ..schemas import ResultSchema
from ..user.models import User
from .models import Token
from app.db import db


class AuthResource(MethodView):
    """
    Get information about your user account (identified by Access-Token in the headers)
    curl -H "Access-Token: $token" -X GET localhost:5000/api/auth
    """
    @require_token
    def get(self, user, **_):
        return ResultSchema(
            data=user.jsonify()
        ).jsonify()

    """
    Login using username and password
    curl -X POST localhost:5000/api/auth -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "testtest"}'
    """
    def post(self):
        data = request.get_json() or {}
        schema = AuthSchema()
        # use the schema to validate the submitted data
        error = schema.validate(data)
        if error:
            return AuthResultSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        # Get the user object by the submitted username
        user = User.query.filter_by(username=data.get('username')).first()
        # Check if the user exists and if the submitted password is correct
        if not user or not user.verify_password(data.get('password')):
            return AuthResultSchema(
                message='Wrong credentials',
                errors=['Wrong credentials'],
                status_code=401
            ).jsonify()
        # create a new token for the user
        token = Token(user=user)
        # set the last_login attribute in the user object to the current time
        user.last_login = datetime.utcnow()
        # add the new token object to the database
        db.session.add(token)
        db.session.commit()
        return AuthResultSchema(
            message='Authentication was successfully',
            token=token.token
        ).jsonify()

    """
    Logout (destroy session by setting the attribute broken to 1)
    curl -v -H "Access-Token: $token" -X DELETE localhost:5000/api/auth
    """
    @require_token
    def delete(self, token, **_):
        token.broken = 1
        db.session.commit()
        return '', 204
