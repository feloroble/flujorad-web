import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """Configuración general de la aplicación Flask."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'ghchfhfty5675756372h1f2h161725672562715627ft2thjft1r27527152715628175268.,-,...,.m.m../*.-*m,-.*m')
    DB_NAME = os.getenv('DB_NAME', 'mi_bd_flask')
    DB_USER = os.getenv('DB_USER', 'usuario')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))  # MariaDB default: 3306
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Pool de conexiones para producción
    DB_MAX_CONNECTIONS = int(os.getenv('DB_MAX_CONNECTIONS', 20))

# Seleccionar configuración según entorno
env = os.getenv('FLASK_ENV', 'development')
config = DevelopmentConfig() if env == 'development' else ProductionConfig()