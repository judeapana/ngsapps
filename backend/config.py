from datetime import timedelta


class Config:
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/ngsapps'
    MAIL_SERVER = 'mail.hrm.portalsgh.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '_mainaccount@hrm.portalsgh.com'
    MAIL_PASSWORD = 'apana1jude1'
    MAIL_DEFAULT_SENDER = 'noreply.portalghs@portalghs.com'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=5)
    PAGINATE_PAGE_SIZE = 10
    PAGINATE_RESOURCE_LINKS_ENABLED = True
    JWT_SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba'


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass
