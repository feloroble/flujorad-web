import os
from flask import Flask

from .extensions import db ,migrate , bcrypt, login_manager,csrf
from .models import register_models  # carga dinámica
from .routes import register_routes

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuración
    app.config.from_object('app.config.DevelopmentConfig')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)  # <- IMPORTANTE
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
   
   # Cargar modelo User para LoginManager
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    login_manager.login_view = 'auth.login'

   
    # Registrar modelos automáticamente
    with app.app_context():
        register_models()
        db.create_all() # Crea las tablas en la base de datos
        
    # Registrar rutas
    register_routes(app)

    from flask import render_template

    @app.errorhandler(404)
    def pagina_no_encontrada(error):
      return render_template('error.html'), 404

    return app
