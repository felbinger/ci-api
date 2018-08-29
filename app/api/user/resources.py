from flask.views import MethodView
from flask import request, current_app
from hashlib import sha512

from app.db import db
from app.utils import SMTPMail
from ..schemas import ResultSchema, ResultErrorSchema
from ..authentication import require_token, require_admin
from ..role import Role
from .models import User
from ..authentication import Token
from .schemas import DaoCreateUserSchema, DaoUpdateUserSchema, DaoRegisterUserSchema


class UserResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/users
    """
    @require_token
    @require_admin
    def get(self, uuid, **_):
        if uuid is None:
            return ResultSchema(
                data=[d.jsonify() for d in User.query.all()]
            ).jsonify()
        else:
            data = User.query.filter_by(public_id=uuid).first()
            if not data:
                return ResultErrorSchema(
                    message='User does not exist!',
                    errors=['user does not exist'],
                    status_code=404
                ).jsonify()
            return ResultSchema(
                data=data.jsonify()
            ).jsonify()

    """
    curl -X POST localhost:5000/api/users -H "Content-Type: application/json" \
    -d '{"username": "janedoe", "password": "JaneDoe2", "email": "jane@doe.de"}'
    
    curl -X POST localhost:5000/api/users -H "Access-Token: $token" -H "Content-Type: application/json" \
    -d '{"username": "johndoe", "password": "JohnDoe2", "email": "john@doe.de", "role": "admin"}'
    """
    def post(self, **_):
        token = request.headers.get('Access-Token')
        if token:
            token_obj = Token.query.filter_by(token=token).first()
            if token_obj:
                if not token_obj.is_valid() or not token_obj.user:
                    return ResultErrorSchema(
                        message='Invalid Access-Token',
                        errors=['invalid access token'],
                        status_code=401
                    ).jsonify()
                else:
                    return self._create_user_as_admin()
        else:
            return self._register_user()

    """
    curl -X PUT localhost:5000/api/users/89789fc7-4655-413d-8339-6fabedb1eab0 -H "Access-Token: $token" \
    -H "Content-Type: application/json" -d '{"email": "neue@mail.de"}'
    """
    @require_token
    def put(self, uuid, user, **_):
        if uuid == 'me':
            return self._update_user(user)
        else:
            target = User.query.filter_by(public_id=uuid).first()
            if not target:
                return ResultErrorSchema(
                    message='User does not exists',
                    errors=['user does not exists'],
                    status_code=404
                ).jsonify()
            return require_admin(self._update_user_as_admin)(user=user, target=target)

    """
    curl -X DELETE localhost:5000/api/users/2a1c8ba8-f12e-4d2a-97c3-2fe454fefc6e -H "Access-Token: $token"
    """
    @require_token
    @require_admin
    def delete(self, uuid, **_):
        user = User.query.filter_by(public_id=uuid).first()
        db.session.delete(user)
        db.session.commit()
        return '', 204

    def _update_user(self, user):
        schema = DaoUpdateUserSchema()
        data = request.get_json()
        data, error = schema.load(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        if 'role' in data.keys():
            return ResultErrorSchema(
                message='You are not allowed to change your role',
                errors='not allowed to change role',
                status_code=403
            ).jsonify()
        for key, val in data.items():
            if key == 'password':
                setattr(user, key, sha512(val.encode()).hexdigest())
            else:
                setattr(user, key, val)
        db.session.commit()
        return ResultSchema(data=user.jsonify()).jsonify()

    def _update_user_as_admin(self, target, **_):
        schema = DaoUpdateUserSchema()
        data = request.get_json()
        data, error = schema.load(data)
        if error:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=error,
                status_code=400
            ).jsonify()
        for key, val in data.items():
            if key == 'role':
                role = Role.query.filter_by(name=val).first()
                if not role:
                    return ResultErrorSchema(
                        message='Invalid Role',
                        errors=['invalid role'],
                        status_code=400
                    ).jsonify()
                else:
                    target.role = role
            elif key == 'password':
                setattr(target, key, sha512(val.encode()).hexdigest())
            else:
                setattr(target, key, val)
        db.session.commit()
        return ResultSchema(data=target.jsonify()).jsonify()

    def _register_user(self, **_):
        data = request.get_json() or {}
        schema = DaoRegisterUserSchema()
        result = schema.load(data)
        if result.errors:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=result.errors,
                status_code=400
            ).jsonify()
        data = result.data
        user_exists = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
        if user_exists:
            return ResultErrorSchema(
                message='Username or email already in use!',
                errors=['username or email already in use'],
                status_code=422
            ).jsonify()

        data['role'] = Role.query.filter_by(name="user").first()
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        if current_app.config['ENABLE_MAIL']:
            smtp = SMTPMail(
                current_app.config['SMTP_HOSTNAME'],
                current_app.config['SMTP_PORT'],
                current_app.config['SMTP_USERNAME'],
                current_app.config['SMTP_PASSWORD']
            )
            smtp.sendmail(
                current_app.config['MAIL_SUBJECT'],
                current_app.config['MAIL_MESSAGE']
                [user.email]
            )
            smtp.exit()

        return ResultSchema(
            data=user.jsonify(),
            status_code=201
        ).jsonify()

    def _create_user_as_admin(self, **_):
        data = request.get_json() or {}
        schema = DaoCreateUserSchema()
        result = schema.load(data)
        if result.errors:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=result.errors,
                status_code=400
            ).jsonify()
        data = result.data
        user_exists = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
        if user_exists:
            return ResultErrorSchema(
                message='Username or email already in use!',
                errors=['username or email already in use'],
                status_code=422
            ).jsonify()
        data['role'] = Role.query.filter_by(name=data.get('role')).first()
        if not data['role']:
            return ResultErrorSchema(
                message='Role does not exist!',
                errors=['role does not exist'],
                status_code=404
            ).jsonify()

        user = User(**data)
        db.session.add(user)
        db.session.commit()

        return ResultSchema(
            data=user.jsonify(),
            status_code=201
        ).jsonify()
