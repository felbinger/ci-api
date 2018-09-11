from flask import request

from ..schemas import ResultErrorSchema
from .models import Token


def require_token(view_func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Access-Token')
        if not token:
            return ResultErrorSchema(
                message='Missing Access-Token',
                errors=['missing access token'],
                status_code=401
            ).jsonify()
        # get the token object by the submitted Access-Token in the header
        token_obj = Token.query.filter_by(token=token).first()
        if token_obj:
            if not token_obj.is_valid() or not token_obj.user:
                return ResultErrorSchema(
                    message='Invalid Access-Token',
                    errors=['invalid access token'],
                    status_code=401
                ).jsonify()
            return view_func(*args, **kwargs, user=token_obj.user, token=token_obj)
        else:
            return ResultErrorSchema(
                message='Invalid Access-Token',
                errors=['invalid access token'],
                status_code=401
            ).jsonify()
    return wrapper


def require_admin(view_func):
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        if not user:
            raise AttributeError('Missing user attribute, please use @require_token before!')
        # check if the user has the role admin
        if user.role.name != 'admin':
            return ResultErrorSchema(message='Access Denied!', errors=['access denied'], status_code=403).jsonify()
        return view_func(*args, **kwargs)
    return wrapper
