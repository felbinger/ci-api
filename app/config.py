import os


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'jnw639kO3{28W1cvtDl]tjdrzkkd3YJCB(2IPK1deBKe*v!I6e0NB1$n3admTreE79Q%MxOuVtVFbuAsb69Mb2gPPpCQ?GAFcUMoH'
    TOKEN_VALIDITY = 48  # hours
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    ENABLE_MAIL = False


class ProductionConfig(Config):
    username = os.environ.get('MYSQL_USERNAME')
    password = os.environ.get('MYSQL_PASSWORD')
    hostname = os.environ.get('MYSQL_HOSTNAME')
    port = os.environ.get('MYSQL_PORT')
    database = os.environ.get('MYSQL_DATABASE')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8mb4'

    ENABLE_MAIL = True

    MAIL_SUBJECT = "Willkommen, junger h4x0r-Padawan"
    MAIL_MESSAGE = """
HAI 1.2
CAN HAS STDIO?
VISIBLE `
May the sudo be with you.
Click on this link to confirm you are a bot: https://www.youtube.com/user/TheMorpheus407
If you != bot:
click here: https://challenges.the-morpheus.de
try: systemd of a pwn
except: Panic! at the Kernel
finally: rage against the virtual machine`
KTHXBYE
"""

    SMTP_HOSTNAME = os.environ.get('SMTP_HOSTNAME')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@localhost:9999/hc?charset=utf8mb4'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
