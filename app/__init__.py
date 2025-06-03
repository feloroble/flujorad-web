import os
from flask import Flask

from .extensions import db ,migrate
from .models import register_models  # carga dinámica
from .routes import register_routes

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuración
    app.config.from_object('app.config.DevelopmentConfig')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)  # <- IMPORTANTE

    # Registrar modelos automáticamente
    with app.app_context():
        register_models()
        db.create_all() # Crea las tablas en la base de datos

    # Registrar rutas
    register_routes(app)

    return app
