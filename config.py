# coding:utf8
import os
from os.path import dirname
from yaml import load as load_yml
basedir = os.path.abspath(os.path.dirname(__file__)) # 取出项目所在目录


class YmlEnv:
    def __init__(self, path):
        self.path = path

    def load_to_env(self):
        if os.path.exists(self.path):
            with open(self.path) as config_file:
                ret = load_yml(config_file)
                os.environ['FLASK_ENV'] = ret.get('FLASK_ENV') or 'development'
            return ret
        else:
            raise RuntimeError('Please complete your .env.yml')


dir_name = dirname(__file__)
env_config = YmlEnv(dir_name + '/env/.env.yml').load_to_env()

class Config:
    SECRET_KEY = env_config.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = env_config.get('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = env_config.get('MAIL_USERNAME')
    MAIL_PASSWORD = env_config.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = env_config.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME=0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = env_config.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """测试环境, 使用SQLite"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = env_config.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = env_config.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    # @classmethod
    # def init_app(cls, app):
    #     Config.init_app(app)
    #
    #     # email errors to the administrators
    #     import logging
    #     from logging.handlers import SMTPHandler
    #     credentials = None
    #     secure = None
    #     if getattr(cls, 'MAIL_USERNAME', None) is not None:
    #         credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
    #         if getattr(cls, 'MAIL_USE_TLS', None):
    #             secure = ()
    #     mail_handler = SMTPHandler(
    #         mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
    #         fromaddr=cls.FLASKY_MAIL_SENDER,
    #         toaddrs=[cls.FLASKY_ADMIN],
    #         subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
    #         credentials=credentials,
    #         secure=secure)
    #     mail_handler.setLevel(logging.ERROR)
    #     app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
