from datetime import timedelta


class Config:
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/ngsapps'
    MAIL_SERVER = 'mail.evoting.portalsgh.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'password@evoting.portalsgh.com'
    MAIL_PASSWORD = 'apana1jude1'
    MAIL_DEFAULT_SENDER = 'Evoting.portalghs@portalghs.com'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=5)
    PAGINATE_PAGE_SIZE = 10
    PAGINATE_RESOURCE_LINKS_ENABLED = True
    JWT_AUTH_URL_RULE = '/api/auth'
    JWT_SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba'
    SERVER_NAME = '127.0.0.1:5000'


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass
