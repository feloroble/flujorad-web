class Config:
    SQLALCHEMY_DATABASE_URI = "mysql://flujorad:frroble91@localhost:3306/flujoradb?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
