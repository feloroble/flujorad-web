from datetime import datetime
from app.extensions import db
from .user import User

class Publicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con el usuario
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    usuario = db.relationship('User', backref='publicaciones')

    # Relación con los bloques de contenido
    contenidos = db.relationship(
        'PublicacionContenido',
        backref='publicacion',
        cascade='all, delete-orphan',
        order_by='PublicacionContenido.orden'
    )

class PublicacionContenido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicacion.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'texto' o 'imagen'
    contenido = db.Column(db.Text)  # si es texto
    ruta_imagen = db.Column(db.String(255))  # si es imagen
    orden = db.Column(db.Integer, nullable=False)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicacion.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Nuevo
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    publicacion = db.relationship('Publicacion', backref='comentarios')
    user = db.relationship('User', backref='comentarios')  # Nuevo