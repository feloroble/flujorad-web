from peewee import MySQLDatabase
from config import config

# Configuración de la DB usando variables de .env
db = MySQLDatabase(
    config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    charset=config.DB_CHARSET
)