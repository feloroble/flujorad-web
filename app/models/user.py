from peewee import CharField, BooleanField
from .base import BaseModel  # Usa BaseModel explícitamente

class Usuario(BaseModel):
    nombre = CharField(max_length=50)
    email = CharField(unique=True)
    activo = BooleanField(default=True)