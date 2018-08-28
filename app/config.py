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

    ENABLE_MAIL = True

    SMTP_HOSTNAME = os.getenv('SMTP_HOSTNAME')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    # TODO add something
    MAIL_SUBJECT = "Subject"
    MAIL_MESSAGE = "Message"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:9999/hc?charset=utf8mb4'
    DB_CHARSET = 'utf8'


class DevelopmentConfig(Config):
    ENABLE_MAIL = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:9999/hc?charset=utf8mb4'
    DB_CHARSET = 'utf8'


class TestingConfig(Config):
    ENABLE_MAIL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
