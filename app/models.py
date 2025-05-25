from peewee import Model, CharField, BooleanField
from . import db   # db se inicializa en __init__.py

class Usuario(Model):
    nombre = CharField(max_length=50)
    email = CharField(unique=True)
    activo = BooleanField(default=True)

    class Meta:
        database = db 