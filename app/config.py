import os


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'jnw639kO3{28W1cvtDl]tjdrzkkd3YJCB(2IPK1deBKe*v!I6e0NB1$n3admTreE79Q%MxOuVtVFbuAsb69Mb2gPPpCQ?GAFcUMoH'
    TOKEN_VALIDITY = 180
    username = os.getenv('MYSQL_USERNAME')
    password = os.getenv('MYSQL_PASSWORD')
    hostname = os.getenv('MYSQL_HOSTNAME')
    port = os.getenv('MYSQL_PORT')
    database = os.getenv('MYSQL_DATABASE')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8mb4'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:9999/hc?charset=utf8mb4'
    DB_CHARSET = 'utf8'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:9999/hc?charset=utf8mb4'
    DB_CHARSET = 'utf8'


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
