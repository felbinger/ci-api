import os
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS

from .api import AuthResource, UserResource, RoleResource, ChallengeResource, SolveResource, CategoryResource, \
    UrlResource, MessageResource, RatingResource, LeaderboardResource
from .config import ProductionConfig, DevelopmentConfig
from .db import db
from .views import general, challenges, admin, leaderboard


def create_app(testing_config=None):
    # create flask app
    app = Flask(__name__)
    # enable cross origin resources sharing
    CORS(app)
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
    register_resource(app, AuthResource, 'auth_api', '/api/auth', pk=None, get=False, put=False)
    register_resource(app, RoleResource, 'role_api', '/api/roles', pk='name', pk_type='string')
    register_resource(app, UserResource, 'user_api', '/api/users', pk='uuid', pk_type='string')
    register_resource(app, CategoryResource, 'category_api', '/api/categories', pk='name', pk_type='string')
    register_resource(app, UrlResource, 'url_api', '/api/urls', get_all=False, get=False)
    register_resource(app, ChallengeResource, 'challenge_api', '/api/challenges', delete=False)
    register_resource(app, SolveResource, 'solve_api', '/api/solve', get=False, delete=False)
    register_resource(app, MessageResource, 'message_api', '/api/messages')
    register_resource(app, RatingResource, 'rating_api', '/api/rate',
                      get=False, get_all=False, post=False, delete=False)
    register_resource(app, LeaderboardResource, 'leaderboard_api', '/api/leaderboard', pk="name", pk_type="string",
                      post=False, put=False, delete=False)

    return app


def register_models():
    # noinspection PyUnresolvedReferences
    from .api import User, Token, Role, Challenge, Solve, Url, Category, Message, Rating


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
    # register blueprints
    app.register_blueprint(general)
    app.register_blueprint(challenges, url_prefix='/challenges')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(leaderboard, url_prefix='/')

    # 404 error page
    @app.errorhandler(404)
    def not_found(e):
        return 'File not found!', 404

    # 403 error page
    @app.errorhandler(403)
    def permission_denied(e):
        return 'Permissions Denied!', 403

    # Special Challenge 0x03 (suppose to be found with gobuster/dirbuster/dirb)
    @app.route('/cursor-snarfing/')
    def special_0x03():
        return """Submit <a href="img.jpg">me</a> in the well known format: TMT{flag}"""

    @app.route('/cursor-snarfing/img.jpg')
    def special_0x03_img():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static/dist/img/'),
            filename='special_0x03.png',
            mimetype='image/png'
        )

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static'),
            filename='favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static'),
            filename='robots.txt',
            mimetype='text/plain'
        )

    @app.route('/static/vendor/images/sort_both.png')
    def sort_both():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static/vendor/datatables/images/'),
            filename='sort_both.png',
            mimetype='image/png'
        )

    @app.route('/static/vendor/images/sort_asc.png')
    def sort_asc():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static/vendor/datatables/images/'),
            filename='sort_asc.png',
            mimetype='image/png'
        )

    @app.route('/static/vendor/images/sort_desc.png')
    def sort_desc():
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static/vendor/datatables/images/'),
            filename='sort_desc.png',
            mimetype='image/png'
        )

    # Download a file inside the downloads directory. This feature is for new challenges - reversing for example
    @app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
    def download(filename):
        return send_from_directory(
            directory=os.path.join(app.root_path, 'static/downloads'),
            filename=filename
        )
