import os
from flask import Flask

from .api import UserResource, AuthResource, RoleResource, ChallengeResource, SolveResource
from .config import ProductionConfig, DevelopmentConfig
from .db import db


def create_app(testing_config=None):
    # create flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # check which config should be used, can be defined in the environment variable FLASK_ENV
    env = os.environ.get('FLASK_ENV')
    # load config
    if testing_config is None:
        if env == 'development':
            app.config.from_object(DevelopmentConfig)
        else:
            app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(testing_config)

    db.init_app(app)
    register_models()
    with app.app_context():
        # create all tables in the database
        db.create_all()
    register_views(app)
    register_resource(app, UserResource, 'user_api', '/api/users', pk='uuid', pk_type='string')
    register_resource(app, AuthResource, 'auth_api', '/api/auth', pk=None, get=False, put=False)
    register_resource(app, RoleResource, 'role_api', '/api/roles', pk='name', pk_type='string')
    register_resource(app, ChallengeResource, 'challenge_api', '/api/challenge', pk='name', pk_type='string',
                      delete=False)
    register_resource(app, SolveResource, 'solve_api', '/api/solve', pk='name', pk_type='string',
                      get=False, post=False, delete=False)

    return app


def register_models():
    # noinspection PyUnresolvedReferences
    from .api import User, Token, Role, Challenge, Solve


def register_resource(app, resource, endpoint, url, pk='_id', pk_type='int',
                      get=True, get_all=True, post=True, put=True, delete=True):
    view_func = resource.as_view(endpoint)
    if get_all:
        app.add_url_rule(url, defaults={pk: None} if get else None, view_func=view_func, methods=['GET'])
    if post:
        app.add_url_rule(url, view_func=view_func, methods=['POST'])
    if get:
        app.add_url_rule(f'{url}/<{pk_type}:{pk}>', view_func=view_func, methods=['GET'])
    if put:
        app.add_url_rule(f'{url}/<{pk_type}:{pk}>', view_func=view_func, methods=['PUT'])
    if delete:
        app.add_url_rule(f'{url}/<{pk_type}:{pk}>' if pk else url, view_func=view_func, methods=['DELETE'])


def register_views(app):
    # 404 error page
    @app.errorhandler(404)
    def not_found(e):
        return 'File not found!', 404

    # 403 error page
    @app.errorhandler(403)
    def not_found(e):
        return 'Permissions Denied!', 403
