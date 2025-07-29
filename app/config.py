import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'fdkgfsdkgsd454654646747//*'
    SQLALCHEMY_DATABASE_URI = "mysql://flujorad:frroble91@localhost:3306/flujoradb?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENABLE_BLOG = True
    ENABLE_FLUJO_RAC = False
    APP_NAME = "Tecno Táctil"
    APP_VERSION = "1.0.0"

class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_FLUJO_RAC = True
    

class ProductionConfig(Config):
    DEBUG = False
    ENABLE_FLUJO_RAC = False
    AC = False

class TestingConfig(Config):
    TESTING = True
    FLASK_ENV = 'testing'